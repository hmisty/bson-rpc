#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Authorization(object):
  def process_request(self, req, resp):
    # TODO some monitor process
    print('Come into authorization')
