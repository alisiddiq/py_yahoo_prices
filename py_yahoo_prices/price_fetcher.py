import logging
import time
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import StringIO
import lxml.html

import pandas as pd
import re
import requests

_logger = logging.getLogger(__name__)
yahoo_url = "https://finance.yahoo.com/quote/{}/history?p={}"

def _get_cookies(code):
    r = requests.get(yahoo_url.format(code, code))
    # Testing if code exists
    tree = lxml.html.fromstring(r.text)
    name_elem = tree.cssselect('h1.D\(ib\)')
    if len(name_elem) == 0:
        _logger.error("company code {} not found".format(code))
        sys.exit(1)
    else:
        try:
            cookie = r.cookies.get('B')
            crumb = re.search(r'"CrumbStore":{"crumb":"(.{11})"}', r.text).group(1)
            return cookie, crumb
        except AttributeError as e:
            return '', ''

def get_raw_prices(code, start_date, end_date=datetime.now(), interval='1d', retry_attempts=10, sleep_time=5):
    """
    Get raw prices from yahoo in the form of a pd.DataFrame()
    :param code: <str> company code
    :param start_date: <datetime> start date from which the prices should be fetched
    :param end_date: <datetime> end date up till when the prices should be fetched (defaults to now())
    :param interval: <str> one of ['1d', '1wk', '1mo'] (defaults to 1d)
    :param retry_attempts: <int> number of retries on failure to fetch (defaults to 10)
    :param sleep_time: <int> time in seconds to sleep between each re attempt
    :return: <pd.DataFrame> raw prices as they are returned from yahoo
    """
    start_date_str = '{:.0f}'.format(start_date.timestamp())
    end_date_str = '{:.0f}'.format(end_date.timestamp())
    cookie, crumb = _get_cookies(code)
    out = None
    url = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(code)

    params = {
        'period1': start_date_str,
        'period2': end_date_str,
        'interval': interval,
        'events': 'history',
        'crumb': crumb
    }

    headers = {'Cookie': 'B={}'.format(cookie)}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 401:
        # retry
        _logger.error(response.text)
        _logger.error('Status code 401, retrying after {} secs...'.format(sleep_time))
        time.sleep(sleep_time)
        if retry_attempts > 0:
            out = get_raw_prices(code, start_date, end_date, interval, retry_attempts - 1, sleep_time)
            return out
        else:
            _logger.error('FAILED after multiple reattempts')
    if response.status_code == 200:
        dat = StringIO(response.text)
        out = pd.read_csv(dat)
        # Making sure dtypes are converted
        out['Date'] = pd.to_datetime(out['Date'])
        out[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = pd.to_numeric(out[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
                                                                                     .stack(), errors='coerce').unstack()
        out.index = out['Date']
        out.sort_index()
        out.drop('Date', axis=1, inplace=True)
    return out

def get_returns(code, start_date, end_date=datetime.now(), interval='1d'):
    """
    Get daily returns from yahoo, based on the Close prices
    :param code: <str> company code
    :param start_date: <datetime> start date from which the deltas should be fetched
    :param end_date: <datetime> end date up till which the deltas should be fetched
    :param interval: <str> one of ['1d', '1wk', '1mo'] for daily, weekly and monthly returns defaults to daily
    :return: <pd.Series> with datetime as index and pct_changes as values
    """
    # Making sure we get the the delta even on the start date
    raw_start = start_date - relativedelta(months=2)
    raw_prices = get_raw_prices(code, raw_start, end_date, interval=interval)
    pct_changes = raw_prices['Close'].pct_change()
    return pct_changes[start_date:end_date]
