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
import os
import sys
import signal
import atexit
import time
import socket
import select
import Queue
import bson

from . import status
from . import config

# the global workers _id list
# for checking/stopping workers
workers = []

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
        response['error_msg'] = repr(error)

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
        conn_str = 'unconnected'

    message = ' '.join(map(lambda x: str(x), args)).replace('\n', '').replace('\r', '')
    print(datetime, conn_str, message.decode('unicode_escape'))

class Server:
    def __init__(self, host, port):
        self._id = 0 # for numbering the workder processes
        self.host = host
        self.port = port

        server = self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5) # allow max 5 in waiting list
        log(server, 'Listening on', self.host, self.port)

        self.inputs = [self.server] # sockets to read
        self.outputs = [] # sockets to write
        self.message_queues = {} # socket message queue

    def start_forever(self, polling_interval=0.5):
        bson.patch_socket()

        server = self.server
        inputs = self.inputs
        outputs = self.outputs
        message_queues = self.message_queues

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
            if sock is server:
                # it is the server socket

                # while trying to accept, we need to handle the "thundering bird" problem
                # because in *nix, all child processes will be waken up to accept
                # only one child can succeed
                # others will fail to accept and go back to loop again
                # be careful not to crash when accept failed
                try:
                    conn, addr = sock.accept()
                except:
                    return

                log(conn, 'CONNECT')
                conn.setblocking(False)
                inputs.append(conn)
                message_queues[conn] = Queue.Queue()

            else:
                # it is a connection socket

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

"""
get daemon pid
"""
def get_pid():
    try:
        pf = file(config.settings['pid_file'], 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None
    except SystemExit:
        pid = None

    return pid

"""
delete daemon pid file
"""
def del_pid():
    if os.path.exists(config.settings['pid_file']):
        os.remove(config.settings['pid_file'])

"""
daemonize
"""
def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    os.chdir(config.settings['home_dir'])
    os.setsid()
    os.umask(config.settings['umask'])

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

    si = file(os.devnull, 'r')
    so = file(config.settings['log_file'], 'a+', 0)
    se = file(config.settings['err_file'], 'a+', 0)

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    def sig_handler(signum, frame):
        print('daemon exiting ...')

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    print('daemon process started ...')

    atexit.register(del_pid)
    pid = str(os.getpid())
    file(config.settings['pid_file'], 'w+').write('%s\n' % pid)

"""
exported as start_server(...)
"""
def start(host, port, n_worker=2, settings={}):
    config.settings.update(settings)
    print('starting ...')

    # daemonize the parent and create a guard process to protect the workers
    # i.e. restart them if they are killed abnormally
    pid = get_pid()
    if pid:
        sys.stderr.write('%s already running' % pid)
        sys.exit(1)
    else:
        daemonize()

        server = Server(host, port)
        global workers
        for i in range(n_worker):
            pid = os.fork()

            if pid:
                # in parent process
                workers.append(pid)
            else:
                # pid == 0, in child process
                server._id = i
                server.start_forever()
                sys.exit(1)

        print(workers)

"""
exported as stop_server(...)
"""
def stop(settings={}):
    config.settings.update(settings)
    print('stopping all workers ...')

    pid = get_pid()
    if not pid:
        pid_file = config.settings['pid_file']
        msg = 'pid file [%s] does not exist. Not running?\n' % pid_file
        sys.stderr.write(msg)
        if os.path.exists(pid_file):
            os.remove(pid_file)
            return
    #try to kill the daemon process
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError, err:
        err = str(err)
        if err.find('No such process') > 0:
            pid_file = config.settings['pid_file']
            if os.path.exists(pid_file):
                os.remove(pid_file)
            else:
                print(str(err))
                sys.exit(1)

    # and kill all the workers
    global workers
    for _id in workers:
        try:
            os.kill(_id, signal.SIGTERM)
        except:
            pass

    print('stopped!')

"""
exported as server_status(...)
"""
def status(settings={}):
    config.settings.update(settings)
    pid = get_pid()
    pids = {
        '%s(guard)' % pid: pid,
    }
    pids.update(dict([('%s(worker)' % w,w) for w in workers]))

    for k, p in pids.items():
        if p and os.path.exists('/proc/%d' % p):
            pids[k] = 'running'
        else:
            pids[k] = 'dead'

    print(pids)
