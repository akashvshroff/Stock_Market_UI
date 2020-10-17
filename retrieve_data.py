import requests
import pandas as pd
from datetime import date, timedelta, datetime
import sqlite3
from file_paths import *
from pprint import pprint
import time
import threading
import multiprocessing
import concurrent.futures


class GetData:
    def __init__(self, num_days, n, k):
        """
        Initialise all the data structures used in the program.
        """
        self.num_days = num_days  # number of previous days to run for
        self.n = n  # number of days for primary average
        self.k = k  # number of days for secondary average
        self.stocks_dict = {}  # stock name -> daily value list
        self.processed_data = []  # holds all the info for each stock as a tuple
        self.dates_used = []  # dates for which data has been used
        self.conn = sqlite3.connect(stocks_db)
        self.cur = self.conn.cursor()
        self.get_stock_names()

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

    def get_iso(self, date_obj):
        """
        Returns the epoch time for a date to store.
        """
        return date_obj.isoformat()

    def reset_db(self):
        """
        Drops all existing tables.
        """
        for stock in self.stocks_dict.keys():
            query = f'DROP TABLE IF EXISTS {self.convert_name(stock)}'
            self.cur.execute(query)

    def initialise_db(self):
        """
        Connect to the database and create the table.
        """
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS info (id INTEGER PRIMARY KEY UNIQUE, n INTEGER, k INTEGER)")
        self.cur.execute(
            "INSERT OR REPLACE INTO info(n,k,id) VALUES (?,?,?)", (self.n, self.k, 1,))
        for name in self.stocks_dict.keys():
            table_name = self.convert_name(name)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, date TEXT UNIQUE, avgn REAL, avgk REAL, ratio REAL, error_message INT)"
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

    def get_dates(self):
        """
        Function to get the valid dates to be used to fetch the data.
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

    def process_data(self, item):
        """
        Use a sliding window to calculate the moving average across all values.
        """
        stock, values = item
        num_points = len(values)
        avg_n, avg_k = [sum(values[0:self.n]) /
                        self.n], [sum(values[0:self.k]) / self.k]
        num_remove = 0
        dates = []
        k_add = self.k
        for num_add in range(self.n, num_points):
            avg_n.append(
                ((avg_n[-1]*self.n) - values[num_remove] +
                 values[num_add])/self.n
            )
            avg_k.append(
                ((avg_k[-1]*self.k) - values[num_remove] + values[k_add])/self.k
            )
            dates.append(self.dates_used[num_remove])
            num_remove += 1
            k_add += 1
        self.processed_data.append((stock, dates, avg_n, avg_k))

    def store_data(self):
        """
        Store data by calling upon store database function.
        """
        for stock, dates, avgn, avgk in self.processed_data:
            self.store_database(stock, dates, avgn, avgk)
        self.conn.commit()

    def store_database(self, stock, dates, avgn, avgk):
        """
        Store all the data collected in the database.
        """
        # print(f'{stock}')
        table = self.convert_name(stock)
        err = 0
        if len(avgn) != self.num_days + self.n - 2:
            err = 1
        items = list(zip(dates, avgn, avgk))[::-1]
        # print(items)
        for date, n, k in items:
            ratio = k / n
            iso_time = self.get_iso(date)
            query = f'INSERT OR REPLACE INTO {table}(date, avgn, avgk, ratio, error_message) VALUES (?,?,?,?,?)'
            # print(query)
            self.cur.execute(query, (iso_time, n, k, ratio, err,))


def main(num, n, k, reset):
    """
    Driver function for the program.
    """
    obj = GetData(num + 1, n, k)
    if reset:
        obj.reset_db()
    obj.initialise_db()
    obj.get_dates()
    workers = len(obj.stocks_dict)
    executor = concurrent.futures.ThreadPoolExecutor(workers)
    futures = [executor.submit(obj.process_data, item)
               for item in obj.stocks_dict.items()]
    concurrent.futures.wait(futures)
    obj.store_data()
    obj.conn.close()
    # pprint(obj.processed_data)


if __name__ == '__main__':
    num, n, k, reset = 10, 20, 5, False
    main(num, n, k, reset)
