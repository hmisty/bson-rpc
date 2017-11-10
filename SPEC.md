# Specification of bson-rpc microservice framework

## Design objectives

## Features and current implementations

* Client

| *ID* | *Feature* | *Python* | *Nodejs* |
|------|-----------|----------|----------|
| 1 | Persistent TCP connection | Yes | Yes |
| 2 | BSON object send & receive over persistent TCP connection | Yes | Yes |
| 3 | Auto-restart / auto-reconnect | In-process auto-reconnect | Die when disconnect and rely on supervisor to restart |
| 4 | connect mode: local | No | Yes |
| 5 | connect mode: standalone | Yes | Yes |
| 6 | connect mode: stand-by | No | Yes |
| 7 | connect mode: load balance | No | Yes |

* Server

| *ID* | *Feature* | *Python* | *Nodejs* |
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

+-----------------+-------------+---------------+----------+
| *function name* | *arguments* | *description* | *result* |
+-----------------+-------------+---------------+----------+
| \__stats__ | None | Get function call statistics | { function_name::String : \[ num_of_calls::Integer, milliseconds_cost::Integer ], ... }::BSON |

* Error codes

+--------------+-----------------+---------------+
| *error code* | *error message* | *description* |
+--------------+-----------------+---------------+
| 0 | success | success |
| 401 | unknown message | unknown message |
| 402 | the Error catched when invoking the function | invoke error |
| 404 | function not found | function not found |
| 405 | function not callable | function not callable |
| 501 | connection error | connection error |

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

