# -*- coding: utf-8 -*-
"""
 - Author:      Daniel J. Umpierrez
 - Created:     05-15-18 00:10
 - GitHub:      https://github.com/havocesp/pcmc
"""
import json
import time
import typing as tp
import warnings
from pathlib import Path

import begin
import ccxt
import pandas as pd
import tabulate as tbl
import term
from appdirs import AppDirs
from begin.utils import tobool

from pcmc import CoinMarketCap

warnings.filterwarnings('ignore')

TIMEFRAMES = ['1h', '24h', '7d']
HOME = AppDirs('ccxt')
HOME_CONFIG = Path(HOME.user_config_dir)
HOME_LOCAL_SHARE = Path(HOME.user_data_dir)

HOME_CONFIG.mkdir(parents=True, exist_ok=True)
HOME_LOCAL_SHARE.mkdir(parents=True, exist_ok=True)

SETTINGS = dict(timeout=30000)


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
        return data
    else:
        markets = api.load_markets()
        data = json.dumps(markets, indent=4)
        DATA_FILE.write_text(data)
        return markets


def get_exchange_currencies(exchange):
    """
    Returns all supported currencies for "exchange".

    >>> get_exchange_currencies('hitbtc')[:4]
    ['1ST', 'ABA', 'ABTC', 'ABYSS']

    :param str exchange: exchange name
    :return list: all supported currencies for "exchange"
    """
    e = str(exchange).lower()
    api = getattr(ccxt, e)(SETTINGS)  # type: ccxt.Exchange
    api.markets = markets_cache_handler(api)
    split = lambda s: str(s).split('/')
    currencies = {s[0] for s in map(split, api.symbols)}
    return list(currencies)


def _get_last_version(e):
    """
    Return latest exchange version reference from ccxt exchange list.

    >>> _get_last_version('hitbtc')
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


# noinspection PyUnusedFunction
@begin.start
@begin.convert(loop_interval=int, loop=tobool)
def main(timeframe='1h', filter_by='gainers', loop=False, loop_interval=60, *exchanges):
    timeframe = str(timeframe or '1h').lower()
    filter_by = str(filter_by or 'gainers').lower()

    timeframe = timeframe if timeframe in TIMEFRAMES else '1h'
    filter_by = filter_by if filter_by in ['losers', 'gainers'] else 'gainers'

    columns = ['symbol', 'volume24h', 'price', 'btc', timeframe, 'exchanges']
    headers = [c.upper() for c in columns]
    table_settings = dict(headers=headers, stralign='right', numalign='right', disable_numparse=[1, 2, 3])
    rename = dict.fromkeys(columns)
    for col in columns:
        rename[col] = '% {}'.format(col.upper()) if col in TIMEFRAMES else col.title()

    exchanges = [_get_last_version(e) for e in exchanges if e.rstrip('123_ ') in exchanges]
    cmd_data = None
    user_exit = False
    while loop or cmd_data is None:
        try:
            cmd_data = CoinMarketCap().gainers_and_losers
            data = cmd_data[filter_by][timeframe]  # type: pd.DataFrame
            data['btc'] = data['btc'].apply(lambda x: '{: >12.8f}'.format(x))
            data[timeframe] = data[timeframe].apply(lambda x: term.format('{: >+7.2f} %'.format(float(x))), term.green)
            data['price'] = data['price'].apply(lambda x: term.format(format(float(x), ' >9,.3f') + ' $', term.bold))
            data['volume24h'] = data['volume24h'].apply(lambda x: str(format(float(x), ' >12,.0f') + ' $').rjust(15))
            final = filter_by_exchanges(data, exchanges)  # type: pd.DataFrame
            final = final[columns].rename(rename, axis=1)
            term.clear(), term.pos(1, 1)
            print(tbl.tabulate(final.to_records(False), **table_settings))
        except IndexError as err:
            print(type(err), ': ', str(err))
        except KeyboardInterrupt:
            user_exit = True
        finally:
            if not user_exit and loop:
                time.sleep(loop_interval)
