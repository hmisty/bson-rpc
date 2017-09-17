#!/usr/bin/env python
"""
How to run:
    $ cat examples/server.py | python
"""

import time
from bson_rpc import rpc, start_server

@rpc
def add(a, b):
    #time.sleep(5.0) # would block all
    return a + b

def main(host, port):
    start_server(host, port)
    #start_server('ipc:///tmp/bson_rpc')

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181
    main(host, port)

