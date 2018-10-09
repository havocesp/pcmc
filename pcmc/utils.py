# -*- coding: utf-8 -*-
"""
 PandasCoinMarketCap

 - Author:      Daniel J. Umpierrez
 - Created:     09-10-2018
 - License:     MIT
"""
import json
import time
import typing as tp
from pathlib import Path

import ccxt
from appdirs import AppDirs

HOME = AppDirs('ccxt')
HOME_CONFIG = Path(HOME.user_config_dir)
HOME_LOCAL_SHARE = Path(HOME.user_data_dir)

HOME_CONFIG.mkdir(parents=True, exist_ok=True)
HOME_LOCAL_SHARE.mkdir(parents=True, exist_ok=True)


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
    :param tp.Iterable currencies:
    :return:
    """
    currency_lists = list(currencies.values()) if isinstance(currencies, dict) else list(currencies)
    flat_currency_lists = sum(currency_lists, [])
    all_currencies = list(set(flat_currency_lists))
    return list(sorted(all_currencies))


def filter_by_exchanges(data, exchanges):
    """

    :param pd.DataFrame data:
    :param tp.Iterable[tp.AnyStr] exchanges:
    :return pd.DataFrame:
    """
    currencies = {e: get_exchange_currencies(e) for e in exchanges}
    all_currencies = get_uniq_currency_list(currencies)
    data = data[[c in all_currencies for c in data.symbol.tolist()]]
    symbols = data.symbol.tolist()
    clean = lambda x: x.strip('1234_ ').upper()
    data['exchanges'] = [','.join([clean(e) for e in exchanges if s in currencies[e]]) for s in symbols]
    return data.select(lambda x: x)
