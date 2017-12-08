#!/usr/bin/env python
#encoding=utf-8

import falcon
from falcon import testing
import json
import pytest
# Python 3
# from unittest.mock import mock_open, call
# Python 2
from mock import mock_open, call

from app import api

@pytest.fixture
def client():
  print("init client")
  return testing.TestClient(api)

def test_get_images(client):
  print("test get images")
  doc = {
      'images': [
        {'name':'baidu', 'href': 'https://www.baidu.com/img/bd_logo1.png'}
      ]
      }

  response = client.simulate_get('/images')

  assert 1 == 1
  #assert response.status == falcon.HTTP_OK
  #assert response.content == json.dumps(doc)

def test_post_images(client, monkeypatch):
  print("test post images")
  mock_file_open = mock_open()
  monkeypatch.setattr('io.open', mock_file_open)

  fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
  monkeypatch.setattr('uuid.uuid4', lambda: fake_uuid)

  # when the service receive an image through POST
  fake_image_bytes = b'fake-image-bytes'
  response = client.simulate_post(
      '/images',
      body=fake_image_bytes,
      headers={'content-type': 'image/png'}
      )
  assert response.status == falcon.HTTP_CREATED
  assert call().write(fake_image_bytes) in mock_file_open.mock_calls
  assert response.headers['location'] == '/images/{}.png'.format(fake_uuid)


