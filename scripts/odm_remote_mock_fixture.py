#!/usr/bin/env python3
"""Exercise ODM's remote task plumbing using an in-process fake, never HTTP."""
import json
import os
import sys
import tempfile
import threading
import zipfile
from pathlib import Path
from types import SimpleNamespace


def run(prefix, app):
    os.environ['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    sys.path.insert(0, str(app))
    from opendm import remote
    from pyodm.types import TaskStatus
    from pyodm import exceptions
    remote.get_submodel_args_dict = lambda config: {'fixture': True}
    remote.config.config = lambda: None
    with tempfile.TemporaryDirectory(prefix='odm-remote-mock-') as directory:
        root = Path(directory)
        (root / 'images').mkdir()
        (root / 'images' / 'synthetic.jpg').write_bytes(b'not a real image')
        (root / 'opensfm').mkdir()
        for name in ('camera_models.json', 'reference_lla.json', 'reconstruction.json', 'tracks.csv'):
            (root / 'opensfm' / name).write_text('fixture')
        class FakeTask:
            uuid = 'mock-task'
            def __init__(self, fail): self.fail = fail
            def info(self): return SimpleNamespace(status=TaskStatus.RUNNING)
            def wait_for_completion(self, status_callback):
                status_callback(SimpleNamespace(status=TaskStatus.RUNNING))
                if self.fail: raise exceptions.TaskFailedError('injected failure')
            def output(self): return ['synthetic remote failure']
            def download_assets(self, destination, progress_callback):
                (Path(destination) / 'mock-downloaded.txt').write_text('synthetic result')
        class FakeNode:
            def __init__(self, fail): self.fail = fail; self.calls = []
            def create_task(self, files, args, progress_callback, skip_post_processing, outputs):
                seed = next(Path(f) for f in files if Path(f).name == 'seed.zip')
                with zipfile.ZipFile(seed) as z:
                    names = set(z.namelist())
                assert {'opensfm/reconstruction.json', 'opensfm/tracks.csv', 'opensfm/features/empty'} <= names
                assert any(Path(f).name == 'synthetic.jpg' for f in files)
                assert args == {'fixture': True} and skip_post_processing
                assert 'odm_georeferencing' in outputs and 'odm_dem' in outputs
                self.calls.append({'seed_members': len(names), 'requested_outputs': len(outputs)})
                return FakeTask(self.fail)
        result = {}
        for fail in (False, True):
            if fail:
                (root / 'toolchain_completed.txt').unlink()
                (root / 'mock-downloaded.txt').unlink()
            node = FakeNode(fail)
            params = {'tasks': [], 'threads': [], 'rerun': False}
            task = remote.ToolchainTask(str(root), node, params)
            done_event = threading.Event(); errors = []
            def done(error=None):
                errors.append(error); done_event.set()
            task.process_remote(done)
            if not done_event.wait(10): raise AssertionError('remote callback timed out')
            for thread in params['threads']: thread.join(10)
            if len(node.calls) != 1 or len(errors) != 1: raise AssertionError('unexpected task or callback count')
            if fail:
                assert isinstance(errors[0], exceptions.TaskFailedError)
                assert not (root / 'toolchain_completed.txt').exists()
                assert not (root / 'mock-downloaded.txt').exists()
                assert 'synthetic remote failure' in (root / 'error.log').read_text()
            else:
                assert errors == [None]
                assert (root / 'toolchain_completed.txt').is_file()
                assert (root / 'mock-downloaded.txt').read_text() == 'synthetic result'
            assert not (root / 'seed.zip').exists()
            result['failure' if fail else 'success'] = node.calls[0]
        return result


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()), sort_keys=True))
