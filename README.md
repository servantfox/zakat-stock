# zakat-stock
 Calculate Zakat on Stocks options like SPP/RSU

# Problem Statement
 Stocks have to be zakat-ed once reach haul (364 days or 365 days) of holdings (for long term investment).  
 It is hard to keep track especially for SPP/RSUs as "purchase" or "vested" dates maybe differed.
 This script is meant to help to calculate those per each year to ease zakat payment.
 
# Implementation
Uses the "lowest" price between the haul period to calculate zakat.
1. Say 10 stock vested on 10-Jan-2021. The next complete haul would be on the 10-Jan-2022 (use 365 days/haul).  
2. The lowest price of the stock between 10-Jan-2021 to 10-Jan-2022 was $10, thus the "zakat-able" amount is 10*$10 = $100.
3. Taking 2.5% of $100, would be $2.50 to be paid as zakat.  

Note the current implementation doesn't take account on the nisab, as those are varied depending on locality.  

# Requirement
Currently accept Excel xlsx format, or Google spreadsheet URL.  
Would require ```TICKER```, ```AMOUNT```, ```VEST_DATE``` columns.  
Example as below:
| TICKER | AMOUNT | VEST_DATE |
|--------|--------|-----------|
| INTC   |     16 | 2/19/2016 |
| AMD    |     22 | 8/19/2020 |

Note that only tickers that can be found in yfinance lib are supported for now.

## Excel 
Simply use ```--excel <path to XLSX file>``` 

## Google Sheet
Would require ```--json <service account JSON>``` and ```--url <spreadsheet URL>```.  
Follow steps from [stackoverflow here](https://stackoverflow.com/questions/46287267/how-can-i-get-the-file-service-account-json-for-google-translate-api).  

