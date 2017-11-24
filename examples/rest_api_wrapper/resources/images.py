#!/usr/bin/env python
#encoding:utf-8

import json
import falcon

import io
import os
import uuid
import mimetypes


DOC = {
        'images': [
          {'id':1, 'name':'baidu', 'href': 'https://www.baidu.com/img/bd_logo1.png'},
          {'id':2, 'name':'test', 'href': 'https://www.baidu.com/img/bd_logo1.png'}
        ]}

class ImageCollection(object):

  _CHUNK_SIZE_BYTES = 4096

  def __init__(self, storage_path):
    self._storage_path = storage_path

  def validate_req_type(req, resp, resource, params):
    types = (
        'application/json',
        )
    if req.content_type not in types :
      msg = 'Req content type must be applicaiton/json'
      raise falcon.HTTPBadRequest('Bad request', msg)

  @falcon.before(validate_req_type)
  def on_get(self, req, resp):
    """
    on get image
    """
    resp.body = json.dumps(DOC, ensure_ascii=False)
    resp.status = falcon.HTTP_200

  def on_post(self, req, resp):
    """
    on post image
    """
    ext = mimetypes.guess_extension(req.content_type)
    name = '{uuid}{ext}'.format(uuid=uuid.uuid4(), ext=ext)
    image_path = os.path.join(self._storage_path, name)

    with io.open(image_path, 'wb') as image_file:
      while True:
        chunk = req.stream.read(self._CHUNK_SIZE_BYTES)
        if not chunk:
          break
        image_file.write(chunk)

    resp.status = falcon.HTTP_201
    resp.location = '/images/' + name

class ImageItem(object):
  def on_get(self, req, resp, _id):
    """
    on get single image
    """
    print("the id is : %s" % _id)
    try:
      doc = DOC["images"][int(_id)]
    except IndexError:
      raise falcon.HTTPNotFound()
    except ValueError:
      raise falcon.HTTPNotAcceptable()

    resp.body = json.dumps(doc, ensure_ascii=False)
    resp.status = falcon.HTTP_200


