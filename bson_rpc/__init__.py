__version = (0, 0, 1)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc_service', 'start_server']

import rpc
rpc_service = rpc.rpc_service
start_server = rpc.start_server
