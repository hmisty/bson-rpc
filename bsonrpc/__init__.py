__version = (0, 0, 1)

__version__ = version = '.'.join(map(str, __version))
__project__ = PROJECT = __name__

#__all__ = ['rpc', 'rpc_func']

import rpc
rpc_func = rpc.rpc_func
start_server = rpc.start_server
