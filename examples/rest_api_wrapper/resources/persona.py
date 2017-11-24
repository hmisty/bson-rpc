#!/usr/bin/env python
#encoding:utf-8

import json
import falcon

class PersonaRest(object):

  def __init__(self, rpc):
    self._rpc = rpc

  def on_get(self, req, resp):
    """
    on get image
    """
    print("get persona info")
    # 1. get request query param: uid
    uid = req.get_param('uid') or '' # '53d207bb2c4b9e6b3f97d0d5'
    print("uid is %s" % uid)
    # 2. get rpc data
    err, res = self._rpc.get_persona_with_user_identifier(uid)
    print("end of get rpc")
    # 3. send http reponse
    if err == 0:
      print("Get Persona OK")
      resp.set_header('Powered-By', 'JuliyeTech')
      resp.body = json.dumps(res, ensure_ascii=False)
      resp.status = falcon.HTTP_200
    else:
      print("Get Persona Error!!")
      resp.set_header('Powered-By', 'JuliyeTech')
      resp.body = json.dumps({"Error": err}, ensure_ascii=False)
      resp.status = falcon.HTTP_500
    return


