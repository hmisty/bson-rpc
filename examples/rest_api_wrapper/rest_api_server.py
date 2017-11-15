#!/usr/bin/env python
#encoding:utf-8

import SimpleHTTPServer
import SocketServer

from bson_rpc import connect

PORT = 3000

proxy = connect('127.0.0.1', 8181)
#proxy.die_on_failure(False)

proxy.use_service(['add'])

class DemoHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        route = {
            '/' : self.send_docroot,
            '/1': self.send_doc1,
            '/2': self.send_doc2,
            '/3': self.send_doc3,
            '/4': self.send_doc4,
        }

        path = self.path
        self.send_head()
        route.get(path, self.send_404)()

    def send_head(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def send_404(self):
        self.wfile.write('''<html><body>
                         <h1>404 Not Found</h1>
                         </body></html>
                         ''')
        self.wfile.flush()
        self.wfile.close()

    def send_docroot(self):
        self.wfile.write('''<html><body><ul>
                         <li><a href=/1>1</a></li>
                         <li><a href=/2>2</a></li>
                         <li><a href=/3>3</a></li>
                         <li><a href=/4>4</a></li>
                         </ul></body></html>
                         ''')
        self.wfile.flush()
        self.wfile.close()

    def send_docx(self, x):
        err, res = proxy.add(x, x + 1)
        print("send docx : %s" % x )
        if err == 0:
            self.wfile.write(res)
        else:
            self.wfile.write(err)

        self.wfile.flush()
        self.wfile.close()

    def send_doc1(self):
        self.send_docx(1)

    def send_doc2(self):
        self.send_docx(2)

    def send_doc3(self):
        self.send_docx(3)

    def send_doc4(self):
        self.send_docx(4)


handler = DemoHandler

httpd = SocketServer.TCPServer(('', PORT), handler)

print 'httpd server started at http://127.0.0.1:%s' % (PORT)
httpd.serve_forever()

