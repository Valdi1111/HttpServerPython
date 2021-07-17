from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import base64


class SimpleAuthHandler(SimpleHTTPRequestHandler):
    """ Main class to present webpages and authentication. """

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Login to the website\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """ Present frontpage with user authentication. """
        username = "sos"
        password = "sos"
        key = base64.b64encode(bytes("%s:%s" % (username, password), "utf-8")).decode("utf-8")

        if self.headers['Authorization'] == 'Basic '+key:
            super().do_GET()
        else:
            self.do_AUTHHEAD()
            f = None
            try:
                f = open("unauthorized.html", 'rb')
            except OSError:
                self.wfile.write(bytes('Not authenticated', 'utf-8'))

            if f:
                try:
                    super().copyfile(f, self.wfile)
                finally:
                    f.close()


def main():
    try:
        ip = "127.0.0.1"
        port = 10001
        httpd = ThreadingHTTPServer((ip, port), SimpleAuthHandler)
        print('started httpd...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        httpd.socket.close()


if __name__ == '__main__':
    main()
