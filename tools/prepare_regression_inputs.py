"""Restore hash-pinned offline study inputs without changing frozen evidence.

Only the five indispensable captures/reports are bundled. No network, model
client, extraction of arbitrary archive paths, or expected-hash updates.
"""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA256 = 'c207c649705e56fa09b2ae77c789961e8c06612ea47ca04cb3ea286bdfc4e589'
ARCHIVED = frozenset((
    '.day27-local/post_fix/responses/harmonic--main.json',
    '.day27-local/post_fix/responses/harmonic--atlas.json',
    'docs/day28/pretest/focused-final.log',
    'docs/day28/pretest/focused.log',
    'docs/day28/pretest/full-regression.log',
))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exact_bytes(data, expected):
    """Accept only exact frozen bytes or their reversible checkout newlines."""
    lf = data.replace(b'\r\n', b'\n')
    for candidate in (data, lf, lf.replace(b'\n', b'\r\n')):
        if digest(candidate) == expected:
            return candidate
    raise ValueError('Frozen input hash differs')


def prepare(root=ROOT):
    root = Path(root).resolve()
    manifests = (
        ('docs/day28/prepared-inputs.json', 'files_sha256'),
        ('docs/day28/freeze-manifest.json', 'files_sha256'),
        ('docs/day28-ai-red-team/baseline-integrity.json', 'files_sha256'),
    )
    expected = {}
    for name, key in manifests:
        values = json.loads((root / name).read_text(encoding='utf-8-sig'))[key]
        for path, fingerprint in values.items():
            if path in expected and expected[path] != fingerprint:
                raise ValueError('Conflicting frozen manifests')
            expected[path] = fingerprint
    archive = root / 'tests/fixtures/day28-frozen-inputs.zip'
    if digest(archive.read_bytes()) != ARCHIVE_SHA256:
        raise ValueError('Frozen archive hash differs')
    writes = []
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != ARCHIVED or sum(i.file_size for i in bundle.infolist()) > 1024 * 1024:
            raise ValueError('Frozen archive envelope differs')
        for name, fingerprint in expected.items():
            path = (root / name).resolve()
            if not path.is_relative_to(root):
                raise ValueError('Frozen path outside repository')
            if path.exists():
                original = path.read_bytes()
                data = exact_bytes(original, fingerprint)
                if data != original:
                    writes.append((path, data))
            else:
                if name in ARCHIVED:
                    data = bundle.read(name)
                elif name == '.day27-local/subsets/harmonic.pdf':
                    data = (root / 'prepared/harmonic/source.pdf').read_bytes()
                else:
                    raise ValueError('Required frozen input absent: ' + name)
                writes.append((path, exact_bytes(data, fingerprint)))
    # Validate everything before touching any path; never replace changed data.
    for path, data in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return len(writes)


if __name__ == '__main__':
    print('Hash-verified offline inputs restored:', prepare())
