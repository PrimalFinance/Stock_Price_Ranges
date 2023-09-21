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

# Yahoo Finance imports
import yfinance as yf

chrome_driver = "D:\\ChromeDriver\\chromedriver.exe"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

"""fiscal_params = {
    "AVAV": {"annual": {
                    "fiscal_start": "",
                    "fiscal_end": "",
                },
                  "quarterly": {
                    "Q1_start": "7/30",
                    "Q1_end": "10/28",
                    "Q2_start": "10/29",
                    "Q2_end": "1/27",
                    "Q3_start": "1/28",
                    "Q3_end": "4/29",
                    "Q4_start": "4/30",
                    "Q4_end": "7/29",
            }}, 
    "CHPT": {"annual": {
                "fiscal_start": "1/1",
                "fiscal_end": "1/31",
                "fiscal_year_adjust": True,
            },
            "quarterly": {
                "Q1_start": "1/1",
                "Q1_end": "4/31",
                "Q1_year_adjust": True,
                "Q2_start": "5/1",
                "Q2_end": "7/31",
                "Q2_year_adjust": True,
                "Q3_start": "8/1",
                "Q3_end": "10/31",
                "Q3_year_adjust": True,
                "Q4_start": "11/1",
                "Q4_end": "1/31",
                "Q4_year_adjust": 
            }},
     
    "DUD": {"annual": {
                "fiscal_start": "",
                "fiscal_end": "",
                "fiscal_year_adjust": ""
            },
            "quarterly": {
                "Q1_start": "",
                "Q1_end": "",
                "Q1_year_adjust": "",
                "Q2_start": "",
                "Q2_end": "",
                "Q2_year_adjust": "",
                "Q3_start": "",
                "Q3_end": "",
                "Q3_year_adjust": "",
                "Q4_start": "",
                "Q4_end": "",
                "Q4_year_adjust": ""
            }},
}
"""





class FiscalScraper: 
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.key = os.getenv("alpha_vantage_key")

        # Root url to make queries. 
        self.root_url = "https://www.alphavantage.co/"

        # Variables for financial statements.
        self.income_statement = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cash_flow = pd.DataFrame()
        self.earnings = pd.DataFrame()

        # List of possible function parameters for financial report frequency.
        self.quarterly_params = ["q", "Q", "Quarter", "quarter", "Quarterly", "quarterly"]
        self.annual_params = ["a", "A", "Annual", "annual"]

    '''-------------------------------'''
    def get_fiscal_year_end_date(self):
        sec_annual_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={self.ticker}&type=10-k&dateb=&owner=include&count=100&search_text="
        
        self.create_browser(sec_annual_url)


        # Loop vars 
        running = True
        filing_index = 2
        date_index = 2

        while running:
            filing_type_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[2]/td[1]"
            filing_type_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[{filing_index}]/td[1]"
            date_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[{date_index}]/td[4]"
            # Extract the data.
            filing_type = self.read_data(filing_type_xpath)
            filing_date = self.read_data(date_xpath)

            if filing_type == "10-K":
                print(f"Filing Type: {filing_type} {filing_date}")
                documents_button_xpath = f"/html/body/div[4]/div[4]/table/tbody/tr[2]/td[{filing_index}]/a[1]" 
                self.click_button(documents_button_xpath)
                # NOTE: This xpath does not require an index to be incremented. 
                period_of_report_xpath = "/html/body/div[4]/div[1]/div[2]/div[2]/div[2]"
                period_of_report = self.read_data(period_of_report_xpath)
                return period_of_report
                


            filing_index += 1
            date_index += 1
                
        
        
    '''-------------------------------'''
    def organize_quarters(self, quarters: list, fiscal_end: str):
        '''
        :param quarters: Unordered list of the most recent 4 quarters.
        :param fiscal_end: The date of the 4th quarter. 
        
        :return: list of organized quarters. 
        '''

        print(f"Quarters: {quarters}  Fiscal: {fiscal_end}")




    '''-------------------------------'''
    def get_all_quarters(self, quarters: dict = {}):
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

        ticker = yf.Ticker(self.ticker)

        # Get the income statement
        income_statement = ticker.financials(yearly=False)

        # Print the income statement.
        print(f"Income Statement: {income_statement}")

    '''-------------------------------'''
    '''-------------------------------'''
    def set_income_statement(self, frequency: str ="q") -> None:
        '''
        frequency: Determines if quarterly data or annual data is set. 
        '''

        # Create a query to get the data.
        query = self.build_query(func="INCOME_STATEMENT")
        r = requests.get(query)
        data = r.json()

        # Create a dataframe. 
        if frequency in self.quarterly_params:
            self.income_statement = pd.DataFrame(data["quarterlyReports"])
        elif frequency in self.annual_params:
            self.income_statement = pd.DataFrame(data["annualReports"])

        # Make the row index the dates of the filing. 
        self.income_statement.set_index("fiscalDateEnding", inplace=True)
        # Transpose the dataframe to swap the row labels with the column labels. We want the dates to be the column. 
        self.income_statement = self.income_statement.transpose()
        # Reverse the order of the columns. We want the oldest filings on the left, and the newest ones on the right.
        self.income_statement = self.income_statement.iloc[:, ::-1]

    '''-----------------------------------'''
    def get_income_statement(self, frequency: str = "q") -> pd.DataFrame:
        if self.income_statement.empty:
            self.set_income_statement(frequency=frequency)
        print(f"- [Scraper Data Retrieved] Income Statement data was collected from Alpha Vantage Scraper")
        return self.income_statement


    '''-------------------------------'''
    def build_query(self, func: str) -> str:
        end_point = f"query?function={func}&symbol={self.ticker}&apikey={self.key}"
        query = self.root_url + end_point
        return query
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
    def read_data(self, xpath: str):
        '''
        :param xpath: Path to the web element.
        :return: None
        '''

        data = self.browser.find_element("xpath", xpath).text
        return data
    '''-------------------------------'''
    def click_button(self, xpath: str):
        '''
        :param xpath: Path to the web element. 
        :return: None
        '''

        element = self.browser.find_element("xpath", xpath)
        element.click()


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
