__version = (0, 0, 1)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['remote__', 'start_server']

import server
remote__ = server.remote__
start_server = server.start_server

import client
connect = client.connect

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

