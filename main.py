import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt

from PriceRanges.priceranges import PriceRanges


def get_annual_data(ticker: str, start_year: int = 2000, end_year: int =2023):

    for i in range(start_year, end_year+1):
        pr = PriceRanges(ticker, year=i)
        data = pr.get_price_range_in_year()

        if np.isnan(data["High"]):
            pass
        else:
            print(f"\n\n-----------------\n{i}\n\nHigh: {data['High']}\nLow: {data['Low']}\n Average: {data['Average']}")

def get_quarterly_data(ticker:str, start_year: int = 2000, end_year: int = 2023, quarters: dict = {}):

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

    ticker = "TSLA"
    #get_annual_data(ticker)
    get_quarterly_data(ticker)

main()