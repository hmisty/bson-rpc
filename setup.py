#!/usr/bin/env python

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

from distutils.core import setup

VERSION = "0.9.1"
URLBASE = "https://github.com/hmisty/bson-rpc/"
URLMAP = {
		"daily": "tarball/master",
		"1.1": "tarball/1.1",
		}

if __name__ == "__main__":
	setup(
			name='bson-rpc',
			version=VERSION,
			description='a lightweight, high performance, multilingual RPC library',
			author='Evan Liu (hmisty)',
			author_email='hmisty@gmail.com',
			url=URLBASE,
			download_url='/'.join([URLBASE, URLMAP.get(VERSION, URLMAP['daily'])]),
			packages=[
				'bson_rpc'
				],
			scripts=[],
			license= 'MIT',
			keywords = ['BSON', 'bson-rpc', 'brpc', 'rpc'],
			classifiers = [
				'Development Status :: 4 - Beta',
				'Topic :: Internet',
				'Environment :: No Input/Output (Daemon)',
				'Intended Audience :: Developers',
				'License :: OSI Approved :: MIT License',
				'Operating System :: OS Independent',
				'Programming Language :: Python :: 2.7',
				'Topic :: Software Development :: Libraries :: Python Modules',
				]
			)
