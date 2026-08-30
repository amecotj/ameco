import http.server, urllib.request
class Proxy(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        req = urllib.request.Request("http://127.0.0.1:5001" + self.path, data=body, headers=dict(self.headers), method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
    def do_GET(self):
        self.do_POST()
http.server.HTTPServer(('', 80), Proxy).serve_forever()
