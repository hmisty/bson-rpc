#!/usr/bin/env python
#encoding:utf-8

import falcon

class ThingsRest(object):
  def on_get(self, req, resp):
    """ Handle get request  """
    resp.status = falcon.HTTP_200
    resp.content_type = falcon.MEDIA_TEXT
    resp.body = ('hello falcon!! \n'
        'it\'s really nice to meet you! \n'
        '   ~ lulucky')
