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


def run():
    cmc = CoinMarketCap()
    exchanges_list = cmc.get_exchanges(True)

    parser = argparse.ArgumentParser(description='Coinmarketcap.com from CLI.')

    filter_grp = parser.add_mutually_exclusive_group()

    filter_grp.add_argument('-G', '--gainers',
                            dest='filter_by',
                            action='store_true',
                            help='Show gainers related data.')
    filter_grp.add_argument('-L', '--losers',
                            dest='filter_by',
                            action='store_false',
                            help='Show losers related data.')
    parser.add_argument('exchanges',
                        choices=exchanges_list,
                        metavar='EX',
                        nargs='+',
                        help='Show only currencies supported by supplied exchanges.')
    parser.add_argument('-t', '--timeframe',
                        default='1h',
                        nargs='?',
                        choices=[],
                        help='CoinMarketCap valid timeframes are: 1h, 24h, 7d.')
    parser.add_argument('-f', '--filter_by',
                        choices=['gainers', 'losers'],
                        default='filter_by',
                        nargs='?',
                        help='Set to "losers" to show currencies losers data (default "gainers").')
    parser.add_argument('-l', '--loop',
                        help='Enable "loop" behaviour (show data repeatedly at the supplied interval in seconds.',
                        type=int,
                        default=0,
                        nargs='?',
                        const=0)
    parser.add_argument('-m', '--minvol',
                        help='Minimum 24 hour volume amount filter.',
                        type=float,
                        default=0.0,
                        nargs='?',
                        const=0.0)

    filter_grp.set_defaults(filter_by=True)
    args = parser.parse_args(sys.argv[1:])

    main(args)


# noinspection PyUnusedFunction
def main(args):
    timeframe = args.timeframe if args.timeframe in st.TIMEFRAMES else '1h'
    filter_by = args.filter_by if args.filter_by in ['losers', 'gainers'] else 'gainers'
    columns = ['symbol', 'volume24h', 'usd', 'btc', timeframe]

    if len(args.exchanges) > 1:
        columns.append('exchanges')

    rename = dict.fromkeys(columns)

    for col in columns:
        rename[col] = f'% {col.upper()}' if col in st.TIMEFRAMES else col.title()

    cmd_data = None
    user_exit = False

    snapshots = collections.OrderedDict()

    cmc = CoinMarketCap()

    # per exchange currencies supported
    exchange_currencies = {ex: cmc.get_exchange_currencies(ex) for ex in args.exchanges}
    # sorted and unique list of currencies
    all_currencies = list(sorted(set(sum(list(exchange_currencies.values()), []))))

    while args.loop or cmd_data is None:
        try:
            if data := cmc.gainers if filter_by is True else cmc.losers:
                data = data.get(timeframe)
                data = data.set_index('symbol')  # type: pd.DataFrame
                data.index.name = 'Symbol'
            else:
                continue

            snapshots.update({epoch(True): data.copy(True)})
            print(data.head())
            data = data.query(f'volume24h > {args.minvol * 1000.0}')
            print(data.head())
            data['btc'] = data['btc'].apply(lambda x: '{: >12.8f}'.format(x))

            data[timeframe] = data[timeframe].apply(lambda x: rg(float(x), '{: >+7.2f} %'))
            data['usd'] = data['usd'].apply(lambda x: term.format('{: >9,.3f}'.format(float(x)) + ' $', term.bold))
            data['volume24h'] = data['volume24h'].apply(lambda x: str(format(float(x), ' >12,.0f') + ' $').rjust(15))

            final = data[[c in all_currencies for c in data.index]]

            exchanges_fmt = lambda s: [e.upper() for e in args.exchanges if s in exchange_currencies[e]]
            final['exchanges'] = [','.join(exchanges_fmt(s)) for s in final.index]
            final = final[columns[1:]].rename(rename, axis=1)

            print(final)
            hour = f'{dt.now():%H:%M:%S}'
            print(f'  {str("=" * 38)} {hour} {str("=" * 38)}  ')
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
                if args.loop > 0:
                    time.sleep(args.loop)
                else:
                    break
