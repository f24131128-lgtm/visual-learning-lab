"""Repackage existing verified Day28 captures, never generate model content."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root/'prepared/harmonic'
target.mkdir(parents=True, exist_ok=True)
previous = json.loads((root/'docs/day28/prepared-inputs.json').read_text(encoding='utf-8'))['files_sha256']
for name, digest in previous.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest
(target/'source.pdf').write_bytes((root/'.day27-local/subsets/harmonic.pdf').read_bytes())
for kind, old in [('analysis','main'),('atlas','atlas')]:
    raw = json.loads((root/f'.day27-local/post_fix/responses/harmonic--{old}.json').read_text(encoding='utf-8'))['raw']
    (target/f'{kind}.json').write_text(json.dumps(raw, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
manifest = dict(source='MIT OpenCourseWare / Peter Dourmashkin, Chapter 23: Simple Harmonic Motion',
    url='https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs16_chapter23/',
    original_pages=list(range(3,11)), license='CC BY-NC-SA 4.0', prepared=True,
    provenance='Unedited source subset and existing Day27 human-approved main/Atlas declarations reused by Day28',
    limits='Estimated Atlas grounding; source formulas without exact semantic ownership have no fabricated control link.',
    sha256={name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in ('source.pdf','analysis.json','atlas.json')})
(target/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
