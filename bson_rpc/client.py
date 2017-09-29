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

class Proxy:
    def __init__(self, host=None, port=None):
        bson.patch_socket()
        if host != None and port != None:
            self.connect(host, port)

    def connect(self, host, port):
        self.sock = socket()
        self.sock.connect((host, port))

    def use_service(self, namelist):
        namelist.append('__stats__')
        for name in namelist:
            f = self.invoke_func(name);
            setattr(self, name, f);

    def invoke_func(self, name):
        def invoke_remote_func(*args, **kwargs):
            self.sock.sendobj({'fn': name, 'args': list(args)})
            doc = self.sock.recvobj()
            err = doc['error_code']
            if (err == 0):
                result = doc['result']
            else:
                result = doc['error_msg']
            return err, result

        return invoke_remote_func

    def disconnect(self):
        self.sock.close()
        self.sock = None

def connect(host, port):
    proxy = Proxy(host, port)
    return proxy

