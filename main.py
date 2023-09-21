# Operating system imports
import os

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt

from PriceRanges.priceranges import PriceRanges, FiscalScraper

# Get the current working directory. 
cwd = os.getcwd()


# Custom quarter layouts for specific companies.
avav_info =     {"annual": {
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
                 }}



default_quarters = {}









def get_annual_data(ticker: str, fiscal_data: dict = {}):

    pr_dud = PriceRanges(ticker)
    start_year = pr_dud.get_first_trading_year()
    end_year = dt.datetime.now().year

    for i in range(start_year, end_year+1):
        pr = PriceRanges(ticker, year=i)
        data = pr.get_price_range_in_year()

        if np.isnan(data["High"]):
            pass
        else:
            print(f"\n\n-----------------\n{i}\n\nHigh: {data['High']}\nLow: {data['Low']}\n Average: {data['Average']}")

def get_quarterly_data(ticker:str, quarters: dict = {}):

    # Create PR_object to get the first trading year. 
    pr_dud = PriceRanges(ticker)

    start_year = pr_dud.get_first_trading_year()
    end_year = dt.datetime.now().year

    for i in range(start_year, end_year+1):
        pr = PriceRanges(ticker, year=i)

        quarterly_data = pr.get_all_quarters(quarters=quarters)
        print(f"---------------------------------")
        
        for key, val in quarterly_data.items():
            if np.isnan(val['High']):
                pass
            else:
                print(f"------\n{key} {i}")
                print(f"High  {val['High']}\nLow: {val['Low']}\nAverage: {val['Average']}")
      






def set_fiscal_data(ticker: str):
    """
    ticker: Ticker of a company. 
    
    Takes a ticker as a string. Searches a csv file names "quarterly_filings"
    """

    csv_file = pd.read_csv(cwd + "\\Filings\\quarterly_filings.csv")

    # Check if the ticker is in the csv file. 
    ticker_found = csv_file[csv_file["ticker"] == ticker]
    
    if ticker_found.empty:
        # Create a "FiscalScraper" class object.
        fs = FiscalScraper(ticker)
        # Get the quarterly filings for the income statement. 
        income_statement = fs.get_income_statement(frequency="q")
        income_statement_cols = income_statement.columns
        # Get the last 4 columns.
        income_statement_cols = income_statement_cols[-4:]
        # Get the fiscal year end for the company. 
        fiscal_end = fs.get_fiscal_year_end_date()

        fs.organize_quarters(income_statement_cols, fiscal_end=fiscal_end)

        #print(f"Fiscal_end: {fiscal_end}     {income_statement}")
    







def main():

    default_quarters = {
        "Q1_start": "1/1",
        "Q1_end": "3/31",
        "Q2_start": "4/1",
        "Q2_end": "6/30",
        "Q3_start": "7/1",
        "Q3_end": "9/30",
        "Q4_start": "10/1",
        "Q4_end": "12/31" 
    }

    ticker = "AMZN"
    set_fiscal_data(ticker)
    #get_annual_data(ticker)
    #get_quarterly_data(ticker, quarters=default_quarters)

"""

TODO:

Finish organize quarters function. 

"""



main()