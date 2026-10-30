import json
import pytest
from common import ScaffoldError
from inventory_conda_environment import inventory


def test_inventory_sanitizes_url_and_reports_missing_metadata(tmp_path):
    meta=tmp_path/'conda-meta'; meta.mkdir()
    (meta/'pkg.json').write_text(json.dumps({'name':'pkg','version':'1','build':'0','url':'https://user:secret@example.com/a.conda?token=secret','sha256':'abc','files':['share/licenses/pkg/LICENSE','bin/x']}))
    p=inventory(tmp_path)['packages'][0]
    assert p['source_package_url']=='https://example.com/a.conda'
    assert p['license'] is None and p['notice_paths']==['share/licenses/pkg/LICENSE']
    (meta/'bad.json').write_text('{}')
    with pytest.raises(ScaffoldError): inventory(tmp_path)
