# MIT License
#
# Copyright (c) 2017 Evan Liu (hmisty)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function
from gevent.server import StreamServer
import bson

from . import status

# the global function map that remotely callable
remote_functions = dict()

def remote__(func, name=None):
    """ add a function to remote callable function map.

    use as function

    >>> remote__(lambda s: s, name="echo")

    or use as decorator

    >>> @remote__
        def echo(s):
            return s

    """
    global remote_functions
    remote_functions[name or func.__name__] = func
    return func

def invoke_func(fn, args):
    global remote_functions

    if not remote_functions.has_key(fn):
        return status.function_not_found

    f = remote_functions[fn]
    if not callable(f):
        return status.function_not_callable

    if args == None:
        result = f()
    else:
        result = f(*args)

    return result

def rpc_router(socket, address):
    print('%s:%s connected' % address)

    while True:
        obj = socket.recvobj()

        if obj != None:
            if obj.has_key('fn'):
                fn = obj['fn']

                if obj.has_key('args'):
                    args = obj['args']
                else:
                    args = None

                print("call %s" % fn)
                try:
                    result = invoke_func(fn, args)
                    response = status.ok
                    response['data'] = result
                except Exception as error:
                    response = status.invoke_error
                    response['error_msg'] = str(error)
                finally:
                    socket.sendobj(response)
            else:
                socket.sendobj(status.function_not_found)

    socket.close()

def patch_socket():
    from gevent.server import socket
    from bson.network import recvbytes, recvobj, sendobj
    socket.recvbytes = recvbytes
    socket.recvobj = recvobj
    socket.sendobj = sendobj

def start_server(host, port):
    patch_socket()
    server = StreamServer((host, port), rpc_router)
    server.serve_forever()

