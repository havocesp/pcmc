# -*- coding:utf-8 -*-
"""
CoinMarketCap site data scrapper as Pandas dataframes.
"""
import pathlib

from pcmc.core import CoinMarketCap

_CWD = pathlib.Path.cwd()

PATH_ROOT = _CWD.parent  # type: pathlib.Path

__long_description__ = PATH_ROOT.joinpath('README.md')
__long_description__.touch(exist_ok=True)
__long_description__ = __long_description__.read_text(encoding='utf-8')

__project__ = 'Pandas CoinMarketCap'
__package__ = 'pcmc'
__version__ = '0.1.4'
__license__ = 'UNLICENSE'
__author__ = 'Daniel J. Umpierrez'
__site__ = 'https://github.com/havocesp/{}'.format(__package__)
__description__ = __doc__
__email__ = 'umpierrez@pm.me'
__keywords__ = 'api-wrapper coinmarketcap crytocurrencies altcoins altcoin bitcoin exchange data stock finance'
__dependencies__ = ['requests', 'tabulate', 'pandas', 'ccxt', 'begins']
__all__ = ['CoinMarketCap', '__package__', '__description__', '__version__', '__license__', '__author__', '__site__',
           '__project__', '__email__', '__keywords__']
