# Based on https://gist.github.com/mildred/67d22d7289ae8f16cae7

import argparse
import http.server

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_PUT(self):
        try:
            path = self.translate_path(self.path)
            if path.endswith('/'):
                self.send_response(405, "Method Not Allowed")
                self.end_headers()
                self.wfile.write("PUT not allowed on a directory\n".encode())
            else:
                # Don't support folders as we don't know where it is hosted from (e.g., HTTPProxy)
                path = path.rsplit("/", 1)[-1]
                length = int(self.headers['Content-Length'])
                with open(path, 'wb') as f:
                    f.write(self.rfile.read(length))
                self.send_response(201, "Created")
                self.send_header('Content-Length', '0')
                self.end_headers()
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
            raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', action='store',
                        default=8080, type=int,
                        help='Specify port to host HTTP server on')
    args = parser.parse_args()

    http.server.test(HandlerClass=HTTPRequestHandler, port=args.port, bind="0.0.0.0")
