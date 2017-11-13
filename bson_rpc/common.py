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
"""
enum
"""
def enum(**enums):
    return type('Enum', (), enums)

connection_mode = enum(LOCAL = 'LOCAL',
                       STAND_ALONE = 'STAND_ALONE',
                       STAND_BY = 'STAND_BY',
                       LOAD_BALANCE = 'LOAD_BALANCE')

"""
from common import multimethod

@multimethod(int, int)
def foo(a, b):
    ...

@multimethod(int)
def foo(a):
    return foo(a, 10) # This calls the previous foo()!
"""
registry = {}

class MultiMethod(object):
    def __init__(self, name):
        self.name = name
        self.typemap = {}

    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args) # a generator expression!
        print types
        
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)

    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function

def multimethod(*types):
    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        return mm

    return register

