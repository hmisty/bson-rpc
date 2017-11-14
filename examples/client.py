#!/usr/bin/env python
#encoding:utf-8

"""
How to run:
    $ python examples/client.py
"""

from bson_rpc import connect

if __name__ == '__main__':
    #conn = connect() # LOCAL
    #conn = connect('127.0.0.1') # STAND-ALONE
    #conn = connect('127.0.0.1', 8181) # STAND-ALONE
    #conn = connect('10.0.0.1', '127.0.0.1', 8181) # STAND-BY
    conn = connect(['10.0.0.1', '10.0.0.2', '127.0.0.1', '10.0.0.3']) # LOAD-BALANCE
    #conn = connect(['10.0.0.1', '10.0.0.2', '127.0.0.1', '10.0.0.3'], 8181) # LOAD-BALANCE
    #conn = connect('ipc:///tmp/bson_rpc')
    #print('connected to server %s' % host)

    conn.use_service(['add', 'echo']);

    err, res = conn.add(1,2)
    print('result: %s' % str(res))

    err, res = conn.echo('你好')
    print('result: %s' % str(res))

    err, res = conn.__stats__()
    print('result: %s' % str(res))

    conn.disconnect();
    #print('disconnected from server %s' % host)
