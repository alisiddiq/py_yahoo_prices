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

# get the raw prices from yahoo, auto retries on a 401 error
raw_prices = pf.get_raw_prices(code=comp_code, start_date=st_dt)

# the parameters can be adjusted
raw_prices = pf.get_raw_prices(code=comp_code, 
                               start_date=st_dt,
                               end_date=datetime(2018, 3, 1),
                               interval='1d',
                               retry_attempts=10,
                               sleep_time=3)
                               

daily_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1d')
weekly_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1wk')
monthly_returns = pf.get_returns(code=comp_code, start_date=st_dt, interval='1mo')

# Gets pct changes based on last close price
 ```
 
