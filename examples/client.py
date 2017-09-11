#encoding:utf-8
#!/usr/bin/env python

"""
How to run:
    $ cat examples/client.py | python
"""

print __name__
print __package__

from bson_rpc.client import connect

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181

    conn = connect(host, port)
    print('connected to server %s' % host)

    conn.use_service(['hi', 'echo', 'add']);

    err, res = conn.hi()
    print('result: %s' % str(res))

    err, res = conn.echo('你好')
    print('result: %s' % str(res))

    err, res = conn.add(1,2)
    print('result: %s' % str(res))

    conn.disconnect();
    print('disconnected from server %s' % host)
