# py_yahoo_prices

Get daily/weekly/monthly returns and prices of equities from yahoo's new tricky endpoint query1.finance.yahoo.com/v7/finance/download/

# Installation
```
pip install py_yahoo_prices
 ```

# Usage
 
 ```Python
from datetime import datetime
import py_yahoo_prices.price_fetcher as pf


st_dt = datetime(2017, 6, 1)
comp_code = "IMM.L"

# get the raw prices from yahoo
raw_prices = pf.get_raw_prices(code=comp_code, start_date=st_dt)


daily_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1d')
weekly_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1wk')
monthly_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1mo')

# Gets pct changes based on last close price
 ```
 
