#!/usr/bin/env python
"""
How to run:
    $ cd examples
    $ ln -s ../bson_rpc .
    $ python server_daemon.py
"""

import sys
import time
from bson_rpc import daemon
from bson_rpc.config import settings
from bson_rpc.server import rpc, Server

N_WORKERS = 2

@rpc
def hi():
    return 'hi'

@rpc
def add(a, b):
    #time.sleep(1.0) # would block all
    return a + b

@rpc
def echo(s):
    return s

def create_main():
    s = Server(settings.host, settings.port)

    def main():
        s.start_forever()

    return main

def start_daemon():
    main = create_main()
    daemon.start(main, N_WORKERS)

if __name__ == '__main__':
    #start_server()
    #sys.exit(0)

    usage = 'Usage: python %s <start|stop|status>' % sys.argv[0]
    if len(sys.argv) < 2:
        print usage
        sys.exit(1)

    if sys.argv[1] == 'start':
        start_daemon()
    elif sys.argv[1] == 'stop':
        daemon.stop()
    elif sys.argv[1] == 'status':
        daemon.status()
    else:
        print usage
        sys.exit(1)

