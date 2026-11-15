"""PyODM wire-format smoke test against a local fake, not a NodeODM server."""
import io
import json
import threading
import zipfile
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

pyodm = pytest.importorskip('pyodm')
from pyodm.exceptions import TaskFailedError
from pyodm.types import TaskStatus


def test_pyodm_task_lifecycle_over_loopback(tmp_path):
    state = {'uploads': {}, 'init': {}, 'removed': [], 'failure': False}
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('odm_georeferencing/result.txt', 'synthetic result')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass
        def response(self, body, content_type='application/json'):
            if isinstance(body, dict):
                body = json.dumps(body).encode()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/info':
                self.response({'version': '1.5.0', 'engine': 'odm', 'engineVersion': 'mock'})
            elif path == '/task/mock-1/info':
                self.response({'uuid': 'mock-1', 'name': 'fixture', 'dateCreated': 0,
                               'processingTime': 1, 'status': {'code': 30 if state['failure'] else 40},
                               'options': [], 'imagesCount': 2})
            elif path == '/task/mock-1/download/all.zip':
                self.response(archive.getvalue(), 'application/zip')
            else:
                self.send_error(404)
        def do_POST(self):
            path = urlsplit(self.path).path
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            if path in ('/task/new/init', '/task/new/upload/mock-1'):
                msg = BytesParser(policy=default).parsebytes(
                    b'Content-Type: ' + self.headers['Content-Type'].encode() + b'\r\nMIME-Version: 1.0\r\n\r\n' + body)
                fields = [(part.get_param('name', header='content-disposition'), part.get_filename(),
                           part.get_payload(decode=True)) for part in msg.iter_parts()]
                if path.endswith('/init'):
                    state['init'] = {name: value.decode() for name, _, value in fields}
                    self.response({'uuid': 'mock-1'})
                else:
                    for name, filename, value in fields:
                        if name == 'images': state['uploads'][filename] = value
                    self.response({'success': True})
            elif path == '/task/new/commit/mock-1':
                self.response({'uuid': 'mock-1'})
            elif path == '/task/remove':
                state['removed'].append(parse_qs(body.decode()).get('uuid', [''])[0])
                self.response({'success': True})
            else:
                self.send_error(404)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        node = pyodm.Node('127.0.0.1', server.server_port, timeout=5)
        assert node.info().engine == 'odm'
        files = []
        for name, content in [('image.jpg', b'fake image'), ('seed.zip', b'fake seed')]:
            path = tmp_path / name; path.write_bytes(content); files.append(str(path))
        task = node.create_task(files, {'dsm': True}, skip_post_processing=True,
                                outputs=['odm_georeferencing'], parallel_uploads=1)
        assert state['uploads'] == {'image.jpg': b'fake image', 'seed.zip': b'fake seed'}
        assert state['init']['skipPostProcessing'] == 'true'
        assert json.loads(state['init']['outputs']) == ['odm_georeferencing']
        assert task.info().status == TaskStatus.COMPLETED
        task.wait_for_completion(interval=0.01)
        destination = tmp_path / 'download'; task.download_assets(str(destination), parallel_downloads=1)
        assert (destination / 'odm_georeferencing/result.txt').read_text() == 'synthetic result'
        state['failure'] = True
        with pytest.raises(TaskFailedError):
            task.wait_for_completion(interval=0.01, max_retries=0)
        assert task.remove() and state['removed'] == ['mock-1']
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
