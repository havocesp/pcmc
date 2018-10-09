# -*- coding: utf-8 -*-
"""
 PandasCoinMarketCap

 - Author:      Daniel J. Umpierrez
 - Created:     09-10-2018
 - License:     MIT
"""
import json
import numbers as nums
import time
import typing as tp
from pathlib import Path

import ccxt
import term
from appdirs import AppDirs

HOME = AppDirs('ccxt')
HOME_CONFIG = Path(HOME.user_config_dir)
HOME_LOCAL_SHARE = Path(HOME.user_data_dir)

HOME_CONFIG.mkdir(parents=True, exist_ok=True)
HOME_LOCAL_SHARE.mkdir(parents=True, exist_ok=True)


def cls():
    """
    Clear terminal content and move cursor to initial position (row 1, column 1)
    """
    term.clear()
    term.pos(1, 1)


wLn = term.writeLine


def rg(v, format_spec=None):
    """
    Returns "v" as str and red or green ANSI colored depending of its sign (+ green, - red)

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


def markets_cache_handler(api):
    """
    Load data from cached file (data is refreshed every 24h)

    :param ccxt.Exchange api:
    :return dict: markets metadata for exchange name extracted from "api" param.
    """
    MARKETS_DIR = HOME_LOCAL_SHARE.joinpath('markets')
    MARKETS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE = MARKETS_DIR.joinpath('{}.json'.format(api.id))
    DATA_FILE.touch(exist_ok=True)

    file_date = DATA_FILE.stat().st_ctime
    file_size = DATA_FILE.stat().st_size

    ts_now = int(time.time())

    less_than_24h = (ts_now - file_date) < (3600 * 24)

    if file_size > 0 and less_than_24h:
        raw = DATA_FILE.read_text()
        data = json.loads(raw)
        if data and isinstance(data, dict) and len(data) > 0:
            api.set_markets(dict(data))
    else:
        markets = api.load_markets()
        data = json.dumps(markets, indent=4)
        DATA_FILE.write_text(data)
    return api


def get_exchange_currencies(exchange):
    """
    Returns all supported currencies for "exchange".

    >>> get_exchange_currencies('hitbtc')[:4]
    ['1ST', 'ABA', 'ABTC', 'ABYSS']

    :param str exchange: exchange name
    :return list: all supported currencies for "exchange"
    """
    e = str(exchange).lower()
    api = getattr(ccxt, e)({'timeout': 30000})  # type: ccxt.Exchange
    api.markets = markets_cache_handler(api)
    split = lambda s: str(s).split('/')
    currencies = {s[0] for s in map(split, api.symbols)}
    return list(currencies)


def get_last_version(e):
    """
    Return latest exchange version reference from ccxt exchange list.

    >>> get_last_version('hitbtc')
    'hitbtc2'

    :return str: latest exchange version name available at "ccxt" lib.
    """
    return [x for x in ccxt.exchanges if x.rstrip('123_ ') in e][-1]


def get_uniq_currency_list(currencies):
    """
    Returns a sorted and deduped currency list from "currencies" param data.

    :param tp.Iterable currencies: currencies iterable to be processed.

    :return list: currencies iterable after dedupe and sorted processes.
    """
    currency_lists = list(currencies.values()) if isinstance(currencies, dict) else list(currencies)
    flat_currency_lists = sum(currency_lists, [])
    all_currencies = list(set(flat_currency_lists))
    return list(sorted(all_currencies))


def filter_by_exchanges(data, exchanges):
    """
    Receive a DataFrame and returns their content filtered by coin listed in "exchanges"

    :param pd.DataFrame data: full currencies data DataFrame type
    :param tp.Iterable[tp.AnyStr] exchanges: exchange names as iterable used for filtering.
    :return pd.DataFrame: a content filtered by coin listed in "exchanges" DataFrame
    """
    currencies = {e: get_exchange_currencies(e) for e in exchanges}
    all_currencies = get_uniq_currency_list(currencies)
    data = data[[c in all_currencies for c in data.symbol.tolist()]]
    symbols = data.symbol.tolist()
    clean = lambda x: x.strip('1234_ ').upper()
    data['exchanges'] = [','.join([clean(e) for e in exchanges if s in currencies[e]]) for s in symbols]
    return data.select(lambda x: x)


def data2nums(s):
    """
    Try to extract number from str with non numeric chars like "%" or "$" and return it as float type.

    >>> data2nums(' -2.20 % ')
    -2.2
    >>> data2nums(' -2.2a0 % ')
    ' -2.2a0 % '

    :param tp.AnyStr s: the str where to float number will be searched.
    :return: s as is or float type resulted numeric value extraction from "s" content.
    :rtype: tp.AnyStr or float
    """
    try:
        return float(str(s or '').strip(' €$%*,').replace('?', '0'))
    except ValueError:
        return s
