import numpy as np
import yfinance as yf
import datetime as dt


class PriceRanges:
    def __init__(self, ticker: str, year: str) -> None:
        self.ticker = ticker
        self.year = year
    '''-------------------------------'''
    def get_all_quarters(self) -> dict:

        q1_data = self.get_quarter_data(start_month=1, start_day=1, end_month=3, end_day=31)
        q2_data = self.get_quarter_data(start_month=4, start_day=1, end_month=6, end_day=30)
        q3_data = self.get_quarter_data(start_month=7, start_day=1, end_month=9, end_day=30)
        q4_data = self.get_quarter_data(start_month=10, start_day=1, end_month=12, end_day=31)

        quarterly_data = {"Q1": q1_data,
                          "Q2": q2_data,
                          "Q3": q3_data,
                          "Q4": q4_data}
        
        return quarterly_data




    '''-------------------------------'''
    def get_quarter_data(self, start_month:int =1, start_day: int =1, end_month: int = 3, end_day: int = 31) -> dict:
        
        quarter_data = {}

        # Create start and end dates for the first quarter of the year
        start_date = dt.datetime(self.year, start_month, start_day)
        end_date = dt.datetime(self.year, end_month, end_day)

        # Fetch the stock data for the specified ticker symbol and date range
        stock_data = yf.download(self.ticker, start=start_date, end=end_date)

        # Extract the 'High' and 'Low' columns from the stock data
        quarter_data["High"] = round(stock_data["High"].max(), 2)
        quarter_data["Low"] = round(stock_data["Low"].min(), 2)
        try:
            quarter_data["Average"] = round(stock_data["Adj Close"].mean(), 2)
        except ValueError:
            quarter_data["Average"] = "N\A"
        return quarter_data
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    def get_price_range_in_year(self) -> dict:
        data = {}

        # Create variable for first date in year, and last date in year.
        start_date = f"{self.year}-01-01"
        end_date = f"{self.year}-12-31"

        # Get the stock data within the specified year.
        stock_data = yf.download(self.ticker, start=start_date, end=end_date)

        # Extract the high, low, and adjusted close prices from the year. 
        # For the adjusted closes, we will take the average.
        data["High"] = round(stock_data["High"].max(), 2)
        data["Low"] = round(stock_data["Low"].min(), 2)
        data["Average"] = round(stock_data["Adj Close"].mean(), 2)

        return data
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
