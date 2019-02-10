# -*- coding: utf-8 -*-
"""CLI module.

 - Author:      Daniel J. Umpierrez
 - Created:     05-10-2018
 - GitHub:      https://github.com/havocesp/pcmc
"""
import argparse
import collections
import sys
import time
import warnings
from datetime import datetime as dt

import pandas as pd
import term

import pcmc.static as st
from pcmc import CoinMarketCap
from pcmc.utils import rg, epoch

warnings.filterwarnings('ignore')


def main(*exchanges, **kwargs):
    timeframe = kwargs.get('timeframe', '1h').lower()
    filter_by = kwargs.get('filter_by', 'gainers').lower()
    loop = kwargs.get('loop', False)
    loop_interval = kwargs.get('loop_interval', 60)

    timeframe = timeframe if timeframe in st.TIMEFRAMES else '1h'
    filter_by = filter_by if filter_by in ['losers', 'gainers'] else 'gainers'

    columns = ['symbol', 'volume24h', 'usd', 'btc', timeframe]

    if len(exchanges):
        columns.append('exchanges')

    rename = dict.fromkeys(columns)

    for col in columns:
        rename[col] = '% {}'.format(col.upper()) if col in st.TIMEFRAMES else col.title()

    cmd_data = None
    user_exit = False

    snapshots = collections.OrderedDict()

    cmc = CoinMarketCap()

    exchange_currencies = {ex: cmc.get_exchange_currencies(ex) for ex in exchanges}
    all_currencies = list(sorted(set(sum(list(exchange_currencies.values()), []))))

    while loop or cmd_data is None:
        try:
            data = cmc.gainers if filter_by in 'gainers' else cmc.losers
            if data:
                data = data.get(timeframe)
                data = data.set_index('symbol')  # type: pd.DataFrame
                data.index.name = 'Symbol'
            else:
                continue

            snapshots.update({epoch(True): data.copy(True)})

            data['btc'] = data['btc'].apply(lambda x: '{: >12.8f}'.format(x))

            data[timeframe] = data[timeframe].apply(lambda x: rg(float(x), '{: >+7.2f} %'))
            data['usd'] = data['usd'].apply(lambda x: term.format('{: >9,.3f}'.format(float(x)) + ' $', term.bold))
            data['volume24h'] = data['volume24h'].apply(lambda x: str(format(float(x), ' >12,.0f') + ' $').rjust(15))

            final = data[[c in all_currencies for c in data.index]]

            final['exchanges'] = [','.join([e.upper() for e in exchanges if s in exchange_currencies[e]]) for s in
                                  final.index]
            final = final[columns[1:]].rename(rename, axis=1)

            print(final)
            hour = '{:%H:%M:%S}'.format(dt.now())
            print('  {sep} {time} {sep}  '.format(sep=str('=' * 38), time=hour))
        except IndexError as err:
            user_exit = True
            raise err
        except KeyboardInterrupt:
            user_exit = True
        except Exception as err:
            user_exit = True
            raise err

        finally:
            if not user_exit:
                if not loop:
                    break
                time.sleep(loop_interval)


# noinspection PyUnusedFunction
def run():
    exchanges_list = CoinMarketCap().get_exchanges(True)

    parser = argparse.ArgumentParser()

    parser.add_argument('exchanges',
                        choices=exchanges_list,
                        metavar='EX',
                        nargs='+',
                        help='Show only currencies supported by supplied exchanges.')

    parser.add_argument('-t', '--timeframe',
                        default='1h',
                        help='CoinMarketCap valid timeframes are: 1h, 24h, 7d.')

    parser.add_argument('-f', '--filter_by',
                        default='gainers',
                        help='Set to "losers" to show currencies losers data (default "gainers").')

    parser.add_argument('-l', '--loop',
                        help='Set to "losers" to show currencies losers data (default "gainers").',
                        action='store_true')
    parser.add_argument('-i', '--loop-interval',
                        type=int,
                        default=60,
                        help='Set to "losers" to show currencies losers data (default "gainers").')

    args = parser.parse_args(sys.argv[1:])
    args = vars(args)
    exchanges = args.pop('exchanges')

    main(*exchanges, **args)
