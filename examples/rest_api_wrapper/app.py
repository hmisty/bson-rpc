#!/usr/bin/env python
#encoding:utf-8
#
#################################
# TODO List:
# 1. Launch server -  DONE
#   python examples/rest_api_wrapper/rest_api_server.py >> logs/access.log &
#   tail -f logs/access.log
# 2. Unit Test | REST Client
# 3. Launch server pid
# 4. Server Deaman
# 5. Upgrade http server -falcon -DONE
#    gunicorn app
# 6. Upgrade rpc link mode -DONE
# 7. Travis CI
# 8. Code Climate
#################################

import falcon
import json

from bson_rpc import connect
# Import middlewares
from middlewares.authentication import Authentication
from middlewares.authorization import Authorization
from middlewares.accounting import Accounting
# Import resources
from resources.images import ImageCollection,ImageItem
from resources.persona import PersonaRest
from resources.things import ThingsRest
#
from config import CONFIG

def load_routes(api, rpc):
  api.add_route('/persona', PersonaRest(rpc))
  api.add_route('/images', ImageCollection(storage_path='.'))
  api.add_route('/images/{_id}', ImageItem())
  api.add_route('/things', ThingsRest())

def conn_rpc():
  # print(CONFIG.version)
  # print("config %s %s" % (CONFIG.server.master, CONFIG.port))
  master = str(CONFIG.server.master)
  slave = str(CONFIG.server.slave)
  rpc = connect(master, slave, CONFIG.port)
  rpc.die_on_failure(True)
  rpc.use_service(['get_persona_with_user_identifier'])
  return rpc

api = application = falcon.API(middleware=[
  ## 3A Middleware
  Authentication(), # 身份认证
  Authorization(),  # 操作授权
  Accounting(),     # 日志审计
])

load_routes(api, conn_rpc())
