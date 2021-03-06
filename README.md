# py_yahoo_prices

Get daily/weekly/monthly prices of equities from yahoo's new tricky endpoint query1.finance.yahoo.com/v7/finance/download/

If a lot of symbols are fetched at once, the API sometimes returns 404 even for symbols that have the data. Try splitting the queries into multiple chunks if this happens

# Installation
```
pip install py_yahoo_prices
 ```

# Usage
 
 ```Python
from datetime import datetime
import py_yahoo_prices.price_fetcher as pf


st_dt = datetime(2017, 6, 1)
comp_codes = ["IMM.L", "AAPL", "TSLA", ...]

# get the raw prices from yahoo, auto retries on a 401 error
raw_prices = pf.multi_price_fetch(codes_list=comp_codes,
                                  start_date=st_dt)

# the parameters can be adjusted
raw_prices = pf.multi_price_fetch(codes_list=comp_codes, 
                                  start_date=st_dt,
                                  end_date=datetime(2018, 3, 1),
                                  interval='1d',
                                  threads=50)
```

