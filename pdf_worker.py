"""Fixed PDF operation process. Never imports UI or OpenAI and never executes data."""
import os
import sys

if os.name!='nt':
    import resource
    resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(15,15))
    resource.setrlimit(resource.RLIMIT_FSIZE,(0,0))

import base64
import json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from production_safety import checked_pdf, checked_text


def dispatch(request):
    data=base64.b64decode(request['data'],validate=True)
    operation=request['operation'];parameters=request['parameters']
    if operation in ('inspect','extract'):
        if len(data)>2*1024*1024:raise ValueError()
        reader=checked_pdf(data,parameters.get('name'),parameters.get('mime'))
        if len(reader.pages)>2:raise ValueError()
        if operation=='inspect':return dict(pages=len(reader.pages))
        pages={i:(p.extract_text() or '').strip() for i,p in enumerate(reader.pages,1)}
        for text in pages.values():checked_text(text)
        pages={i:text for i,text in pages.items() if text}
        text='\n\n'.join(f'[Page {i}]\n{value}' for i,value in pages.items());checked_text(text)
        return dict(text=text,total_pages=len(reader.pages),extractable_page_numbers=list(pages),
                    analyzed_page_numbers=list(pages),analyzed_page_texts=pages)
    from pdf_renderer import render,anchors
    if operation=='render':
        if set(parameters)!={'number','dpi','side'} or not 40<=parameters['dpi']<=200 or not 100<=parameters['side']<=2200:raise ValueError()
        value=render(data,**parameters);value['png']=base64.b64encode(value['png']).decode();return value
    if operation=='anchors':return anchors(data,**parameters)
    raise ValueError()


if __name__=='__main__':
    try:
        raw=sys.stdin.buffer.read(14*1024*1024+1)
        if len(raw)>14*1024*1024:raise ValueError()
        value=dispatch(json.loads(raw))
        output=json.dumps(dict(ok=True,value=value)).encode()
        if len(output)>8*1024*1024:raise ValueError()
        sys.stdout.buffer.write(output)
    except Exception:
        sys.stdout.write('{"ok":false}')
