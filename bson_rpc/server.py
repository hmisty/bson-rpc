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
import socket
import select
import Queue
import bson

from . import status

# the global function map that remotely callable
remote_functions = dict()

def rpc(func, name=None):
    """ add a function to remote callable function map.

    use as function

    >>> rpc(lambda s: s, name="echo")

    or use as decorator

    >>> @rpc
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

def route(obj):
    response = None
    # obj is a bson obj received from a socket
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
                response['result'] = result
            except Exception as error:
                response = status.invoke_error
                response['error_msg'] = str(error)
        else:
            response = status.function_not_found

    return response

def select_on(server):
    inputs = [server] # sockets to read
    outputs = [] # sockets to write
    message_queues = {} # socket message queue
    timeout = 20

    while inputs:
        readable , writable , exceptional = select.select(inputs, outputs, inputs, timeout)

        if not (readable or writable or exceptional): # timeout will generate three empty lists
            print("time out! ")
            break;

        for sock in readable:
            if sock is server:
                conn, addr = sock.accept()
                print('%s:%s connected' % addr)
                conn.setblocking(False)
                inputs.append(conn)
                message_queues[conn] = Queue.Queue()
            else: # sock is a conn
                obj = sock.recvobj()
                if not obj:
                    # treat empty message as closed connection
                    print('%s:%s disconnected' % addr)
                    if sock in outputs:
                        outputs.remove(sock)

                    inputs.remove(sock)
                    sock.close()
                    del message_queues[sock]
                else:
                    response = route(obj)
                    if response:
                        message_queues[sock].put(response)

                    if sock not in outputs:
                        outputs.append(sock)

        for sock in writable:
            try:
                obj = message_queues[sock].get_nowait()
            except Queue.Empty:
                #print('%s:%s queue empty' % sock.getpeername())
                outputs.remove(sock)
            else:
                sock.sendobj(obj)

        for sock in exceptional:
            print('%s:%s exception' % sock.getpeername())
            if sock in outputs:
                outputs.remove(sock)

            inputs.remove(sock)
            sock.close()
            del message_queues[sock]

def start(host, port):
    bson.patch_socket()

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setblocking(False)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
    server.bind((host, port))
    server.listen(5) # allow max 5 in waiting list

    try:
        while True: # loop forever
            select_on(server)
    except KeyboardInterrupt:
        exit()
