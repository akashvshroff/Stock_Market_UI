import requests
import pandas as pd
from datetime import date, timedelta, datetime
import sqlite3
from file_paths import *


class GetData:
    def __init__(self, num_days, n, k):
        """
        Initialise all the data structures used in the program.
        """
        self.num_days = num_days  # number of previous days to run for
        self.n = n  # number of days for primary average
        self.k = k  # number of days for secondary average
        self.stocks_dict = {}  # stock name -> daily value list
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

    def initialise_db(self):
        """
        Connect to the database and create the table.
        """
        self.conn = sqlite3.connect(stocks_db)
        self.cur = self.conn.cursor()

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
        response = requests.get(url)
        if response.status_code == 200:
            return True
        return False

    def pd_parse_data(self, date_obj):
        """
        Uses pandas to read the csv file from the web.
        """
        url = self.get_url(date_obj)
        stocks_df = pd.read_csv(url, sep=r'\s*,\s*', engine='python')
        print(stocks_df)

    def get_data(self):
        """
        Driver function to fetch data and store it in the stocks_dict.
        """
        for day in range(self.num_days):
            # since yesterday's data is available
            cur_date = date.today() - timedelta(days=1 + day)
            if cur_date.weekday() in [5, 6] or not self.get_valid(cur_date):
                continue
            else:
                counter = 0
                while counter < self.n:  # n data points are collected
                    self.pd_parse_data(cur_date)
                    counter += 1


if __name__ == '__main__':
    obj = GetData(1, 1, 1)
