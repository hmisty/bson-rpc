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


class Settings:
    _ = {
        'host': '127.0.0.1',
        'port': 8181,
        'n_workers': 2,
        'home_dir': '/tmp',
        'umask': 022,
        'pid_file': '/var/run/bson-rpc.pid',
        'log_file': '/var/log/bson-rpc.out',
        'err_file': '/var/log/bson-rpc.err',
        'sock_file': '/tmp/bson-rpc.sock', # for ipc with daemon process
    }

    def __repr__(self):
        return repr(self._)

    def __getattr__(self, name):
        return self._[name]

    def __setattr__(self, name, value):
        self._[name] = value

    def update(self, settings):
        self._.update(settings)

# use the instance
settings = Settings()

