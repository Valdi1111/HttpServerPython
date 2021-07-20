from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import base64
import sys
db = {}



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
        if self.path == "/" or self.path == "/index.html":
            super().do_GET()
        """ Present frontpage with user authentication. """
        canEnter = False
        for user in db:
            key = base64.b64encode(bytes("%s:%s" % (user, db[user]), "utf-8")).decode("utf-8")
            if self.headers['Authorization'] == 'Basic '+key:
                canEnter = True



        if canEnter:
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
        with open("password.txt", 'r') as fp:
            for line in fp:
                auth = line.split()[:2]
                db[auth[0]] = auth[1]
    except OSError:
        sys.exit('File not loaded')
    try:
        ip = "192.168.1.42"
        port = 10001
        httpd = ThreadingHTTPServer((ip, port), SimpleAuthHandler)
        print('started httpd...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(' received, shutting down server')
        httpd.socket.close()


if __name__ == '__main__':
    main()
