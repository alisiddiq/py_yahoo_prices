import logging
import time
from datetime import datetime
from io import StringIO
import py_yahoo_prices.async_fetch as af
import asyncio
import pandas as pd
import re
import requests

_logger = logging.getLogger(__name__)
PRICE_URL = "https://query1.finance.yahoo.com/v7/finance/download/{}"

def _get_cookies():
    # To get the cookies for the session, using hardcoded value
    r = requests.get("https://finance.yahoo.com/quote/AAPL/history?p=AAPL")
    try:
        cookie = r.cookies.get('B')
        crumb = re.search(r'"CrumbStore":{"crumb":"(.{11})"}', r.text).group(1)
        return cookie, crumb
    except AttributeError as e:
        return '', ''

def _login():
    cookie, crumb = _get_cookies()
    start_date_str = '{:.0f}'.format(datetime.now().timestamp())
    end_date_str = '{:.0f}'.format(datetime.now().timestamp())
    params = {
        'period1': start_date_str,
        'period2': end_date_str,
        'interval': '1d',
        'events': 'history',
        'crumb': crumb
    }
    headers = {'Cookie': 'B={}'.format(cookie)}
    # Testing if we can login
    url = PRICE_URL.format("AAPL")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401:
        # retry
        _logger.error('Trying to login...')
        time.sleep(3)
        return _login()
    else:
        return cookie, crumb

def multi_price_fetch(codes_list, start_date, end_date=datetime.now(), interval='1d'):
    """
     Get raw prices from yahoo in the form of a pd.DataFrame()
     :param code: <list(str)> company codes to search
     :param start_date: <datetime> start date from which the prices should be fetched
     :param end_date: <datetime> end date up till when the prices should be fetched (defaults to now())
     :param interval: <str> one of ['1d', '1wk', '1mo'] (defaults to 1d)
     :param retry_attempts: <int> number of retries on failure to fetch (defaults to 10)
     :param sleep_time: <int> time in seconds to sleep between each re attempt
     :return: {code_1: df_1, code_2: df_2, ....}
     """
    start_date_str = '{:.0f}'.format(start_date.timestamp())
    end_date_str = '{:.0f}'.format(end_date.timestamp())
    cookie, crumb = _login()
    params = {
        'period1': start_date_str,
        'period2': end_date_str,
        'interval': interval,
        'events': 'history',
        'crumb': crumb
    }
    headers = {'Cookie': 'B={}'.format(cookie)}
    url_list = [PRICE_URL.format(c) for c in codes_list]
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(af.run(url_list, params, headers))
    responses = loop.run_until_complete(future)

    out_dict = {}
    for c, response in zip(codes_list, responses):
        dat_str = str(response,'utf-8')
        if '"error":{"code":' in dat_str:
            _logger.error("Error while fetching code {}, {}".format(c, dat_str))
        else:
            dat = StringIO(dat_str)
            df = pd.read_csv(dat)
            # Making sure dtypes are converted
            df['Date'] = pd.to_datetime(df['Date'])
            df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = pd.to_numeric(
                df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
                .stack(), errors='coerce').unstack()
            df.index = df['Date']
            df.sort_index(inplace=True)
            df.drop('Date', axis=1, inplace=True)
            out_dict[c] = df

    return out_dict