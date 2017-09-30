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
import time
import socket
import select
import Queue
import bson

from . import status

# the global function map that remotely callable
# { fn: [func, invoke_count, accumulated_time] }
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
    remote_functions[name or func.__name__] = [func, 0, 0]
    return func

@rpc
def __stats__():
    rf = remote_functions
    stats = {}
    total_count = 0
    total_time = 0
    for fn in remote_functions:
        count = remote_functions[fn][1]
        time = remote_functions[fn][2]
        stats[fn] = [count, time]
        total_count += count
        total_time += time

    stats['*'] = [total_count, total_time]

    return stats

def invoke_func(fn, args=None):
    global remote_functions

    if fn is None:
        return status.function_not_found.copy()

    if not remote_functions.has_key(fn):
        return status.function_not_found.copy()

    f = remote_functions[fn][0]
    if not callable(f):
        return status.function_not_callable.copy()

    try:
        begin = time.time()

        if args == None:
            result = f()
        else:
            result = f(*args)

        elapsed = time.time() - begin
        elapsed = int(elapsed * 1000) # in milliseconds

        response = status.ok.copy() # copy() before modify!
        response['result'] = result
        response['time'] = elapsed

        remote_functions[fn][1] += 1
        remote_functions[fn][2] += elapsed
    except Exception as error:
        response = status.invoke_error.copy()
        response['error_msg'] = str(error)

    return response

def compute_on(obj):
    response = None

    # obj is a bson obj received from a socket
    if obj != None:
        _id = obj.get('_id') or 0

        fn = obj.get('fn')
        args = obj.get('args')
        response = invoke_func(fn, args)

        response['_id'] = _id

    return response

def log(sock, *args):
    datetime = '%s %s' % (time.ctime(), time.tzname[0])

    try:
        conn_str = '%s:%s' % sock.getpeername()
    except:
        conn_str = 'broken client'

    message = ' '.join(map(lambda x: str(x), args)).replace('\n', '').replace('\r', '')
    print(datetime, conn_str, message.decode('unicode_escape'))

class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.inputs = [self.server] # sockets to read
        self.outputs = [] # sockets to write
        self.message_queues = {} # socket message queue
        self.host = host
        self.port = port

    def start_forever(self, polling_interval=0.5):
        bson.patch_socket()

        server = self.server
        inputs = self.inputs
        outputs = self.outputs
        message_queues = self.message_queues

        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5) # allow max 5 in waiting list
        log(server, 'Listening on', self.host, self.port)

        inputs = self.inputs
        while inputs:
            readable, writable, exceptional = \
                    select.select(inputs, outputs, inputs, polling_interval)

            if not (readable or writable or exceptional):
                # timeout will generate three empty lists
                continue; # loop forever

            self.read_each(readable)
            self.write_each(writable)
            self.catch_each(exceptional)

    def read_each(self, readable):
        server = self.server
        inputs = self.inputs
        outputs = self.outputs
        message_queues = self.message_queues

        for sock in readable:
            if sock is server: # it is the server socket
                conn, addr = sock.accept()
                log(conn, 'CONNECT')
                conn.setblocking(False)
                inputs.append(conn)
                message_queues[conn] = Queue.Queue()
            else: # it is a connection socket
                obj = None
                try:
                    obj = sock.recvobj()
                except Exception as e:
                    log(sock, e)

                if obj:
                    response = compute_on(obj) # caution: would block!
                    log(sock, 'REQUEST', obj)
                    message_queues[sock].put(response)

                    if sock not in outputs:
                        outputs.append(sock)
                    else:
                        pass

                else:
                    # treat empty message as closed connection
                    log(sock, 'DISCONNECT')
                    if sock in outputs:
                        outputs.remove(sock)

                    inputs.remove(sock)
                    sock.close()
                    del message_queues[sock]

    def write_each(self, writable):
        outputs = self.outputs
        message_queues = self.message_queues

        for sock in writable:
            try:
                if (sock in message_queues):
                    obj = message_queues[sock].get_nowait()
                    log(sock, 'REPLY', obj)
                    sock.sendobj(obj)
            except Queue.Empty:
                outputs.remove(sock)
            except socket.error, msg:
                log(sock, 'socket.error', msg)

    def catch_each(self, exceptional):
        inputs = self.inputs
        outputs = self.outputs
        message_queues = self.message_queues

        for sock in exceptional:
            log(sock, 'EXCEPTION')
            if sock in outputs:
                outputs.remove(sock)

            inputs.remove(sock)
            sock.close()
            del message_queues[sock]


def start(host, port):
    server = Server(host, port)

    try:
        server.start_forever()
    except KeyboardInterrupt:
        exit()
