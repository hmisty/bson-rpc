# Spec of bson-rpc microservice framework

## Design principles

1. F-a-a-S (function as a service).
2. Embedded library, instead of a stand-alone service for greatly lowering the ops effort. Very simple and easy to use.
3. Light-weight. Native language implementations, no extra wrapper layers and compilation effort.
4. High reliability and high availability.
5. Optimized for high performance (max qps, query per second) instead of concurrent connections. Aim for inter-cloud micro-service frameworking, not for directly serving Internet end-users.
6. Support multiple languages, in separate git repositories.

## Features and current implementations

* Client

| **ID** | **Feature** | **Python** | **Nodejs** |
|------|-----------|----------|----------|
| 1 | Persistent TCP connection | Yes | Yes |
| 2 | BSON object send & receive over persistent TCP connection | Yes | Yes |
| 3 | Auto-restart / auto-reconnect | In-process auto-reconnect | Crash when disconnect and rely on supervisor to restart |
| 4 | connect mode: local | No | Yes |
| 5 | connect mode: standalone | Yes | Yes |
| 6 | connect mode: stand-by | No | Yes |
| 7 | connect mode: load balance | No | Yes |

* Server

| **ID** | **Feature** | **Python** | **Nodejs** |
|------|-----------|----------|----------|
| 1 | Persistent TCP connection | Yes | Yes |
| 2 | BSON object send & receive over persistent TCP connection | Yes | Yes |
| 3 | Event-driven concurrency | Yes | Yes |
| 4 | Daemon-worker model | Yes | No, rely on supervisor to manage |
| 5 | Auto-reconnect when DB recovered | Yes, return error 402 when DB disconnected and re-connect when recovered | ? |

## Protocol

* Payload data structure: BSON binary object

```
+---+---+---+---+--------------------+
| 0 | 1 | 2 | 3 | message length - 4 | => full message to be parsed
+---+---+---+---+--------------------+
 \------v------/ 
4-bytes little endian integer = message length
```

* Function call

Client Request: 
```
{'fn': function_name::String, 'args': list_of_arguments::BSON Array}::BSON
```

Server Reply:
```
{'error_code': 0, 'result': result::BSON}::BSON, when succeeded;
{'error_code': error_code::Integer, 'error_msg': error_message::String}::BSON, when failed.
```

* Special function

| **function name** | **arguments** | **description** | **result** |
|-------------------|---------------|----------------|------------|
| \_\_stats\_\_ | None | Get function call statistics | { function_name::String : \[ num_of_calls::Integer, milliseconds_cost::Integer \], ... }::BSON |

* Error codes

| **error code** | **error message** | **description** |
|----------------|-------------------|-----------------|
| 0 | success | success |
| 401 | unknown message | unknown message |
| 402 | the Error catched when invoking the function | invoke error |
| 404 | function not found | function not found |
| 405 | function not callable | function not callable |
| 501 | connection error | connection error |

## APIs

APIs are described in pseudo codes. Refer to de facto implementation in different languages for real API definitions.

### Client APIs

* Proxy initialization

Pseudo code:
```
proxy = new Client() //LOCAL MODE. to connect to 127.0.0.1:8181
proxy = new Client('x.x.x.x', 8181) //STAND-ALONE MODE. to connect to x.x.x.x:8181
proxy = new Client('master', 'stand-by', 8181) //STAND-BY MODE. to connect to master:8181,
                                               //auto fail-over to stand-by:8181 if failed
proxy = new Client(['host-1', 'host-2', 'host-3', ...], 8181) //LOAD-BALANCE MODE.
                   //to randomly connect to a host, try another if failed until no more host to try
```

* Set proxy connection failure mode

Pseudo code:
```
proxy.die_on_failure(false); //just throw Error on connection failure for caller code to catch and handle
//default true, which will crash the process and replying on top-tier supervisor to restart it
```

* Explicitly propose remote functions to call

Pseudo code:
```
proxy.use_service(['function-name-1', 'function-name-2', 'function-name-3', ...])
```

* Connect to server

Pseudo code:
```
proxy.connect()
```

* Fire a remote function call

Pseudo code:
```
err, result = proxy.function-name-1(arguments) //in sync mode
proxy.function-name-1(arguments).then(function-handler) //in async mode
```

* Disconnect from server

We never do that because we use persistent connection.

### Server APIs

* Server initialization

Pseudo code:
```
server = new Server('x.x.x.x', 8181) //to listen x.x.x.x:8181
```

* Function declaration as remotely callable

Pseudo code:
```
Decorator style:

@rpc
def function-name-1(arguments)

Appender style:

server['function-name-1'] = function definition
```

* start server

Pseudo code:
```
server.start_foreground() //on foreground for dev mode
server.start_background() //like a daemon
```

### Server APIs

## Deployment architecture

* Node client:

```
Supervisor: PM2
Worker: node
```

* Python server:

```
Tier-2 daemon: systemd
Tier-1 daemon: bson-rpc daemonize
Worker: python
```

## References

