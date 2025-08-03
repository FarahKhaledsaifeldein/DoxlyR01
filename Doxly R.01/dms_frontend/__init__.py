"""DMS Frontend Package

This package contains the frontend components and utilities for the DMS (Document Management System).
"""

__version__ = '0.1.0'
__author__ = 'Doxly Team'

# Import essential subpackages
from . import api
from . import ui
from . import utils

# Define package-level exports
__all__ = ['api', 'ui', 'utils']