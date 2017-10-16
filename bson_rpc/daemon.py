# MIT License
#
# Copyright (c) 2017 Evan Liu (hmisty@gmail.com)
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

from .config import settings
from .server import Server

# global daemon running
keep_running = False

# the global workers pid list
# for checking/stopping workers
workers = []

# get daemon pid
def get_pid():
    try:
        pf = file(settings.pid_file, 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None
    except SystemExit:
        pid = None

    return pid

# delete daemon pid file
def del_pid():
    if os.path.exists(settings.pid_file):
        os.remove(settings.pid_file)

# check if a pid is alive
def is_pid_alive(pid):
    try:
        os.kill(pid, 0)
    except:
        return False
    else:
        return True

# daemonize
def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print('fork1 failed', repr(e))
        sys.exit(1)

    os.chdir(settings.home_dir)
    os.setsid()
    os.umask(settings.umask)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print('fork2 failed', repr(e))
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

    si = file(os.devnull, 'r')
    so = file(settings.log_file, 'a+', 0)
    se = file(settings.err_file, 'a+', 0)

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    def exit_handler(signum, frame):
        global keep_running
        keep_running = False
        print('daemon exiting ...')

    signal.signal(signal.SIGTERM, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)

    def child_exit_handler(signum, frame):
        print('a child exit')

    signal.signal(signal.SIGCHLD, child_exit_handler)

    print('daemon process started ...')

    atexit.register(del_pid)
    pid = str(os.getpid())
    file(settings.pid_file, 'w+', 0).write('%s\n' % pid)

    print ('daemon pid_file(%s) created' % settings.pid_file)

# exported
def setup(local_settings):
    settings.update(local_settings)

# exported
def start(local_settings={}):
    settings.update(local_settings)
    print('starting ...')

    # daemonize the parent
    # * status workers
    # * start/stop/restart a worker
    # * auto-restart if a worker dies TODO
    pid = get_pid()
    if pid:
        sys.stderr.write('%s already running\n' % pid)
        sys.exit(1)
    else:
        daemonize()

        host = settings.host
        port = settings.port
        server = Server(host, port)
        for i in range(settings.n_workers):
            pid = os.fork()

            if pid:
                # in parent process
                workers.append(pid)
            else:
                # fork pid == 0, in child process
                server.pid = os.getpid() # save worker's pid
                try:
                    server.start_forever()
                except select.error, e:
                    print('server quit running... ', repr(e))
                    sys.exit(1)

        print(workers)
        print('started!')

        # daemon process entering event loop
        global keep_running
        keep_running = True

        try:
            os.unlink(settings.sock_file)
        except OSError:
            if os.path.exists(settings.sock_file):
                raise

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(settings.sock_file)
        sock.listen(1)

        while keep_running:
            try:
                conn, addr = sock.accept()

                buf_size = 1024
                request = conn.recv(buf_size)

                if request == 'workers':
                    conn.sendall(','.join([str(w) for w in workers]))
                else:
                    conn.sendall('unknown request: %s ' % request)

                conn.close()
            except socket.error, e:
                print(repr(e))

        # daemon entering exiting process

        print('stopping all workers ...')

        # kill all the workers
        for pid in workers:
            try:
                #os.kill(pid, signal.SIGTERM)
                os.kill(pid, signal.SIGKILL)
            except OSError, err:
                err = repr(err)
                print(err)
                pass

        print('stopped!')


"""
exported
"""
def stop(local_settings={}):
    settings.update(local_settings)
    print('stopping...')

    pid = get_pid()
    if not pid:
        pid_file = settings.pid_file
        msg = 'pid file [%s] does not exist. Not running?\n' % pid_file
        sys.stderr.write(msg)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        return

    #try to kill the daemon process
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError, err:
        err = repr(err)
        print(err)
        if err.find('No such process') > 0:
            pid_file = settings.pid_file
            if os.path.exists(pid_file):
                os.remove(pid_file)
            else:
                print(repr(err))
                sys.exit(1)


# exported
def status(local_settings={}):
    settings.update(local_settings)

    pid = get_pid()
    pids = {
        '%s(daemon)' % pid: pid,
    }

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(settings.sock_file)
    sock.sendall('workers')
    buf_size = 1024
    workers = sock.recv(buf_size)
    sock.close()

    worker_list = workers.split(',')
    pids.update(dict([('%s(worker)' % w, int(w)) for w in worker_list]))

    for k, p in pids.items():
        if p and is_pid_alive(p):
            pids[k] = 'running'
        else:
            pids[k] = 'dead'

    print(pids)


