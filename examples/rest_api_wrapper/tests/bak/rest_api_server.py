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
# 5. Upgrade http server
# 6. Upgrade rpc link mode
# 7. Travis CI
# 8. Code Climate
#################################

import SimpleHTTPServer
import SocketServer
import falcon
import json

from bson_rpc import connect



RPC_HOST_DEF = '127.0.0.1'
RPC_PORT_DEF = 8181
REST_PORT_DEF = 3000

def _read_rpc_config():
  #with open('./examples/rest_api_wrapper/.secret.json') as data:
  with open('./.secret.json') as data:
    config = json.load(data)
    print("Read rpc config: %s" % config)
    return config

# config = _read_rpc_config()
# print("Config: %s : %s" % (config["server"]["master"],config["port"]))
# proxy = connect(str(config["server"]["master"]), config["port"])
proxy = connect("10.80.236.161", 8181)
proxy.die_on_failure(True)
proxy.use_service(['get_persona_with_user_identifier'])

class DemoHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        route = {
            '/' : self.send_root,
            '/persona': self.send_persona,
            '/__stats__': self.send_stats,
        }

        path = self.path
        self.send_head()
        route.get(path, self.send_404)()

    def send_head(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", 21)
        self.end_headers()

    def send_404(self):
        self.wfile.write('''<html><body>
                         <h1>404 Not Found</h1>
                         </body></html>
                         ''')
        self.wfile.flush()
        self.wfile.close()

    def send_root(self):
        self.wfile.write('''<html><body><ul>
                         <li><a href=/1>1</a></li>
                         <li><a href=/2>2</a></li>
                         <li><a href=/3>3</a></li>
                         <li><a href=/4>4</a></li>
                         </ul></body></html>
                         ''')
        self.wfile.flush()
        self.wfile.close()

    def send_persona(self):
        print("send persona")
        err, res = proxy.get_persona_with_user_identifier('53d207bb2c4b9e6b3f97d0d5')
        # persona = json.dumps(res)
        persona = json.dumps({"a":123,"b":"hi"})
        if err == 0:
          print("OK")
          self.wfile.write(str(persona))
        else:
          print("Error!!")
          self.wfile.write(err)
        self.wfile.flush()
        self.wfile.close()
        return

    def send_stats(self):
        err, res = proxy.__stats__()
        if err == 0:
          self.wfile.write(str(res))
          self.wfile.write(str(persona))
        else:
          self.wfile.write(err)
        return

    def send_docx(self, x):
        err, res = proxy.add(x, x + 1)
        print("send docx : %s" % x )
        if err == 0:
            self.wfile.write(res)
        else:
            self.wfile.write(err)

        self.wfile.flush()
        self.wfile.close()

    def send_doc4(self):
        self.send_docx(4)

"""
# Use simple http server
handler = DemoHandler

httpd = SocketServer.TCPServer(('', REST_PORT_DEF ), handler)

print 'httpd server started at http://127.0.0.1:%s' % (REST_PORT_DEF)
httpd.serve_forever()
"""

class PersonaREST(object):

  def on_get(self, req, resp):
    """ Handle get requests """
    print("get persona info")
    # 1. get request query param: uid
    uid = req.get_param('uid') or '' # '53d207bb2c4b9e6b3f97d0d5'
    print("uid is %s" % uid)
    # 2. get rpc data
    err, res = proxy.get_persona_with_user_identifier(uid)
    print("end of get rpc")
    # 3. send http reponse
    if err == 0:
      print("Get Persona OK")
      persona = json.dumps(res)
      # persona = json.dumps({"a":123,"b":"hi"})
      # self.wfile.write(str(persona))
      resp.set_header('Powered-By', 'JuliyeTech')
      resp.status = falcon.HTTP_200
      resp.body = persona
    else:
      print("Get Persona Error!!")
      resp.set_header('Powered-By', 'JuliyeTech')
      resp.status = falcon.HTTP_500
      resp.body = json.dumps({"Error": err})
    return

class MonitorMiddleware(object):
  def process_request(self, req, resp):
    # TODO some monitor process
    print('come into monitor middleware')
    print('host : %s' % req.host) #req.get_header("Host"))
    print('port : %s' % req.port) #req.get_header("Port"))
    print('method : %s' % req.method) #req.get_header("Port"))
    print('uri : %s' % req.uri) #req.get_header("Port"))
    print('headers : %s' % req.headers) #req.get_header("Port"))

app = falcon.API(middleware=[
  MonitorMiddleware(),
  ])
persona = PersonaREST()
app.add_route('/persona', persona)
