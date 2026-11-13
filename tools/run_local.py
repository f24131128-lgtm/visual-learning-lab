"""Local personal-material launcher. Never exposes a private server publicly."""
import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def launch_command(port):
    if not 1024 <= port <= 65535:
        raise ValueError("Port must be between 1024 and 65535")
    return [sys.executable, '-m', 'streamlit', 'run', str(ROOT/'app.py'),
            '--server.address', '127.0.0.1', '--server.port', str(port),
            '--server.headless', 'true', '--browser.gatherUsageStats', 'false']

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8501)
    parser.add_argument('--demo', action='store_true', help='Prepared examples only; no key needed')
    parser.add_argument('--prompt-key', action='store_true', help='Replace an existing environment key with hidden input')
    args=parser.parse_args()
    try: command=launch_command(args.port)
    except ValueError as error: parser.error(str(error))
    env=os.environ.copy()
    env['VLL_LIVE_AI']='' if args.demo else 'private'
    if not args.demo and (args.prompt_key or not env.get('OPENAI_API_KEY')):
        key=getpass.getpass('OpenAI API key (hidden; used only by this local process): ').strip()
        if not key:
            parser.error('A key is required for personal analysis. Use --demo for free examples.')
        env['OPENAI_API_KEY']=key
    print(f'Open http://127.0.0.1:{args.port} — Ctrl+C to stop.')
    print('AI analysis sends your material to OpenAI and may incur charges only after an explicit action.' if not args.demo else 'Prepared mode: no paid AI requests.')
    try: return subprocess.call(command, cwd=ROOT, env=env)
    except KeyboardInterrupt: return 0

if __name__=='__main__': sys.exit(main())
