import argparse
import datetime
import html
import http.server
import io
import os
import urllib.parse

SERVER_FILES = frozenset({'http_server.py', 'index.css', 'index.js'})


def _fmt_size(n):
    if n >= 1024 * 1024:
        return f'{n / (1024 * 1024):.1f} MB'
    if n >= 1024:
        return f'{n / 1024:.1f} KB'
    return f'{n} B'


def _fmt_mtime(path):
    ts = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')


def _row_html(name, fpath):
    size_bytes = os.path.getsize(fpath)
    mtime = _fmt_mtime(fpath)
    ename = html.escape(name)
    return (
        f'        <tr data-name="{ename}" data-mtime="{mtime}" data-size="{size_bytes}">'
        f'<td><a href="{urllib.parse.quote(name)}">{ename}</a></td>'
        f'<td class="mtime">{mtime}</td>'
        f'<td class="size">{_fmt_size(size_bytes)}</td>'
        f'<td class="col-del"><button class="btn-del" title="Delete" data-name="{ename}">&times;</button></td>'
        f'</tr>'
    )


def _page_html(tbody, count):
    count_label = f'{count} file{"s" if count != 1 else ""}'
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>File Storage</title>
  <link rel="stylesheet" href="index.css">
</head>
<body>
  <header>
    <h1>File Storage</h1>
    <button id="openUpload" class="btn-primary">Upload</button>
  </header>
  <main>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th data-col="name" class="sort-asc">Name <span class="file-count" data-count="{count}">{count_label}</span></th>
            <th data-col="mtime">Modified</th>
            <th data-col="size" class="col-size">Size</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
{tbody}
        </tbody>
      </table>
    </div>
  </main>
  <div id="modal" class="hidden" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <div id="modalBackdrop"></div>
    <div class="modal-panel">
      <div class="modal-header">
        <h2 id="modalTitle">Upload a file</h2>
        <button id="closeUpload" class="btn-icon" aria-label="Close">&times;</button>
      </div>
      <div class="upload-area" id="uploadArea">
        <span class="upload-icon">&#11014;</span>
        <span class="upload-text">Click to browse or drag &amp; drop</span>
        <input type="file" id="fileInput" aria-label="Select file">
      </div>
      <div class="file-info hidden" id="fileInfo">
        <span id="displayFileName"></span>
        <span id="displayFileSize"></span>
      </div>
      <div class="field-group">
        <label for="filename">Save as</label>
        <input type="text" id="filename" placeholder="Leave empty to use original name">
      </div>
      <div class="progress-bar hidden" id="progressBar">
        <div class="progress-fill" id="progressFill"></div>
      </div>
      <button class="btn-primary btn-full" id="uploadButton">Upload</button>
    </div>
  </div>
  <script src="index.js"></script>
</body>
</html>"""


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _send_empty(self, code):
        self.send_response(code)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _reject_nested(self):
        """Send 400 and return True if the URL path goes deeper than root."""
        if '/' in urllib.parse.urlparse(self.path).path.strip('/'):
            self.send_error(400, 'Nested paths are not supported')
            return True
        return False

    def do_PUT(self):
        try:
            if self._reject_nested():
                return
            path = self.translate_path(self.path)
            if path.endswith('/'):
                self.send_error(405, 'PUT not allowed on a directory')
                return
            length = int(self.headers['Content-Length'])
            with open(os.path.basename(path), 'wb') as f:
                f.write(self.rfile.read(length))
            self._send_empty(201)
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
            raise

    def do_DELETE(self):
        try:
            if self._reject_nested():
                return
            name = os.path.basename(self.translate_path(self.path))
            if not name or name in SERVER_FILES:
                self._send_empty(403)
                return
            os.remove(name)
            self._send_empty(204)
        except FileNotFoundError:
            self.send_error(404, 'Not found')
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
            raise

    def list_directory(self, path):
        if os.path.realpath(path) != os.path.realpath(os.getcwd()):
            self.send_error(403, 'Directory listing only available at root')
            return None
        try:
            names = sorted(
                (f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f)) and f not in SERVER_FILES),
                key=str.lower,
            )
        except OSError:
            self.send_error(404, 'No permission to list directory')
            return None

        rows = [_row_html(name, os.path.join(path, name)) for name in names]
        tbody = '\n'.join(rows) if rows else \
            '        <tr class="empty"><td colspan="4">No files uploaded yet.</td></tr>'

        encoded = _page_html(tbody, len(names)).encode('utf-8')
        f = io.BytesIO(encoded)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        return f


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', action='store',
                        default=8080, type=int,
                        help='Specify port to host HTTP server on')
    args = parser.parse_args()

    with http.server.ThreadingHTTPServer(('0.0.0.0', args.port), HTTPRequestHandler) as httpd:
        httpd.serve_forever()
