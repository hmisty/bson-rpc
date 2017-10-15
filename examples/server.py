#!/usr/bin/env python
"""
How to run:
    $ cat examples/server.py | python
"""

import sys
import time
from bson_rpc import rpc, start_server, daemon

@rpc
def add(a, b):
    #time.sleep(1.0) # would block all
    return a + b

@rpc
def echo(s):
    return s

if __name__ == '__main__':
    #start_server()
    #sys.exit(0)

    usage = 'Usage: python %s <start|stop|status>' % sys.argv[0]
    if len(sys.argv) < 2:
        print usage
        sys.exit(1)

    local_settings={
        'n_workers': 1,
        'pid_file': '/tmp/brpc.pid',
        'log_file': '/tmp/brpc.out',
        'err_file': '/tmp/brpc.err',
    }
    daemon.setup(local_settings)

    if sys.argv[1] == 'start':
        daemon.start()
    elif sys.argv[1] == 'stop':
        daemon.stop()
    elif sys.argv[1] == 'status':
        daemon.status()
    else:
        print usage
        sys.exit(1)

