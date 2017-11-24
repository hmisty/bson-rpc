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
import psutil
import traceback

from .config import settings

#log
def log(*args, **kwargs):
    pid = os.getpid()
    print(pid, *args, **kwargs)

# get daemon pid
def get_daemon_pid():
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
def del_daemon_pid():
    if os.path.exists(settings.pid_file):
        log('delete daemon pid file %s' % settings.pid_file)
        os.remove(settings.pid_file)

# fork a worker
def start_worker(worker_main_loop):
    pid = os.fork()

    if pid:
        # in parent process
        return pid
    else:
        # fork pid == 0, in child process

        # clear signal hooks
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # start loop
        try:
            worker_main_loop()
        except Exception, e:
            log('worker main loop exit', repr(e))
            sys.exit(1)

# daemonize
def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        log('fork1 failed', repr(e))
        sys.exit(1)

    os.chdir(settings.home_dir)
    os.setsid()
    os.umask(settings.umask)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        log('fork2 failed', repr(e))
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

    si = file(os.devnull, 'r')
    so = file(settings.log_file, 'a+', 0)
    se = file(settings.err_file, 'a+', 0)

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    log('daemon process started')

    #atexit.register(del_daemon_pid) #buggy. child will inherit and del pid file when die
    pid = str(os.getpid())
    file(settings.pid_file, 'w+', 0).write('%s\n' % pid)

    log('daemon pid_file(%s) created' % settings.pid_file)

# quit
def quit_daemon():
    # daemon entering exiting process
    log('stopping all workers ...')

    # kill all the workers
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    pid = os.getpid()
    worker_list = psutil.Process(pid).children()
    for p in worker_list:
        try:
            log('killing %s ...' % p.pid)
            p.kill()
        except OSError, err:
            err = repr(err)
            log(err)
            pass

    del_daemon_pid()

    log('daemon %s exit' % pid)
    sys.exit(0)

# init
def init_daemon():
    # daemonize the parent
    # * status workers
    # * start/stop/restart a worker
    # * auto-restart if a worker dies
    pid = get_daemon_pid()
    if pid:
        log('%s already running' % pid)
        sys.exit(1)
    else:
        daemonize()

# exported
def setup(local_settings):
    settings.update(local_settings)

# exported
def start(worker_main_loop, n_workers=None):
    log('daemon starting...')
    init_daemon()

    if n_workers:
        settings.n_workers = n_workers

    workers = []
    for i in range(settings.n_workers):
        pid = start_worker(worker_main_loop)
        workers.append(pid)

    log('workers', workers, 'started running!')

    # auto-restart child
    def child_exit_handler(signum, frame):
        pid = os.wait()[0]
        log('worker(%s) died. fork a new...' % pid)
        time.sleep(1.0)
        start_worker(worker_main_loop)

    signal.signal(signal.SIGCHLD, child_exit_handler)

    # respond to termination
    def terminate_handler(signum, frame):
        log('daemon being terminated...')
        quit_daemon()

    signal.signal(signal.SIGTERM, terminate_handler)

    def interrupt_handler(signum, frame):
        log('daemon being interrupted...')
        quit_daemon()

    signal.signal(signal.SIGINT, interrupt_handler)

    # forever loop
    log('daemon', os.getpid(), 'started running!')
    while True:
        time.sleep(0.1)

"""
exported
"""
def stop():
    log('daemon stopping...')

    pid = get_daemon_pid()
    if not pid:
        pid_file = settings.pid_file
        msg = 'pid file [%s] does not exist. is it not running?' % pid_file
        log(msg)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        return

    #try to kill the daemon process
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError, err:
        err = repr(err)
        log(err)
        if err.find('No such process') > 0:
            pid_file = settings.pid_file
            if os.path.exists(pid_file):
                os.remove(pid_file)
            else:
                log(repr(err))
                sys.exit(1)


# exported
def status():
    pid = get_daemon_pid()
    if not pid:
        pid_file = settings.pid_file
        msg = 'pid file [%s] does not exist. is it not running?' % pid_file
        print(msg)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        return

    print('status: running')
    print('%s: daemon' % pid)

    worker_list = psutil.Process(pid).children()
    for p in worker_list:
        if psutil.pid_exists(p.pid):
            print('%s: active worker' % p.pid)
        else:
            print('%s: dead worker' % p.pid)

