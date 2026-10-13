"""Read-only release gate, or an explicit first-time ledger initialization.

No OpenAI request or key/project creation. No credentials are printed.
"""
import argparse
import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from public_access import configuration,ledger,mode


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--init-ledger',action='store_true')
    parser.add_argument('--output');args=parser.parse_args()
    report=dict(mode=mode(),configured=False,ledger_connected=False,platform_project_verified=False,
                actual_oidc_verified=False,public_deployment_performed=False,
                pymupdf_in_production=importlib.util.find_spec('pymupdf') is not None,
                dependencies={name:metadata.version(name) for name in ('streamlit','openai','pypdfium2','Authlib','psycopg')})
    try:
        config=configuration();report['configured']=True
        store=ledger(config)
        if args.init_ledger:store.initialize()
        status=store.inspect('0'*64)
        report.update(ledger_connected=True,remaining_microusd=status['remaining'],paused=status['paused'])
    except Exception:report['blocker']='Server configuration or persisted ledger not verified; paid access remains denied'
    # Local booleans cannot attest to remote account setup or a real OIDC login.
    report['release_ready']=False
    output=json.dumps(report,indent=2)+'\n'
    if args.output:Path(args.output).write_text(output,encoding='utf-8')
    print(output)
