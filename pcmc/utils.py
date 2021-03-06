# -*- coding: utf-8 -*-
"""Utils module.

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
import term

import pcmc.static as st


def pandas_settings(precision=8, max_width=120, max_rows=25):
    """Pandas settings handler.

    :param int precision: sets max decimals after 'dot' for "float" type or similar.
    :param int max_cols: amount of chars per line limiter.
    :param int max_rows: amount lines limiter
    """
    pd.options.display.precision = precision
    pd.options.display.width = max_width
    pd.options.display.max_rows = max_rows
    in_range = lambda v: f'{v:.8f}'.rstrip('.0') if 0.0 < abs(v) < .1 else f'{v:,.3f}'.rstrip(',.0')
    pd.options.display.float_format = lambda v: str(in_range(v)) if len(in_range(v)) else '0'
    pd.options.display.date_dayfirst = True
    pd.options.display.colheader_justify = 'center'
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    warnings.catch_warnings()


def str_subs(text, *args):
    for e in args:
        text = text.replace(*(e if len(e) > 1 else (e[0], '')))
    return text


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

    if isinstance(v or 0, str):
        try:
            v = float(v)
        except ValueError:
            return v

    if isinstance(v or [], nums.Number):
        v = float(str(v))
        is_zero = v == 0.0
        is_neg = v < 0.0

        try:
            v = format_spec.format(v)
        except (ValueError, TypeError):
            v = f'{v}'

        if is_zero:
            return term.format(v, term.white, term.dim)
        else:
            return term.format(v, term.red if is_neg else term.green)


def data2num(s):
    """Try to extract number from str with non numeric chars like "%" or "$" and return it as float type.

    >>> data2num(' -2.20 % ')
    -2.2
    >>> data2num(' -2.2a0 % ')
    ' -2.2a0 % '

    :param tp.Text s: the str where to float number will be searched.
    :return: "s" as is or float type resulted numeric value extraction from "s" content.
    :rtype: tp.Text or float
    """
    try:
        return float(str(s).strip(' $%').replace('?', '0').replace(',', '').strip(' *'))
    except ValueError:
        return s


# noinspection PySameParameterValue
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
            print(f'{str(url)} is not a valid URL')
            return str()
        except (HTTPException, HTTPError) as err:
            if verbose:
                print(str(err), file=sys.stderr)
                print(' - Retrying', file=sys.stderr)
            retries -= 1
            time.sleep(wait_secs)
        except KeyboardInterrupt:
            return str()
        except IOError as err:
            return str(err)
