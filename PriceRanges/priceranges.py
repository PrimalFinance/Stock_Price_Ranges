# Operating System imports
import os
from dotenv import load_dotenv
load_dotenv()

# Number management related imports
import numpy as np
import pandas as pd

# Date & time imports
import time
import datetime as dt

# Webscraping
import requests
from bs4 import BeautifulSoup


# Selenium imports 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Yahoo Finance imports
import yfinance as yf

chrome_driver = "D:\\ChromeDriver\\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


# Get the current working directory. 
cwd = os.getcwd()
# Path to csv file.
csv_file_path = cwd + "\\Filings\\quarterly_filings.csv"
# Path to "earnings.csv".
earnings_csv = cwd + "\\Earnings\\"







class FiscalScraper: 
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.key = os.getenv("alpha_vantage_key")
        self.earnings_csv = earnings_csv + f"{earnings_csv}.csv"

        # Root url to make queries. 
        self.root_url = "https://www.alphavantage.co/query"

        # Variables for financial statements.
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.earnings = pd.DataFrame()

        # List of possible function parameters for financial report frequency.
        self.quarterly_params = ["q", "Q", "Quarter", "quarter", "Quarterly", "quarterly"]
        self.annual_params = ["a", "A", "Annual", "annual"]

    '''-------------------------------'''
    def get_fiscal_year_end_date(self) -> str:
        '''
        This function will search the SEC EDGAR database, find the most recent 10-K, and return the period of report for that 10-k.  
        :return: str of the end date of the fiscal year. '''
        
        sec_annual_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-k&dateb=&owner=include&count=100&search_text="
        
        self.create_browser(sec_annual_url)


        # Loop vars 
        running = True
        filing_index = 2
        date_index = 2

        while running:

            filing_type_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[{filing_index}]/td[1]"
            print(f"Filing: {filing_type_xpath}")
            date_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[{date_index}]/td[4]"
            # Extract the data.
            filing_type = self.read_data(filing_type_xpath)
            filing_date = self.read_data(date_xpath)

            if filing_type == "10-K":
                print(f"Filing Type: {filing_type} {filing_date}")
                documents_button_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[{filing_index}]/td[2]/a[1]"
                self.click_button(documents_button_xpath, wait=True, wait_time=5)
                # NOTE: This xpath does not require an index to be incremented. 
                period_of_report_xpath = "/html/body/div[4]/div[1]/div[2]/div[2]/div[2]"
                period_of_report = self.read_data(period_of_report_xpath, wait=True, wait_time=5)
                return period_of_report
                


            filing_index += 1
            date_index += 1
                
        
    '''----------------------------------- Quarter Utilities -----------------------------------'''    
    '''-------------------------------'''
    def organize_quarters(self, quarters: list, fiscal_end: str):
        '''
        :param quarters: Unordered list of the most recent 4 quarters.
        :param fiscal_end: The date of the 4th quarter. 
        
        :return: list of organized quarters. 
        '''        
        # Format the date to only get the month and day. Ex: 2020-09-30 -> 09-30
        for i in range(len(quarters)):
            split_date = quarters[i].split("-")
            split_date = f"{split_date[1]}-{split_date[2]}"
            quarters[i] = split_date

        # Format the "fiscal_end" date to match the quarters. Ex: 2020-12-31 -> 12-31 
        fiscal_end = fiscal_end.split("-")
        fiscal_end = f"{fiscal_end[1]}-{fiscal_end[2]}"
        
        # Find the index of q4 in our list of quarters. 
        q4_index = 0
        for i in range(len(quarters)):
            # If the number of days between than date1 & date2 is less than "days_threshold", the if statement will return True and break the loop.
            if self.compare_dates(date1=quarters[i], date2=fiscal_end, days_threshold=10):
                break
            # If not, increase the q4_index. When the loop breaks the value of q4_index will be used at whatever increment it's current state is. 
            else:
                q4_index += 1
        

        # If q4 is at the first index. [*12-31*, 03-31, 06-30, 09-30]
        if q4_index == 0:
            print(f"TAG0: {quarters}")
            quarter_data = {
                "ticker": self.ticker,
                "Q1": quarters[1],
                "Q2": quarters[2],
                "Q3": quarters[3],
                "Q4": fiscal_end,
                "fiscal_end": fiscal_end
            }
        # If q4 is at the second index. [09-30, *12-31*, 03-31, 06-30]
        elif q4_index == 1:
            print(f"TAG1: {quarters}")
            quarter_data = {
                "ticker": self.ticker,
                "Q1": quarters[2],
                "Q2": quarters[3],
                "Q3": quarters[0],
                "Q4": quarters[q4_index],
                "fiscal_end": fiscal_end
            }
        # If q4 is at the third index. [06-30, 09-30, *12-31*, 03-31]
        elif q4_index == 2:
            print(f"TAG2: {quarters}")
            quarter_data = {
                "ticker": self.ticker,
                "Q1": quarters[3],
                "Q2": quarters[0],
                "Q3": quarters[1],
                "Q4": quarters[q4_index],
                "fiscal_end": fiscal_end
            }
        # If q4 is at the third index. [03-31, 06-30, 09-30, *12-31*]
        elif q4_index == 3:
            quarter_data = {
                "ticker": self.ticker,
                "Q1": quarters[0],
                "Q2": quarters[1],
                "Q3": quarters[2],
                "Q4": quarters[q4_index],
                "fiscal_end": fiscal_end
            }

        return quarter_data

    '''-------------------------------'''
    def get_quarters_price_data(self, quarters, year: int):
        '''
        :param quarters:
        :param year: The year to search for the data.
        :return: Dict, this dictionary will return the start date, end date, and the data.
        '''

        # Get the dates from the dictionary "quarters" passed in the function parameter. 
        q1_date = quarters["Q1"].values[0]
        q2_date = quarters["Q2"].values[0]
        q3_date = quarters["Q3"].values[0]
        q4_date = quarters["Q4"].values[0]

        # Logic to determine the start date for Q1. 
        if self.if_date_greater(target_date=q1_date, compare_date=q4_date): # Determine if Q1 is greater than Q4. If it is, then the company has an "offset" fiscal year. 
            # Get the start date for Q1, by calculating 1 day after the end of Q4.
            q1_start_date = f"{year-1}-{self.add_days_to_date(target_date=q4_date, days_to_add=1)}"
            q1_end_date = f"{year-1}-{q1_date}"
        # Company with a normal fiscal year. 
        else:
            q1_start_date = f"{year}-01-01"
            q1_end_date = f"{year}-{q1_date}"
        # Logic to determine the start date for Q2.
        if self.if_date_greater(target_date=q2_date, compare_date=q4_date): # Determine if Q2 is greater than Q4. 
            # Get the start date for Q2, by calculating 1 day after the end of Q1.
            q2_start_date = f"{year-1}-{self.add_days_to_date(target_date=q1_date, days_to_add=1)}"
            q2_end_date = f"{year-1}-{q2_date}"
        else:
            q2_start_date = f"{year}-{self.add_days_to_date(target_date=q1_date, days_to_add=1)}"
            q2_end_date = f"{year}-{q2_date}"
        # Logic to determine the start date for Q3 & Q4. 
        if self.if_date_greater(target_date=q3_date, compare_date=q4_date):
            # Get the start date for Q3, by calculating 1 day after the end of Q2. 
            q3_start_date = f"{year-1}-{self.add_days_to_date(target_date=q2_date, days_to_add=1)}"
            q3_end_date = f"{year-1}-{q3_date}"

            q4_start_date = f"{year-1}-{self.add_days_to_date(target_date=q3_date, days_to_add=1)}"
            q4_end_date = f"{year}-{q4_date}"
            

        else: 
            q3_start_date = f"{year}-{self.add_days_to_date(target_date=q2_date, days_to_add=1)}"
            q3_end_date = f"{year}-{q3_date}"

            # Q4 dates
            q4_start_date = f"{year}-{self.add_days_to_date(target_date=q3_date, days_to_add=1)}"
            q4_end_date = f"{year}-{q4_date}"

        # Get the data from each quarter. 
        q1_data = self.get_quarter_data(quarter_start=q1_start_date, quarter_end=q1_end_date)
        q2_data = self.get_quarter_data(quarter_start=q2_start_date, quarter_end=q2_end_date)
        q3_data = self.get_quarter_data(quarter_start=q3_start_date, quarter_end=q3_end_date)
        q4_data = self.get_quarter_data(quarter_start=q4_start_date, quarter_end=q4_end_date)

        # Store price data in dictionary.
        quarterly_data = {
            "Q1": {
                "start": q1_start_date,
                "end": q1_end_date,
                "data": q1_data
            },
            "Q2": {
                "start": q2_start_date,
                "end": q2_end_date,
                "data": q2_data
            },
            "Q3": {
                "start": q3_start_date,
                "end": q3_end_date,
                "data": q3_data
            },
            "Q4": {
                "start": q4_start_date,
                "end": q4_end_date,
                "data": q4_data
            }
        }

        return quarterly_data

    '''-------------------------------'''
    def get_quarter_data(self, quarter_start: str, quarter_end: str) -> dict:
        '''
        :param quarter_start: A string that is the date of the quarter_start (Start of the quarter). 
        :param quarter_end: A string that is the date of the quarter_end (End of the quarter). 
        :return: Dictionary holding the high, low, average of the prices within the timeframe of the quarter. 
        '''
        
        quarter_data = {}

        # Split the dates into independent variables. 
        start_year, start_month, start_day = quarter_start.split("-")
        end_year, end_month, end_day = quarter_end.split("-")

        # Turn all of the date elements into integers. 
        start_year, start_month, start_day = int(start_year), int(start_month), int(start_day)
        end_year, end_month, end_day = int(end_year), int(end_month), int(end_day)
        


        # Create start and end dates for the first quarter of the year
        start_date = dt.datetime(start_year, start_month, start_day)
        end_date = dt.datetime(end_year, end_month, end_day)

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





    '''----------------------------------- Annual Utilities -----------------------------------'''
    '''-------------------------------'''
    def get_annual_price_data(self, fiscal_start_end: dict, year: int):
        '''
        :param fiscal_start_end: Dictionary that contains the fiscal year start in the key "fiscal_start", and the fiscal year end in the key "fiscal_end". 
        :return: Dictionary holding the high, low, average of the prices within the timeframe of the annual fiscal year. 
        '''
        annual_data = {}
        finalized_data = {}
        
        # If the fiscal start is greater than the fiscal end (only in terms of months, and day. ) Ex: 11-31 > 1-31 or 6-30 < 7-31
        if self.if_date_greater(target_date=fiscal_start_end["fiscal_start"], compare_date=fiscal_start_end["fiscal_end"]):
            
            fiscal_start = f"{year-1}-{fiscal_start_end['fiscal_start']}"
            fiscal_end = f"{year}-{fiscal_start_end['fiscal_end']}"
            # Fetch the stock data. 
            stock_data = yf.download(self.ticker, start=fiscal_start, end=fiscal_end)

            # Extract the "High" and "Low" columns from the stock data.
            annual_data["High"] = round(stock_data["High"].max(), 2)
            annual_data["Low"] = round(stock_data["Low"].min(), 2)

            try:
                annual_data["Average"] = round(stock_data["Adj Close"].mean(), 2)
            except ValueError:
                annual_data["Average"] = "N\A"
        else:
            fiscal_start = f"{year}-{fiscal_start_end['fiscal_start']}"
            fiscal_end = f"{year}-{fiscal_start_end['fiscal_end']}"
            # Fetch the stock data. 
            stock_data = yf.download(self.ticker, start=fiscal_start, end=fiscal_end)

            # Extract the "High" and "Low" columns from the stock data.
            annual_data["High"] = round(stock_data["High"].max(), 2)
            annual_data["Low"] = round(stock_data["Low"].min(), 2)

            try:
                annual_data["Average"] = round(stock_data["Adj Close"].mean(), 2)
            except ValueError:
                annual_data["Average"] = "N\A"
        
        finalized_data = {
            "start": fiscal_start,
            "end": fiscal_end,
            "data": annual_data
        }


        return finalized_data
    '''-------------------------------'''
    '''----------------------------------- Browser Utilities -----------------------------------'''

    def create_browser(self, url=None):
        '''
        :param url: The website to visit.
        :return: None
        '''
        service = Service(executable_path=chrome_driver)
        self.browser = webdriver.Chrome(
            service=service, options=chrome_options)
        # Default browser route
        if url == None:
            self.browser.get(url=self.sec_quarterly_url)
        # External browser route
        else:
            self.browser.get(url=url)

    '''-----------------------------------'''
    def read_data(self, xpath: str, wait: bool = False, wait_time: int = 5) -> str:
        '''
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.  
        :return: (str) Text of the element. 
        '''

        if wait:
            data = WebDriverWait(self.browser, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        else:
            data = self.browser.find_element("xpath", xpath)
        # Return the text of the element found.
        return data.text
    '''-------------------------------'''
    def click_button(self, xpath: str, wait: bool = False, wait_time: int = 5) -> None:
        '''
        :param xpath: Path to the web element. 
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.  
        :return: None. Because this function clicks the button but does not return any information about the button or any related web elements. 
        '''


        if wait:
            element = WebDriverWait(self.browser, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        else:
            element = self.browser.find_element("xpath", xpath)
        element.click()

    '''-------------------------------'''
    def build_query(self, func: str) -> str:
        end_point = f"query?function={func}&symbol={self.ticker}&apikey={self.key}"
        query = self.root_url + end_point
        return query
    '''-------------------------------'''
    '''------------------------------- Date Utilities -------------------------------'''
    def compare_dates(self, date1, date2, days_threshold: int = 10):
        '''
        :param date1: A date that *only* contains the month and day. 
        :param date2: A date that *only* contains the month and day.
        :param days_threshold: The number of days that are allowed between the dates. 
        returns: Boolean that describes if the difference between date1 & date2 is less than "days_threshold".
                If it is greater than "days_threshold" it will return False. NOTE: The default is 10, but can be changed based on the users needs. 
        '''
        # Convert date strings into "datetime" objects. 
        date1 = dt.datetime.strptime(date1, "%m-%d")
        date2 = dt.datetime.strptime(date2, "%m-%d")

        # Calculate the number of days between the 2 dates. 
        # NOTE: We subtract the smaller date from the larger date to avoid negative delta. 
        if date1 > date2:
            delta = date1 - date2
        else:
            delta = date2 - date1

        # Get the days from the delta. 
        delta = delta.days

        # If the delta is less than the "days_threshold".
        if delta <= days_threshold:
            return True
        else:
            return False
    '''-------------------------------'''
    def if_date_greater(self, target_date, compare_date):
        '''
        :param target_date: The date that we are checking if it is greater or less than. 
        :param compare_date: The date that the target_date is being compared against. 
        return: Boolean. Will return True if the target_date is greater than the compare_date. 
                Will return False if the target_date is less than the compare_date. 
        '''
        # Convert the strings into "datetime".
        date_format = "%m-%d"
        target_date = dt.datetime.strptime(target_date, date_format)
        compare_date = dt.datetime.strptime(compare_date, date_format)

        if target_date > compare_date:
            return True
        else:
            return False
    '''-------------------------------'''
    def add_days_to_date(self, target_date: str, days_to_add: int =1):
        '''
        :param target_date: The date to use for the calculations.
        :param days_to_add: Number of days to add to the "target_date".
        :return: Return the new data after the calculations. 
        '''
        # Convert the string to "datetime".
        date_format = "%m-%d"
        target_date = dt.datetime.strptime(target_date, date_format)

        # Add the number of days to the target_date. 
        new_date = target_date + dt.timedelta(days=days_to_add)
        # Example: If the date is: 07-31 -> 2014-1900-08-01 00:00:00 || Get the next date "days_to_add" days after the target date. 
        # Using the strftime function will now make the date. 
        new_date = new_date.strftime(date_format)

        return new_date
    '''-------------------------------'''      
    def get_first_trading_year(self):
        try:
            # Create a Yahoo Finance Ticker object for the given symbol
            ticker = yf.Ticker(self.ticker)

            # Get historical data
            historical_data = ticker.history(period="max")

            # Extract the first trading year
            first_year = historical_data.index[0].year

            return first_year
        except Exception as e:
            print(f"Error: {e}")
            return None
    '''-------------------------------'''
    def get_date_difference(self, target_date: str, compare_date: str):
        '''
        Description: Calculates the difference between the "target_date" and "compare_date".
        
        :param target_date: Main date. 
        :param compare_date: Date to compare agains the main_date.
        :return: Integer
        '''

        date_format = "%Y-%m-%d"

        # Turn string dates into datetime objects. 
        target_date = dt.datetime.strptime(target_date, date_format)
        compare_date = dt.datetime.strptime(compare_date, date_format)
        
        # Check which date is larger. Subtract the smaller date from the larger date, to avoid negative values. 
        if target_date > compare_date:
            delta = target_date - compare_date
        else:
            delta = compare_date - target_date
        difference = delta.days
        return difference
    '''------------------------------- Alpha Vantage Utilities -------------------------------'''
    '''-------------------------------'''
    def get_fiscal_dates(self, frequency: str = "q") -> pd.DataFrame:
        '''
        :param frequency: Determines to fetch quarterly or annual data. 
        :return: A column from the dataframe, with all of the recent fiscal date, whether annual or quarterly. 
        '''
        if frequency in self.quarterly_params:
            frequency = "quarterlyEarnings"
        elif frequency in self.annual_params:
            frequency = "annualEarnings"

        # Construct the API request URL
        endpoint = 'https://www.alphavantage.co/query'
        params = {
            'function': "EARNINGS",
            'symbol': self.ticker,
            'apikey': self.key
        }

        # Make the API request
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()[frequency]
            df = pd.DataFrame(data)
            return df["fiscalDateEnding"]
        else:
            print(f"[Error] Retrieving Fiscal Dates")
        
    '''-------------------------------'''
    def get_earnings_estimates(self, frequency: str = "q"):
        if frequency in self.quarterly_params:
            frequency = "quarterlyEarnings"
        elif frequency in self.annual_params:
            frequency = "annualEarnings"

        # Construct the API request URL
        endpoint = 'https://www.alphavantage.co/query'
        params = {
            'function': "EARNINGS",
            'symbol': self.ticker,
            'apikey': self.key
        }

        # Make the api request.
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()[frequency]
            df = pd.DataFrame(data) 
            return df
        else:
            print(f"[Error] Retrieving Earnings Estimates")
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''






































































class PriceRanges:
    def __init__(self, ticker: str, year: str = "") -> None:
        self.ticker = ticker 
        
        self.year = year
    '''-------------------------------'''
    def get_all_quarters(self, quarters: dict = {}) -> dict:
        
        if quarters != {}:
            q1_start_month, q1_start_day = quarters["Q1_start"].split("/")
            q1_end_month, q1_end_day = quarters["Q1_end"].split("/")
            q2_start_month, q2_start_day = quarters["Q2_start"].split("/")
            q2_end_month, q2_end_day = quarters["Q2_end"].split("/")
            q3_start_month, q3_start_day = quarters["Q3_start"].split("/")
            q3_end_month, q3_end_day = quarters["Q3_end"].split("/")
            q4_start_month, q4_start_day = quarters["Q4_start"].split("/")
            q4_end_month, q4_end_day = quarters["Q4_end"].split("/")
        else:
            q1_start_month, q1_start_day = 1, 1
            q1_end_month, q1_end_day = 3, 31
            q2_start_month, q2_start_day = 4, 1
            q2_end_month, q2_end_day = 6, 30
            q3_start_month, q3_start_day = 7, 1
            q3_end_month, q3_end_day = 9, 30
            q4_start_month, q4_start_day = 10, 1
            q4_end_month, q4_end_day = 12, 31


        q1_data = self.get_quarter_data(start_month=q1_start_month, start_day=q1_start_day, end_month=q1_end_month, end_day=q1_end_day)
        q2_data = self.get_quarter_data(start_month=q2_start_month, start_day=q2_start_day, end_month=q2_end_month, end_day=q2_end_day)
        q3_data = self.get_quarter_data(start_month=q3_start_month, start_day=q3_start_day, end_month=q3_end_month, end_day=q3_end_day)
        q4_data = self.get_quarter_data(start_month=q4_start_month, start_day=q4_start_day, end_month=q4_end_month, end_day=q4_end_day)

        quarterly_data = {"Q1": q1_data,
                          "Q2": q2_data,
                          "Q3": q3_data,
                          "Q4": q4_data}
        
        return quarterly_data




    '''-------------------------------'''
    def get_quarter_data(self, start_month:int =1, start_day: int =1, end_month: int = 3, end_day: int = 31) -> dict:
        
        quarter_data = {}

        # Turn all of the date elements into integers. 
        start_month, start_day = int(start_month), int(start_day)
        end_month, end_day = int(end_month), int(end_day)
        


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
    def get_price_range_in_year(self, fiscal_data: dict = {}) -> dict:
        data = {}

        if fiscal_data != {}:
            fiscal_start_month, fiscal_start_day = fiscal_data["fiscal_start"].split("/")
            fiscal_end_month, fiscal_end_day = fiscal_data["fiscal_end"]

            fiscal_start_month, fiscal_start_day = int(fiscal_start_month), int(fiscal_start_day)
            fiscal_end_month, fiscal_end_day = int(fiscal_end_month), int(fiscal_end_day)

        else:
            fiscal_start_month, fiscal_start_day = 1, 1
            fiscal_end_month, fiscal_end_day = 12, 31

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
    def get_first_trading_year(self):
        try:
            # Create a Yahoo Finance Ticker object for the given symbol
            ticker = yf.Ticker(self.ticker)

            # Get historical data
            historical_data = ticker.history(period="max")

            # Extract the first trading year
            first_year = historical_data.index[0].year

            return first_year
        except Exception as e:
            print(f"Error: {e}")
            return None
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
    '''-------------------------------'''
