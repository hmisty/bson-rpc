#!/usr/bin/env python
#encoding:utf-8
#
#

import httplib

HOST = 'localhost'
PORT = 3000

def mock_persona_req():
  conn = httplib.HTTPConnection(HOST, PORT)
  conn.request('GET', '/persona')
  res = conn.getresponse()
  print("Status: %s %s" % (res.status,res.reason))
  data = res.read().encode('utf-8')
  # encode('utf-8').decode('latin-1')
  print("Data: %s" % data)
  return data


mock_persona_req()

