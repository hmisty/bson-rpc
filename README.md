# bson-rpc
a lightweight, high performance, multilingual RPC library

## Design Principle

1. f-a-a-s (function as a service).
2. optimized for max qps (query per second) instead of concurrent connections.
3. aim to support multiple languages, in separate git repositories.

## Install

	pip install bson-rpc

or,

	pip install git+https://github.com/hmisty/bson-rpc.git

## Examples

server.py

```python
from bson_rpc import rpc, start_server

@rpc
def add(a, b):
    return a + b

def main(host, port):
    start_server(host, port)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181
    main(host, port)

```

client.py

```python
from bson_rpc.client import connect

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8181

    conn = connect(host, port)
    print('connected to server %s' % host)

    conn.use_service(['add']);

    err, res = conn.add(1,2)
    print('result: %s' % str(res))

    conn.disconnect();
    print('disconnected from server %s' % host)
```

## Other Languages

nodejs: https://github.com/hmisty/bson-rpc-nodejs

# For Contributors

[Development Guide](DEV_GUIDE.md)

## Author and Contributors

Author: Evan Liu (hmisty).

## License
Copyright (c) 2017 Evan Liu (hmisty). MIT License.
