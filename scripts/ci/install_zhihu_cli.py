import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import tarfile
import urllib.request

url = 'https://developer-cdn.zhihu.com/zhihu-cli/releases/stable/cli/0.6.1/zhihu-cli-0.6.1-linux-amd64.tar.gz'
expected_size = 3000541
expected_sha = '65d8d7e6bf96c999095835b540c9d749f24a3c37c1d34217a23e825ee2eae376'
class OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        from urllib.parse import urlparse
        parsed = urlparse(newurl)
        if parsed.scheme != 'https' or parsed.netloc != 'developer-cdn.zhihu.com':
            raise RuntimeError('Refusing a redirect outside the official HTTPS host')
        return super().redirect_request(req, fp, code, msg, headers, newurl)
opener = urllib.request.build_opener(OfficialRedirects())
with opener.open(url, timeout=30) as response:
    data = response.read(expected_size + 1)
if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_sha:
    raise SystemExit('Official CLI download failed size/SHA-256 verification')
with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
    members = archive.getmembers()
    if len(members) != 1 or members[0].name != 'zhihu-cli' or not members[0].isfile():
        raise SystemExit('Unexpected CLI archive structure')
    binary = archive.extractfile(members[0]).read()
if binary[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', binary, 18)[0] != 62:
    raise SystemExit('Expected Linux x86-64 CLI')
cli = Path(os.environ['RUNNER_TEMP']) / 'zhihu-cli'
cli.write_bytes(binary)
cli.chmod(0o700)
result = subprocess.run([str(cli), 'version'], capture_output=True, text=True, timeout=10)
if result.returncode != 0 or json.loads(result.stdout).get('version') != '0.6.1':
    raise SystemExit('CLI runtime version verification failed')
print('PASS: official Linux CLI downloaded, verified and executed (0.6.1)')
