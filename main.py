from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer
from http import HTTPStatus
import base64
import sys

pw_file = 'password.txt'
db = {}

hide_pages = []
skip_extensions = ['ico', 'css']
skip_pages = ['', 'index.html', 'index.htm', 'unauthorized.html']

ip = '127.0.0.1'
port = 10001


def censor_password(password):
    censored = ''
    for c in password:
        censored += '*'
    return censored


class AuthHTTPRequestHandler(SimpleHTTPRequestHandler):
    """ Main class to present webpages and authentication. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='website', **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Login to the website\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_UNAUTHORIZED(self):
        self.do_AUTHHEAD()
        try:
            f = open('website/unauthorized.html', 'rb')
            super().copyfile(f, self.wfile)
        except OSError:
            self.wfile.write(bytes('Not authenticated!', 'utf-8'))
        finally:
            f.close()

    def do_GET(self):
        """ Return the main page without authentication. """
        for page in hide_pages:
            if self.path == '/' + page:
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return

        for extension in skip_extensions:
            if self.path.endswith('.' + extension):
                super().do_GET()
                return

        print('[+] Client is asking for page %s' % self.path)
        for page in skip_pages:
            if self.path == '/' + page:
                print('Returning the page without authentication...')
                super().do_GET()
                return

        """ Present frontpage with user authentication. """
        auth_header = self.headers['Authorization']
        print('Receiving auth header: %s' % auth_header)
        if auth_header is None:
            print('Auth is none, asking for login...')
            self.do_UNAUTHORIZED()
            return

        username, password = base64.b64decode(auth_header[6:]).decode('utf-8').split(':')
        print('Decoded auth Credentials: %s - %s' % (username, censor_password(password)))

        if db.get(username) == password:
            print('Auth is correct, returning the web page...')
            super().do_GET()
            return

        print('Auth is wrong, asking for login again...')
        self.do_UNAUTHORIZED()


def main():
    global ip, port
    if len(sys.argv) >= 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])

    try:
        with open(pw_file, 'r') as f:
            for line in f:
                username, password = line.split()[:2]
                db[username] = password
    except OSError:
        sys.exit('[!] Cloud not load passwords from %s' % pw_file)

    address = (ip, port)
    print('[!] Starting httpd at address %s port %d...' % address)
    httpd = ThreadingTCPServer(address, AuthHTTPRequestHandler)
    httpd.daemon_threads = False
    httpd.allow_reuse_address = True

    try:
        while True:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('[!] Ctrl+C received, shutting down http server...')

    httpd.server_close()


if __name__ == '__main__':
    main()
