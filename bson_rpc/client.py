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
from socket import socket
import bson
import os
import random

from common import connection_mode

class Proxy:

    # init some default setup
    def __init_defaults__(self):
        self.DIE_ON_FAILURE = True
        self.connection_mode = connection_mode.LOCAL
        self.hosts = ['127.0.0.1']
        self.port = 8181

        bson.patch_socket()

    # init
    def __init__(self, *args):
        self.__init_defaults__()

        if len(args) == 3: 
            # master, standby, port
            print('use STAND_BY mode')
            self.connection_mode = connection_mode.STAND_BY
            self.hosts = list(args[0:2])
            self.port = args[2]
        elif len(args) == 2 or len(args) == 1:
            print(type(args[0]))
            print(args[0])
            if isinstance(args[0], str): # str == <type 'str'> 
                # host, port
                print('use STAND_ALONE mode')
                self.connection_mode = connection_mode.STAND_ALONE
                self.hosts = list(args[0:1])
                self.port = args[1] if len(args) > 1 else self.port
            elif isinstance(args[0], list): 
                # [host], port
                print('use LOAD_BALANCE mode')
                self.connection_mode = connection_mode.LOAD_BALANCE
                self.hosts = list(args[0])
                self.port = args[1] if len(args) > 1 else self.port
            else:
                print('incorrect type of host(s)')
                pass
        else:
            print('use LOCAL mode by default')
            pass

    # connect
    def connect(self):
        if self.connection_mode == connection_mode.LOCAL or self.connection_mode == connection_mode.STAND_ALONE:
            pair = (self.hosts[0], self.port)
            print('trying to connect %s:%s in %s mode' % (pair + (self.connection_mode,)))
            try:
                self.sock = socket()
                self.sock.settimeout(1) # fail asap after 1 sec
                self.sock.connect(pair)
                print('connected')
            except Exception, e:
                self.sock.close()
                self.sock = None
                self.fail(repr(e))

        elif self.connection_mode == connection_mode.STAND_BY:
            for host in self.hosts:
                pair = (host, self.port)
                print('trying to connect %s:%s in %s mode' % (pair + (self.connection_mode,)))
                try:
                    self.sock = socket()
                    self.sock.settimeout(1) # fail asap after 1 sec
                    self.sock.connect(pair)
                    print('connected')
                    break
                except Exception, e:
                    self.sock.close()
                    self.sock = None
                    print('failed: ' + repr(e))
                    pass
            
            if self.sock == None:
                self.fail('all failed')

        elif self.connection_mode == connection_mode.LOAD_BALANCE:
            hosts = self.hosts
            
            while len(hosts) > 0:
                host = random.choice(hosts)
                hosts.remove(host)
                pair = (host, self.port)
                print('trying to connect %s:%s in %s mode' % (pair + (self.connection_mode,)))
                try:
                    self.sock = socket()
                    self.sock.settimeout(1) # fail asap after 1 sec
                    self.sock.connect(pair)
                    print('connected')
                    break
                except Exception, e:
                    self.sock.close()
                    self.sock = None
                    print('failed: ' + repr(e))
                    pass
            
            if self.sock == None:
                self.fail('all failed')

    # use some services
    def use_service(self, namelist):
        namelist.append('__stats__')
        for name in namelist:
            f = self.invoke_func(name);
            setattr(self, name, f);

    # invoke a function
    def invoke_func(self, name):
        def invoke_remote_func(*args, **kwargs):
            try:
                self.sock.sendobj({'fn': name, 'args': list(args)})
                doc = self.sock.recvobj()
                err = doc['error_code']
            except Exception, e:
                self.sock.close()
                self.sock = None
                self.fail(repr(e))
            else:
                # reaches here if no exception
                if (err == 0):
                    result = doc['result']
                else:
                    result = doc['error_msg']

                return err, result

        return invoke_remote_func

    # client disconnect
    def disconnect(self):
        self.sock.close()
        self.sock = None
        self.fail('client disconnect explicitly')

    # Set DOF value, True by default
    def die_on_failure(self, dof=True):
        self.DIE_ON_FAILURE = dof

    # Fail the process
    def fail(self, error_msg = None):
        if self.DIE_ON_FAILURE:
            print('Die-On-Failure: ', error_msg)
            os._exit(1)
        else:
            raise Exception(error_msg)

# Helper function.
# Equivalent to,
# from bson_rpc import client
# proxy = client.Proxy(host, port)
def connect(*args):
    proxy = Proxy(*args)
    proxy.connect()
    return proxy

