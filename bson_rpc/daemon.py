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

from .config import settings
from .server import Server

# the global workers pid list
# for checking/stopping workers
workers = []

"""
get daemon pid
"""
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

"""
delete daemon pid file
"""
def del_pid():
    if os.path.exists(settings.pid_file):
        os.remove(settings.pid_file)

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

    os.chdir(settings.home_dir)
    os.setsid()
    os.umask(settings.umask)

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
    so = file(settings.log_file, 'a+', 0)
    se = file(settings.err_file, 'a+', 0)

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
    file(settings.pid_file, 'w+', 0).write('%s\n' % pid)

    print ('daemon pid_file(%s) created' % settings.pid_file)


"""
exported
"""
def start(host, port, local_settings={}):
    settings.update(local_settings)
    print('starting ...')

    # daemonize the parent
    # * status workers
    # * start/stop/restart a worker
    # * auto-restart if a worker dies
    pid = daemon.get_pid()
    if pid:
        sys.stderr.write('%s already running' % pid)
        sys.exit(1)
    else:
        daemon.daemonize()

        server = Server(host, port)
        for i in range(settings.n_workers):
            pid = os.fork()

            if pid:
                # in parent process
                daemon.workers.append(pid)
            else:
                # fork pid == 0, in child process
                server.pid = os.getpid() # save worker's pid
                server.start_forever()
                sys.exit(1)

        print(daemon.workers)
        print('started!')

        # daemon process entering event loop
        n_sheeps = 0
        while True:
            n_sheeps += 1
            time.sleep(1)
            print('daemon is counting sheeps(%s)' % n_sheeps)


"""
exported
"""
def stop(local_settings={}):
    settings.update(local_settings)
    print('stopping all workers ...')

    pid = daemon.get_pid()
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
        err = str(err)
        if err.find('No such process') > 0:
            pid_file = settings.pid_file
            if os.path.exists(pid_file):
                os.remove(pid_file)
            else:
                print(str(err))
                sys.exit(1)

    # and kill all the workers
    for pid in daemon.workers:
        try:
            os.kill(pid, signal.SIGTERM)
        except:
            pass

    print('stopped!')

"""
exported
"""
def status(local_settings={}):
    settings.update(local_settings)

    pid = daemon.get_pid()
    pids = {
        '%s(guard)' % pid: pid,
    }
    pids.update(dict([('%s(worker)' % w,w) for w in daemon.workers]))

    for k, p in pids.items():
        if p and os.path.exists('/proc/%d' % p):
            pids[k] = 'running'
        else:
            pids[k] = 'dead'

    print(pids)


