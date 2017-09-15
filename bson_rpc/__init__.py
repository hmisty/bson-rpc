__version = (0, 5, 2)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc', 'start_server']

import server_zmq
rpc = server_zmq.rpc
start_server = server_zmq.start

import client_zmq
connect = client_zmq.connect

#import sys
#defaultencoding = 'utf-8'
#if sys.getdefaultencoding() != defaultencoding:
#    reload(sys)
#    sys.setdefaultencoding(defaultencoding)
#
