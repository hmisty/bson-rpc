__version = (0, 0, 1)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc_service', 'start_server']

import rpc_server
rpc_service = rpc_server.rpc_service
start_server = rpc_server.start_server

import rpc_client
connect = rpc_client.connect

