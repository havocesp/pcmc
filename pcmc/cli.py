# -*- coding: utf-8 -*-
"""
 - Author:      Daniel J. Umpierrez
 - Created:     05-10-2018
 - GitHub:      https://github.com/havocesp/pcmc
"""
import collections
import time
import warnings

import begin
import pandas as pd
import tabulate as tbl
import term
from begin.utils import tobool

from pcmc import CoinMarketCap
from pcmc.utils import filter_by_exchanges, get_last_version, cls, wLn, rg

warnings.filterwarnings('ignore')

TIMEFRAMES = ['1h', '24h', '7d']


# noinspection PyUnusedFunction
@begin.start
@begin.convert(loop_interval=int, loop=tobool)
def main(timeframe='1h', filter_by='gainers', loop=False, loop_interval=60, *exchanges):
    timeframe = str(timeframe or '1h').lower()
    filter_by = str(filter_by or 'gainers').lower()

    timeframe = timeframe if timeframe in TIMEFRAMES else '1h'
    filter_by = filter_by if filter_by in ['losers', 'gainers'] else 'gainers'

    columns = ['symbol', 'volume24h', 'price', 'btc', timeframe]
    if len(exchanges):
        columns.append('exchanges')
    headers = [c.upper() for c in columns]
    table_settings = dict(headers=headers, stralign='right', numalign='right', disable_numparse=[1, 2, 3])
    rename = dict.fromkeys(columns)
    for col in columns:
        rename[col] = '% {}'.format(col.upper()) if col in TIMEFRAMES else col.title()

    exchanges = [get_last_version(e) for e in exchanges if e.rstrip('123_ ') in exchanges]
    cmd_data = None
    user_exit = False

    snapshots = collections.OrderedDict()

    while loop or cmd_data is None:
        try:
            data = CoinMarketCap().gainers_and_losers.get(filter_by).get(timeframe)  # type: pd.DataFrame

            timestamp_str = str(int(time.time()))
            snapshots.update({timestamp_str: data.copy(True)})

            # data = cmd_data[filter_by][timeframe]
            data['btc'] = data['btc'].apply(lambda x: '{: >12.8f}'.format(x))

            data[timeframe] = data[timeframe].apply(lambda x: rg(float(x), '{: >+7.2f} %'))
            data['price'] = data['price'].apply(lambda x: term.format('{: >9,.3f}'.format(float(x)) + ' $', term.bold))
            data['volume24h'] = data['volume24h'].apply(lambda x: str(format(float(x), ' >12,.0f') + ' $').rjust(15))

            final = filter_by_exchanges(data, exchanges)  # type: pd.DataFrame
            final = final[columns].rename(rename, axis=1)

            cls(), wLn(tbl.tabulate(final.to_records(False), **table_settings))
        except IndexError as err:
            print(type(err), ': ', str(err))
        except KeyboardInterrupt:
            user_exit = True
        finally:

            if not user_exit:
                if not loop:
                    break
                time.sleep(loop_interval)
