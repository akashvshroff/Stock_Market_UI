import requests
import pandas as pd
from datetime import date, timedelta, datetime
import sqlite3
from file_paths import *
from pprint import pprint


class GetData:
    def __init__(self, num_days, n, k):
        """
        Initialise all the data structures used in the program.
        """
        self.num_days = num_days  # number of previous days to run for
        self.n = n  # number of days for primary average
        self.k = k  # number of days for secondary average
        self.stocks_dict = {}  # stock name -> daily value list
        self.dates_used = []  # dates for which data has been used
        self.get_stock_names()
        self.initialise_db()
        self.get_data()

    def get_stock_names(self):
        """
        Retrieve all the stock names from the share_list csv file.
        """
        names_df = pd.read_csv(share_list)
        names = names_df['NAMES'].values.tolist()
        self.stocks_dict = {name: [] for name in names}

    def convert_name(self, name):
        """
        Converts a string to an acceptable field name for sqlite.
        """
        if name[0].isdigit():
            name = '_' + name
        name = ''.join([letter if letter.isalnum() or letter ==
                        '_' else '_' for letter in name])
        return name

    def initialise_db(self):
        """
        Connect to the database and create the table.
        """
        self.conn = sqlite3.connect(stocks_db)
        self.cur = self.conn.cursor()
        for name in self.stocks_dict.keys():
            table_name = self.convert_name(name)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (date TEXT UNIQUE, avgn REAL, avgk REAL, error_message INT)"
            self.cur.execute(query)

    def get_url(self, date_obj):
        """
        Returns the url that is to be scraped.
        """
        year = date_obj.strftime("%Y")
        month = date_obj.strftime("%b").upper()
        day = date_obj.strftime("%d")
        full_date = f'{day}{month}{year}'
        url = f'{base_url}/{year}/{month}/cm{full_date}bhav.csv.zip'
        return url

    def get_valid(self, date_obj):
        """
        Checks if a url is valid, i.e doesn't return an error and returns bool
        """
        url = self.get_url(date_obj)
        response = requests.get(url, stream=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
        })
        if response.status_code == 200:
            return True
        return False

    def pd_parse_data(self, date_obj):
        """
        Uses pandas to read the csv file from the web.
        """
        url = self.get_url(date_obj)
        stocks_df = pd.read_csv(url, sep=r'\s*,\s*', engine='python')
        stocks_df = stocks_df[stocks_df['SERIES'] == 'EQ']
        stocks_df = stocks_df[['SYMBOL', p1, p2]]
        for name in self.stocks_dict.keys():  # get data for the stocks
            df = stocks_df[stocks_df['SYMBOL'] == name]
            if not df.empty:
                v1 = df[p1].values[0]
                v2 = df[p2].values[0]
                self.stocks_dict[name].append(v1 * v2)
        # pprint(self.stocks_dict)

    def get_data(self):
        """
        Driver function to fetch data and store it in the stocks_dict.
        """
        first = True
        cur_date = date.today()
        day = 0
        while day < self.num_days:
            # since yesterday's data is available
            cur_date = cur_date - timedelta(days=1)
            if cur_date.weekday() in [5, 6] or not self.get_valid(cur_date):
                continue
            else:
                day += 1
                if first:  # after first time only 1 data point is collected
                    first = False
                    counter = 0
                    while counter < self.n:  # n data points are collected
                        if not cur_date.weekday() in [5, 6]:
                            if self.get_valid(cur_date):
                                self.dates_used.append(cur_date)
                                self.pd_parse_data(cur_date)
                                counter += 1
                        cur_date = cur_date - timedelta(days=1)
                else:
                    self.dates_used.append(cur_date)
                    self.pd_parse_data(cur_date)
        # pprint(self.stocks_dict)
        # pprint(self.dates_used)
        self.store_database()

    def store_database(self):
        """
        Store all the data collected in the database.
        """
        pass


if __name__ == '__main__':
    obj = GetData(10, 10, 5)
