# Operating system imports
import os

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt

from PriceRanges.priceranges import PriceRanges, FiscalScraper

# Get the current working directory. 
cwd = os.getcwd()
# Path to csv file.
csv_file_path = cwd + "\\Filings\\quarterly_filings.csv"


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








'''-------------------------------'''
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

'''-------------------------------'''
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
      

'''-------------------------------'''
def get_quarterly_data2(ticker: str):
    '''
    :param ticker: Ticker to search data for. 
    :return: 
    '''
    # Read in the data from the csv file. 
    quarter_data_csv = pd.read_csv(csv_file_path)

    ticker_found = quarter_data_csv[quarter_data_csv["ticker"] == ticker]

    # If data for the ticker is not in the csv file, set it. 
    if ticker_found.empty:
        set_fiscal_data(ticker=ticker)
        # Read the csv again now that the data is in it. 
        quarter_data_csv = pd.read_csv(csv_file_path)
        # Create a new ticker_found variable that now has data. 
        ticker_found = quarter_data_csv[quarter_data_csv["ticker"] == ticker]

    # Create a FiscalScraper Object. 
    fs = FiscalScraper(ticker)

    first_trading_year = fs.get_first_trading_year()
    
    if first_trading_year < 2000:
        first_trading_year = 2000 

    # Get the current year.
    end_year = dt.datetime.now().year+1

    for year in range(first_trading_year, end_year):
        # Get the price data for the quarters in the year.
        quarter_data = fs.get_quarters_price_data(ticker_found, year)

        for key, val in quarter_data.items():
            if np.isnan(val["data"]["High"]):
                pass
            else:
                print(f"-----------------------------------\n{key} {year}          Start Date: {val['start']  } || End Date: {val['end']}")
                print(f"High {val['data']['High']}\nLow: {val['data']['Low']}\nAverage: {val['data']['Average']}")
            
    # If the company has an offset fiscal year. 
    q1_date = quarter_data_csv[quarter_data_csv["ticker"] == ticker]["Q1"].values[0]
    q4_date = quarter_data_csv[quarter_data_csv["ticker"] == ticker]["Q4"].values[0]
    print(f"Quarter: {q4_date}   Type: {type(q4_date)}")
    if fs.if_date_greater(target_date=q1_date, compare_date=q4_date):
        # Since the year is offset, add one to it. 
        cur_year = dt.datetime.now().year+1
        offset_quarter_data = fs.get_quarters_price_data(ticker_found, cur_year)
        print(f"-------------------------------------------- NOTE: The quarter labeling is wrong. Use the 'Start Date' and 'End Date' as a reference. ")
        for key, val in offset_quarter_data.items():
            print(f"Key: {key}  {val}")
            if np.isnan(val["data"]["High"]):
                pass
            else:
                print(f"-----------------------------------\n{key} {year}          Start Date: {val['start']  } || End Date: {val['end']}")
                print(f"High {val['data']['High']}\nLow: {val['data']['Low']}\nAverage: {val['data']['Average']}")
    else:
        offset_fiscal_year = False



'''-------------------------------'''
def get_annual_data2(ticker: str): 
    # Read in the data from the csv file. 
    quarter_data_csv = pd.read_csv(csv_file_path)
    # Get the row that matches the ticker. 
    ticker_found = quarter_data_csv[quarter_data_csv["ticker"] == ticker]
    
    # Create "FiscalScraper object."
    fs = FiscalScraper(ticker)

    # If data for the ticker is not in the csv file, set it. 
    if ticker_found.empty:
        set_fiscal_data(ticker=ticker)
        # Read the csv again now that the data is in it. 
        quarter_data_csv = pd.read_csv(csv_file_path)
        # Create a new ticker_found variable that now has data. 
        ticker_found = quarter_data_csv[quarter_data_csv["ticker"] == ticker]

    first_trading_year = fs.get_first_trading_year()

    fiscal_start_end = {
        "fiscal_start": quarter_data_csv[quarter_data_csv["ticker"] == ticker]["Q1"].values[0],
        "fiscal_end": quarter_data_csv[quarter_data_csv["ticker"] == ticker]["Q4"].values[0]
    }

    # Get the current year. 
    current_year = dt.datetime.now().year
    for y in range(first_trading_year, current_year+1):
        annual_data = fs.get_annual_price_data(fiscal_start_end, y)

        
        
        if np.isnan(annual_data["data"]["High"]):
            pass
        else:
            print(f"-----------------------------------\nFY {y}          Start Date: {annual_data['start']  } || End Date: {annual_data['end']}")
            print(f"High {annual_data['data']['High']}\nLow: {annual_data['data']['Low']}\nAverage: {annual_data['data']['Average']}")

    
    

'''-------------------------------'''





def set_fiscal_data(ticker: str):
    """
    ticker: Ticker of a company. 

    Takes a ticker as a string. Searches a csv file names "quarterly_filings"
    """

    csv_file = pd.read_csv(csv_file_path)

    # Check if the ticker is in the csv file. 
    ticker_found = csv_file[csv_file["ticker"] == ticker]

    if ticker_found.empty:
        # Create a "FiscalScraper" class object.
        fs = FiscalScraper(ticker)
        # Get the quarterly filings for the income statement. 
        income_statement = fs.get_income_statement(frequency="q")
        income_statement_cols = income_statement.columns.to_list()
        # Get the last 4 columns.
        income_statement_cols = income_statement_cols[-4:]
        # Get the fiscal year end for the company. 
        fiscal_end = fs.get_fiscal_year_end_date()
        # Get the organized quarters. 
        organized_quarters = fs.organize_quarters(income_statement_cols, fiscal_end=fiscal_end)
        organized_quarters = [organized_quarters]
        # Turn the dictionary into a list. The only element should be this dictionary. 
        # Update csv dataframe with new values. 
        csv_file = csv_file.from_records(organized_quarters)

        csv_file.to_csv(csv_file_path, mode="a",header=False,index=False)

        print(f"CSV: {csv_file}")
    else: 
        print(f"Data already in CSV")





        #print(f"DF: {df}")
    







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

    ticker = "CHPT"
    get_annual_data2(ticker)
    #get_quarterly_data2(ticker)
    #fs = FiscalScraper(ticker)
    #fs.get_annual_price_data()
    #set_fiscal_data(ticker)
    #get_annual_data(ticker)
    #get_quarterly_data(ticker, quarters=default_quarters)

"""

TODO:

Finish organize quarters function. 

"""



main()