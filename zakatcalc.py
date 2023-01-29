# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 09:08:14 2023

@author: Definitely A Human
"""

import gspread as gs
import pandas as pd
import argparse
import datetime
import yfinance
import os
import numpy as np


def get_date_on_or_before(index_list, target):
    result = index_list.get_indexer([target], method='nearest')
    if index_list[result] > target:
        return index_list[result - 1]
    return index_list[result]
        
        
    
def main():
    parser = argparse.ArgumentParser(description="Zakat calculator for RSUs")
    parser.add_argument("--excel", dest="excel", type=str, help="Excel file")
    parser.add_argument("--json", dest="json", type=str, help="JSON file from Google API")
    parser.add_argument("--url", dest="url", type=str, help="URL to Google Sheet")
    parser.add_argument("--sheet", dest="sheet", type=str, help="Sheet name. Default is Sheet1", default="Sheet1")
    
    args = parser.parse_args()
    
    if args.excel:
        sh_df = pd.read_excel(args.excel, args.sheet)
    else:
        # Start accessing gdrive and spread sheet
        gc = gs.service_account(filename=args.json)
        sh = gc.open_by_url(args.url)
        ws = sh.worksheet(args.sheet)
        sh_df = pd.DataFrame(ws.get_all_records())
    
    # Remap the VEST_DATE column to datetime64, America/New_York
    # TODO: is it good idea to localize to NY??
    sh_df.VEST_DATE = sh_df.VEST_DATE.astype("datetime64")
    sh_df.VEST_DATE = sh_df.VEST_DATE.dt.tz_localize("America/New_York")
    
    # Start gathering all tickers in the list
    df_dict = {}
    for ticker in sh_df.TICKER.unique():
        df_dict[ticker] = yfinance.Ticker(ticker).history(period="max")
    
    # Get unique years
    year_list = []
    for date in sh_df.VEST_DATE:
        year_list.append(date.year)
    year_list = sorted(list(set(year_list)))
    
    this_year = datetime.datetime.now().year
    
    zakat_df = pd.DataFrame({"Year": year_list, 
                             "Lowest Zakat-able": [0 for i in range(len(year_list))],
                             "To_Pay": [0 for i in range(len(year_list))]})
    
    # Start process each entry in the spreadsheet
    for i, row in sh_df.iterrows():
        ticker = row.TICKER
        target_df = df_dict[ticker]
        current_date = row.VEST_DATE
        while current_date.year < this_year:
            next_haul = current_date + np.timedelta64(365, "D") # 1 haul == 365 days
            current_idx = get_date_on_or_before(target_df.index, current_date)
            next_idx = get_date_on_or_before(target_df.index, next_haul)
            mask = (target_df.index >= current_idx[0]) & (target_df.index <= next_idx[0])
            lowest = target_df.loc[mask]["Low"].min()  # Get lowest. TODO: Maybe add the date-price?
            zakat_df.loc[(zakat_df.Year == current_date.year), "Lowest Zakat-able"] += lowest * row.AMOUNT
            current_date = next_haul
    
    for year in year_list:  # Calculate 2.5%
        amount = zakat_df.loc[(zakat_df.Year == year), "Lowest Zakat-able"]
        zakat_df.loc[(zakat_df.Year == year), "To_Pay"] = amount * 0.025
    
    zakat_df = zakat_df.round({"Lowest Zakat-able": 2, "To_Pay": 2})
    
    print(zakat_df)
    return zakat_df



if __name__ == "__main__":
    start_time = datetime.datetime.now()
    ret = main()
    end_time = datetime.datetime.now()
    print(f"Ran for {(end_time - start_time).total_seconds()} seconds")
