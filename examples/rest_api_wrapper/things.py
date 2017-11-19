#!/usr/bin/env python
#encoding:utf-8

import falcon

class ThingsREST(object):
  def on_get(self, req, resp):
    """ Handle get request  """
    resp.status = falcon.HTTP_200
    resp.body = ('hello falcon!! \n'
        'it\'s really nice to meet you! \n'
        '   ~ lulucky')

app = falcon.API()
things = ThingsREST()
app.add_route('/things', things)
