#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Accounting(object):
  def process_request(self, req, resp):
    # TODO some monitor process
    print('Come into accounting')
    print('host : %s' % req.host) #req.get_header("Host"))
    print('port : %s' % req.port) #req.get_header("Port"))
    print('method : %s' % req.method) #req.get_header("Port"))
    print('uri : %s' % req.uri) #req.get_header("Port"))
    print('headers : %s' % req.headers) #req.get_header("Port"))


