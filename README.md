# bson-rpc
a lightweight, high performance, multilingual RPC library

## Design Principle

1. f-a-a-s (function as a service).
2. optimized for max qps (query per second) instead of concurrent connections.
3. aim to support multiple languages, in separate git repositories.

# Variable Naming Philosophy

* fn, f, func, function, service, args

* remote\_\_, rpc\_


## Install

	pip install git+https://github.com/hmisty/bson-rpc.git

test

	python -m bson_rpc.example_server

```
from bson_rpc.client import connect
s1 = connect('127.0.0.1', 8181)
s2 = connect('127.0.0.1', 8181)
s1.remote__hi()
s1.remote__echo('hello bson-rpc')
s1.remote__add(1,2)
s2.remote__hi()
s1.close()
s2.remote__echo('i am still alive')
s2.close()
```

## Other Languages

nodejs: https://github.com/hmisty/bson-rpc-nodejs

## Author and Contributors

Author: Evan Liu (hmisty).

## License
Copyright (c) 2017 Evan Liu (hmisty). MIT License.
