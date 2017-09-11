# bson-rpc
a lightweight, high performance, multilingual RPC library

## Design Principle

1. f-a-a-s (function as a service).
2. optimized for max qps (query per second) instead of concurrent connections.
3. aim to support multiple languages, in separate git repositories.

## Install

	pip install git+https://github.com/hmisty/bson-rpc.git

test

	python examples/server2.py

```
from bson_rpc.client import connect
s1 = connect('127.0.0.1', 8181)
s2 = connect('127.0.0.1', 8181)
s1.use_service(['hi', 'echo', 'add'])
s2.use_service(['hi', 'echo'])
s1.hi()
s1.echo('hello bson-rpc')
s1.add(1,2)
s2.hi()
s1.close()
s2.echo('i am still alive')
s2.close()
```

	python examples/client2.py

## Other Languages

nodejs: https://github.com/hmisty/bson-rpc-nodejs

## Author and Contributors

Author: Evan Liu (hmisty).

## License
Copyright (c) 2017 Evan Liu (hmisty). MIT License.
