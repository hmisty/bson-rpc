#encoding:utf-8
#!/usr/bin/env python

"""
How to run:
    $ cat examples/client.py | python
"""

from bson_rpc import connect

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181

    #conn = connect(host, port)
    conn = connect('ipc:///tmp/bson_rpc')
    print('connected to server %s' % host)

    conn.use_service(['add']);

    err, res = conn.add(1,2)
    print('result: %s' % str(res))

    conn.disconnect();
    print('disconnected from server %s' % host)
