"""Separate preserved Day28 work from the exact uncommitted Day29 inventory."""
from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


if __name__=='__main__':
    changed=git('diff','--name-only','-z').decode('utf-8').strip('\0').split('\0')
    restored=[]
    for name in changed:
        # All tracked bytecode was clean at Day29 start; restore only our artifacts.
        if '__pycache__/' in name and name.endswith('.pyc'):
            (ROOT/name).write_bytes(git('show','HEAD:'+name))
            restored.append(name)
    record=ROOT/'docs/day29/restored-test-artifacts.json'
    if restored:record.write_text(json.dumps(dict(restored_to_original_clean_blob=restored,method='Git blob read/write, no checkout/reset'),indent=2)+'\n',encoding='utf-8')
    changed=git('diff','--name-only','-z').decode('utf-8').strip('\0').split('\0')
    new=git('ls-files','--others','--exclude-standard','-z').decode('utf-8').strip('\0').split('\0')
    prior_tracked=['app.py','docs/OPEN_SOURCE_REUSE_LEDGER.md','i18n.py','interactive_lab.py','workspace/ui.py']
    prior_exact=['docs/DAY28_CHECKPOINT.md','docs/DAY28_EVIDENCE.md','tests/day28_freeze.py','tests/day28_prepared.py','tests/manual_day28.py','tests/manual_day28_red_team.py','tests/test_day28_preparation.py','tests/test_day28_red_team.py','workspace/control_navigation.py']
    prior_new=[name for name in new if name in prior_exact or name.startswith(('docs/day28/','docs/day28-ai-red-team/'))]
    retained_only=['interactive_lab.py','workspace/ui.py']
    out=ROOT/'docs/day29/changed-files.json'
    day29_new=sorted(set(new)-set(prior_new)|{'docs/day29/changed-files.json'})
    out.write_text(json.dumps(dict(
        branch=git('branch','--show-current').decode().strip(),head=git('rev-parse','HEAD').decode().strip(),
        original_dirty_tracked=prior_tracked,retained_day28_only_tracked=retained_only,
        day29_modified_tracked=sorted(set(changed)-set(retained_only)),
        original_day28_untracked=sorted(prior_new),day29_new_untracked=day29_new,
        commit=False,push=False,ignored_test_env='.day29-local, excluded from deployment'),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(day29_modified=len(set(changed)-set(retained_only)),day29_new=len(day29_new),prior_untracked=len(prior_new),restored_bytecode=len(restored))))
