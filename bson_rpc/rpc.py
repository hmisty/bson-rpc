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

# the global function map that remotely callable
services = dict()

def rpc_service(func, name=None):
    """ add a function to remote callable service map.

    use as function

    >>> rpc_service(lambda s: s, name="echo")

    or use as decorator

    >>> @rpc_service
        def echo(s):
            return s

    """
    global services
    services[name or func.__name__] = func
    return func

def rpc_router(socket, address):
    print('%s:%s connected' % address)

    while True:
        obj = socket.recvobj()

        if obj != None:
            if obj.has_key('service'):
                func = obj['service']
                print("call %s" % func)
                socket.sendobj({func: 'ok'})
            else: # by default be an echo service
                print("echo")
                socket.sendobj(obj)

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

