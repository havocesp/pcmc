from setuptools import setup
from pcmc import __description__, __version__, __site__, __package__, __author__, __licence__

setup(
    name=__package__,
    version=__version__,
    packages=[''],
    package_dir={'': __package__},
    url=__site__,
    license=__licence__,
    author=__author__,
    author_email='',
    description=__description__,
    requires=['pandas', 'html5lib']
)
