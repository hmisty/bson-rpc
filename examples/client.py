#!/usr/bin/env python
#encoding:utf-8

"""
How to run:
    $ python examples/client.py
"""

from bson_rpc import connect

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181

    conn = connect(host, port)
    #conn = connect('ipc:///tmp/bson_rpc')
    print('connected to server %s' % host)

    conn.use_service(['add', 'echo']);

    err, res = conn.add(1,2)
    print('result: %s' % str(res))

    err, res = conn.echo('你好')
    print('result: %s' % str(res))

    err, res = conn.__stats__()
    print('result: %s' % str(res))

    conn.disconnect();
    print('disconnected from server %s' % host)
