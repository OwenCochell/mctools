import importlib.metadata

# Import mclient

from mctools.mclient import RCONClient, QUERYClient, PINGClient

# Define some metadata here:

__version__ = importlib.metadata.version("mctools")
__author__ = 'Owen Cochell'
