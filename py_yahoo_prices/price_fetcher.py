import logging
import time
from datetime import datetime
from io import StringIO
from multiprocessing.pool import ThreadPool
import pandas as pd
from tqdm.auto import tqdm
import re
import requests

_logger = logging.getLogger(__name__)
PRICE_URL = "https://query1.finance.yahoo.com/v7/finance/download/{}"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"

def _get_cookies():
    # To get the cookies for the session, using hardcoded value
    r = requests.get("https://finance.yahoo.com/quote/AAPL/history?p=AAPL", headers={'User-Agent': USER_AGENT})
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
    request_params = {
        'period1': start_date_str,
        'period2': end_date_str,
        'interval': '1d',
        'events': 'history',
        'crumb': crumb
    }
    request_headers = {'Cookie': 'B={}'.format(cookie), 'User-Agent': USER_AGENT}
    # Testing if we can login using an arbitrary code
    url = PRICE_URL.format("AAPL")
    response = requests.get(url, headers=request_headers, params=request_params)
    if response.status_code == 401:
        # retry
        _logger.error('Trying to login...')
        time.sleep(3)
        return _login()
    else:
        _logger.info("Logged in successfully, fetching prices...")
        return cookie, crumb


def _single_fetch(args):
    try:
        r = requests.get(url=args['url'], params=args['params'], headers=args['headers'])
    except requests.ConnectionError as e:
        _logger.error("Error while fetching code {}, {}".format(args['code'], e))
        return None

    dat_str = str(r.content, 'ISO-8859-1')
    if not r.ok:
        _logger.error("Error while fetching code {}, status code {}, {}".format(args['code'], r.status_code, dat_str))
    else:
        dat = StringIO(dat_str)
        df = pd.read_csv(dat)
        df.dropna(inplace=True, axis=0, how='all')
        return df


def multi_price_fetch(codes_list, start_date, end_date=None, interval='1d', threads=20):
    """
     Get raw prices from yahoo in the form of a pd.DataFrame()
     :param code: <list(str)> company codes to search
     :param start_date: <datetime> start date from which the prices should be fetched
     :param end_date: <datetime> end date up till when the prices should be fetched (defaults to now())
     :param interval: <str> one of ['1d', '1wk', '1mo'] (defaults to 1d)
     :param retry_attempts: <int> number of retries on failure to fetch (defaults to 10)
     :param sleep_time: <int> time in seconds to sleep between each re attempt
     :param threads: <int> How many threads to use
     :return: {code_1: df_1, code_2: df_2, ....}
     """
    if end_date is None:
        end_date = datetime.now()

    start_date_str = '{:.0f}'.format(start_date.timestamp())
    end_date_str = '{:.0f}'.format(end_date.timestamp())
    cookie, crumb = _login()
    request_params = {
        'period1': start_date_str,
        'period2': end_date_str,
        'interval': interval,
        'events': 'history',
        'crumb': crumb
    }
    request_headers = {'Cookie': 'B={}'.format(cookie), 'User-Agent': USER_AGENT}

    method_params = [{'url': PRICE_URL.format(c),
                      'code': c,
                      'params': request_params,
                      'headers': request_headers} for c in codes_list]

    with ThreadPool(processes=threads) as pool:
        df_list = list(tqdm(pool.imap(_single_fetch, method_params), total=len(method_params)))

    out_dict = {code: df for code, df in  zip(codes_list, df_list) if df is not None}
    return out_dict

