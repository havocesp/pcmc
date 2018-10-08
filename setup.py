# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import pcmc

classifiers = [
    'Development Status :: 5 - Production',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]

exclude = ['.idea*', 'build*', '{}.egg-info*'.format(__package__), 'dist*', 'venv*', 'doc*', 'lab*']

setup(
    name=pcmc.__project__,
    version=pcmc.__version__,
    packages=find_packages(exclude=exclude),
    entry_points={
        'console_scripts': [
            'pcmc = pcmc.cli:main.start'
        ]
    },
    url=pcmc.__site__,
    license=pcmc.__license__,
    author=pcmc.__author__,
    author_email=pcmc.__email__,
    description=pcmc.__description__,
    keywords=pcmc.__keywords__,
    classifiers=classifiers,
    install_requires=['requests', 'tabulate', 'pandas', 'ccxt', 'begins'],
    dependency_links=['https://github.com/havocesp/cryptocmp.git@0.1.1']

)
