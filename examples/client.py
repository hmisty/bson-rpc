#!/usr/bin/env python
#encoding:utf-8

"""
How to run:
    $ python examples/client.py
"""

from bson_rpc import connect

if __name__ == '__main__':
    #proxy = connect() # LOCAL
    #proxy = connect('127.0.0.1') # STAND-ALONE
    #proxy = connect('127.0.0.1', 8181) # STAND-ALONE
    #proxy = connect('10.0.0.1', '127.0.0.1', 8181) # STAND-BY
    proxy = connect(['10.0.0.1', '10.0.0.2', '127.0.0.1', '10.0.0.3']) # LOAD-BALANCE
    #proxy = connect(['10.0.0.1', '10.0.0.2', '127.0.0.1', '10.0.0.3'], 8181) # LOAD-BALANCE
    #proxy = connect('ipc:///tmp/bson_rpc')
    #print('proxyected to server %s' % host)

    proxy.use_service(['add', 'echo']);

    err, res = proxy.add(1,2)
    print('result: %s' % str(res))

    err, res = proxy.echo('你好')
    print('result: %s' % str(res))

    err, res = proxy.__stats__()
    print('result: %s' % str(res))

    proxy.disconnect();
    #print('disproxyected from server %s' % host)
