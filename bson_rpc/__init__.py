__version = (0, 6, 0)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc', 'start_server']

import server as server
rpc = server.rpc
start_server = server.start
stop_server = server.stop
server_status = server.status

import client as client
connect = client.connect

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

