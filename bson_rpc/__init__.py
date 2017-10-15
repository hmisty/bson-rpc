__version = (0, 6, 0)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc', 'start_server']

import server
rpc = server.rpc
start_server = server.start_server

import client
connect = client.connect

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

