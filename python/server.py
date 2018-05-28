from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from led import led
import json

PORT = 8000

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("get")
        led()
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": 200}).encode('ascii'))
        return


try:
    httpd = socketserver.TCPServer(("", PORT), MyHandler)
    print("serving at port", PORT)
    httpd.serve_forever()
except KeyboardInterrupt:
    print("close python server")
    httpd.socket.close()
