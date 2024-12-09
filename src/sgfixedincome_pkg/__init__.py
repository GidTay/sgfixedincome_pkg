# __init__.py
"""
A python package to aggregate and analyse data on 
SGD-denominated retail fixed income products in Singapore.
"""

# read version from installed package
from importlib.metadata import version
__version__ = version("sgfixedincome_pkg")

# import all functions
from .analysis import *
from .consolidate import *
from .equations import *
from .mas_api_client import *
from .scraper import *

