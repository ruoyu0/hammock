from __future__ import absolute_import
import six
import threading
import logging
import json
import socket


def test_connection(address):
    try:
        socket.create_connection(address)
    except socket.error:
        return False
    else:
        return True


class Server(object):
    def __init__(self, host="localhost", port=None, name=None):
        self.host = host
        self.port = port or self._get_available_port()
        logging.info("Starting server on %s:%d...", self.host, self.port)
        self.name = name
        self._httpd = _Server((self.host, self.port), type("Handler", (Handler, object), {"name": self.name}))
        self._thread = threading.Thread(target=self._httpd.serve_forever)
        self._thread.start()
        logging.info("Server started")

    def close(self):
        logging.info("Closing server...")
        self._httpd.shutdown()
        self._httpd.server_close()
        logging.info("Server closed")

    def _get_available_port(self):
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port


class _Server(six.moves.socketserver.TCPServer):
    allow_reuse_address = True


class Handler(six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler):
    name = None

    def __init__(self, *args, **kwargs):
        self.path = None
        six.moves.SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_GET(self):  # NOQA
        self._do("GET")

    def do_DELETE(self):  # NOQA
        self._do("DELETE")

    def do_POST(self):  # NOQA
        self._do("POST")

    def do_PUT(self):  # NOQA
        self._do("PUT")

    def _do(self, method):
        if 'content-length' in self.headers \
                and int(self.headers['content-length']) > 0 \
                and method in ("PUT", "POST"):
            body = self.rfile.read(int(self.headers['content-length']))
        else:
            body = None
        if body and not isinstance(body, six.string_types):
            body = body.decode()
        parsed = six.moves.urllib.parse.urlsplit(self.path)
        content = dict(
            method=method,
            path=parsed.path,
            headers=dict(self.headers.items()),
            query_string=parsed.query,
            body=body,
        )
        content['server_name'] = self.__class__.name
        logging.info("Server echoing: %s", content)
        self.send_response(200)
        if not self.headers.get('content-type') or self.headers['content-type'] == 'application/json':
            if isinstance(content, six.binary_type):
                content = content.decode()  # pylint: disable=no-member
            content = six.b(json.dumps(content))
            self.send_header('content-length', len(content))
            self.send_header('content-type', 'application/json')
            self.end_headers()
            self.wfile.write(content)
        else:
            content = six.b(body)
            self.send_header('content-length', len(content))
            self.send_header('content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)
        self.wfile.flush()
