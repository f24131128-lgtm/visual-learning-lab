"""Read-only public corpus acquisition; never imported by production."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/".day27-local"
SOURCES={
 "circular": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter6.pdf",
 "harmonic": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter23.pdf",
 "circuits": "https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/84f4b553fc6a1ddd7007465041c4e213_6002_l12.pdf",
 "signals": "https://greenteapress.com/thinkdsp/thinkdsp.pdf",
 "python": "https://greenteapress.com/thinkpython2/thinkpython2.pdf",
 "statistics": "https://www.openintro.org/go/?id=os4_for_screen_reader",
 "spectrum": "https://science.nasa.gov/wp-content/uploads/2023/08/tour-of-the-ems-tagged-v7-0.pdf",
}

def download():
    directory=PRIVATE/"originals"; directory.mkdir(parents=True,exist_ok=True)
    records=[]
    for key,url in SOURCES.items():
        path=directory/(key+".pdf")
        if not path.exists():
            with urlopen(Request(url,headers={"User-Agent":"VLL educational evaluation"}),timeout=60) as response:
                data=response.read(25_000_001); resolved=response.url
            if not data.startswith(b"%PDF-") or len(data)>25_000_000:
                raise ValueError(key+" is not a bounded PDF")
            path.write_bytes(data)
        else: resolved=None
        data=path.read_bytes()
        records.append(dict(source_id=key,url=url,resolved_url=resolved,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        print(key,len(data),records[-1]["sha256"],flush=True)
        (PRIVATE/"download-records.json").write_text(json.dumps(records,indent=2),encoding="utf-8")

if __name__=="__main__": download()
