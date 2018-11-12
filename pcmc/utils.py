# -*- coding: utf-8 -*-
"""
 Pandas CoinMarketCap

 - Author:      Daniel J. Umpierrez
 - Created:     09-10-2018
 - License:     UNLICENSE
"""
import numbers as nums
import sys
import time
import typing as tp
import warnings
from http.client import HTTPException, InvalidURL
from urllib.request import Request, build_opener, HTTPError

import pandas as pd
import pcmc.static as st
import term


# ROOT = AppDirs('ccxt')
# HOME_CONFIG = Path(ROOT.user_config_dir)
# HOME_LOCAL_SHARE = Path(ROOT.user_data_dir)
#
# HOME_CONFIG.mkdir(parents=True, exist_ok=True)
# HOME_LOCAL_SHARE.mkdir(parents=True, exist_ok=True)


def pandas_settings(precision=8, max_width=120, max_rows=25):
    pd.options.display.precision = precision
    pd.options.display.width = max_width
    pd.options.display.max_rows = max_rows
    pd.options.display.float_format = lambda v: str(
        '{:.8f}'.format(v).rstrip('.0') if 0.0 < abs(v) < .1 else '{:,.3f}'.format(v).rstrip(
            ',.0')) if len(str('{:.8f}'.format(v).rstrip('.0') if 0.0 < abs(v) < .1 else '{:,.3f}'.format(v).rstrip(
        ',.0'))) else '0'
    pd.options.display.date_dayfirst = True
    pd.options.display.colheader_justify = 'center'
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    warnings.catch_warnings()


# noinspection PySameParameterValue
def rg(v, format_spec=None):
    """Returns "v" as str and red or green ANSI colored depending of its sign (+ green, - red).

    >>> colored_value = rg(0.1)
    >>> colored_value == '\x1b[32m0.1\x1b[0m\x1b[27m'
    True

    :param nums.Number v: number to be colored
    :param tp.AnyStr format_spec: format specification (python 3 style)
    :return str: v as str and red or green ANSI colored depending of its sign (+ green, - red)
    """

    if v and isinstance(v, str):
        try:
            v = float(v)
        except ValueError:
            return v

    if v and isinstance(v, nums.Number):
        v = float(str(v))
        is_zero = v == 0.0
        is_neg = v < 0.0

        format_spec = format_spec or '{}'

        try:
            v = str(format_spec).format(v)
        except ValueError:
            v = '{}'.format(v)

        if is_zero:
            return term.format(v, term.white, term.dim)
        else:
            return term.format(v, term.red if is_neg else term.green)


#
# def markets_cache_handler(api):
#     """Load data from cached file (data is refreshed every 24h)
#
#     :param ccxt.Exchange api: ccxt Exchange instance
#     :return dict: markets metadata for exchange name extracted from "api" param.
#     """
#     MARKETS_DIR = HOME_LOCAL_SHARE.joinpath('markets')
#     MARKETS_DIR.mkdir(parents=True, exist_ok=True)
#     DATA_FILE = MARKETS_DIR.joinpath('{}.json'.format(api.id))
#     DATA_FILE.touch(exist_ok=True)
#
#     file_date = DATA_FILE.stat().st_ctime
#     file_size = DATA_FILE.stat().st_size
#
#     ts_now = int(time.time())
#
#     less_than_24h = int(ts_now - file_date) < int(3600 * 24)
#
#     if file_size > 0 and less_than_24h:
#         raw = DATA_FILE.read_text()
#         data = json.loads(raw)
#         if data and isinstance(data, dict) and len(data) > 0:
#             api.set_markets(dict(data))
#     else:
#         markets = api.load_markets()
#         data = json.dumps(markets, indent=4)
#         DATA_FILE.write_text(data)
#     return api


# def fusit(iterable):
#     """
#     Flat Uniq and Sort Iterable (FUSIT)
#
#     Returns a sorted and deduped currency list from "currencies" param data.
#
#     :param tp.Iterable iterable: currencies iterable to be processed.
#
#     :return list: currencies iterable after dedupe and sorted processes.
#     """
#     if iterable and isinstance(iterable, tp.Iterable):
#         if isinstance(iterable, dict):
#             lists = list(iterable.values())
#         elif isinstance(iterable, (set, tuple)):
#             lists = list(iterable)
#         else:
#             lists = [iterable]
#     else:
#         return list()
#     flat_list = set(sum(lists, []))
#     return sorted(flat_list)


def data2num(s):
    """Try to extract number from str with non numeric chars like "%" or "$" and return it as float type.

    >>> data2num(' -2.20 % ')
    -2.2
    >>> data2num(' -2.2a0 % ')
    ' -2.2a0 % '

    :param tp.AnyStr s: the str where to float number will be searched.
    :return: "s" as is or float type resulted numeric value extraction from "s" content.
    :rtype: tp.AnyStr or float
    """
    try:
        return float(str(s or '').strip(' $%').replace('?', '0').replace(',', '').strip(' *'))
    except ValueError:
        return s


def epoch(to_str=False):
    """Return local datetime (unix epoch).

    :param bool to_str: if True, returned value will converted from int to str.
    :return int: current datetime integer with amount of seconds since 01-01-2018 (unix epoch).
    """
    timestamp = int(time.time())
    return str(timestamp) if to_str else timestamp


def get_url(url, retries=-1, wait_secs=15, verbose=True):
    """Read URL content and return it as str type.

    :param str url: URL to retrieve as str.
    :param int retries: max retries, if retries value is negative there is no attempts limit (default -1)
    :param int wait_secs: sleep time in secs between retries.
    :param bool verbose: if True all catches errors will be reported to stderr.
    :return str: raw url content as str type. In case of error, an empty string will be returned.
    """

    while retries > 0:
        try:
            handler = build_opener()
            request = Request(url, headers=st.HEADERS)
            response = handler.open(request)
            response = response.read()
            return response.decode('utf-8')
        except InvalidURL:
            print('{} is not a valid URL'.format(str(url)))
            return str()
        except (HTTPException, HTTPError) as err:
            if verbose:
                print(str(err), file=sys.stderr)
                print(' - Retrying', file=sys.stderr)
            retries -= 1
            time.sleep(wait_secs)
        except KeyboardInterrupt:
            return str()
        except Exception as err:
            return str()
