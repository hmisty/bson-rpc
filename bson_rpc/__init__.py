__version = (0, 9, 1)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

"""
>>> from bson_rpc import rpc, start_server
>>> from bson_rpc import connect
"""
#__all__ = ['rpc', 'start_server', 'connect']

import server
rpc = server.rpc
start_server = server.start

import client
connect = client.connect

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

