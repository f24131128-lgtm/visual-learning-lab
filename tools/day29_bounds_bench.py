"""Small synthetic envelope timing, not hostile-resource or cloud load testing."""
import io
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pypdf import PdfWriter
from production_safety import checked_pdf, MAX_PDF_BYTES

rows=[]
writer=PdfWriter()
for _ in range(81):writer.add_blank_page(width=100,height=100)
stream=io.BytesIO();writer.write(stream)
for name,data in [('oversize bytes',b'%PDF-'+b'0'*MAX_PDF_BYTES),('81 blank pages',stream.getvalue())]:
    start=time.perf_counter()
    try:
        checked_pdf(data)
        raise AssertionError('Expected rejection')
    except ValueError:
        rows.append(dict(case=name,bytes=len(data),seconds=time.perf_counter()-start,status='REJECTED'))
(ROOT/'docs/day29/bounds-performance.json').write_text(json.dumps(dict(
    corpus='Synthetic, created locally; no actual exhaustion',python=sys.version,
    allocation='Input already allocated before timer; not a memory benchmark',results=rows),indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
