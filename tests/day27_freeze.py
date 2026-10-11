"""Deterministic public page subsets and prospective corpus, never production.

prepare() retains the original prospective AI draft. freeze_approved_review()
applies the user's recorded 2026-10-11 review to that exact draft, verifies
the source/production hashes and freezes the approved packet without requests.
This is not a general permission mechanism for later drafts or model execution.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from day27_sources import ROOT, PRIVATE, SOURCES

PUBLIC=ROOT/"docs/day27"
MIT="https://ocw.mit.edu/pages/privacy-and-terms-of-use/"
GREEN="https://greenteapress.com/"
OPEN="https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md"
NASA="https://www.nasa.gov/nasa-brand-center/images-and-media/"

# Integer pages mean 1-based physical PDF pages, never original printed labels.
CASES=[
 ("circular","circular",list(range(3,11)),"spatial/mechanics","MIT OCW","Classical Mechanics Chapter 6: Circular Motion",MIT,"CC BY-NC-SA 4.0",True,True,
  ["position on a circle","angular velocity and period","tangential velocity","radial acceleration"],
  ["spatial_dynamics","numeric_lab","formal concept map"],
  ["source example coefficients remain compiled baseline; not measurements"],
  ["positive radius","positive uniform angular speed","time"],
  ["no gravitational orbit or motor torque model","no radius=0","no changing the original source examples"],
  "A formal/numeric view is correct if a consistent bounded planar world cannot compile."),
 ("harmonic","harmonic",list(range(3,11)),"spatial/physical-system","MIT OCW","Classical Mechanics Chapter 23: Simple Harmonic Motion",MIT,"CC BY-NC-SA 4.0",True,True,
  ["amplitude and period","Hooke force and mass","omega=sqrt(k/m)","initial conditions and phase"],
  ["spatial_dynamics","numeric_lab","formal concept map"],
  ["given initial conditions must remain identified as the source baseline"],
  ["positive mass and spring constant","non-negative amplitude","phase","time"],
  ["no damping or driving force","no amplitude interpreted as wavelength","no arbitrary 3D mechanics"],
  "Numeric/formal degradation is correct when the runtime cannot express the oscillator honestly."),
 ("circuits","circuits",list(range(6,14)),"signal/circuit/engineering","MIT OCW","6.002 Lecture 12: First Order Circuits",MIT,"CC BY-NC-SA 4.0",True,True,
  ["RC node equation","homogeneous and particular solutions","initial voltage","tau=RC","charging and discharging"],
  ["numeric_lab","dynamic_simulation","process_flow","formal comparison"],
  ["5 V/0 V examples and boundary conditions are source baselines"],
  ["positive R and C","hypothetical input/initial voltage","time"],
  ["no invented measured component values","no nonlinear transistor or second-order RLC model","no physical circuit rewiring handle"],
  "A formula/table/flow is correct without an unambiguous waveform inverse; generic bounded hypothetical defaults must be labeled."),
 ("signals","signals",list(range(14,19)),"signal/oscillation/engineering","Green Tea Press / Allen B. Downey","Think DSP: Sounds and Signals",GREEN,"CC BY-NC-SA 4.0 (PDF copyright page)",False,False,
  ["period/frequency","waveform/timbre","harmonics and spectral decomposition","two-sinusoid mixture"],
  ["numeric_lab","formal concept map","comparison"],
  ["439 Hz observed bell and plotted recording","440/880 Hz, 1.0/0.5 and offset=0 example baseline","original spectrum samples"],
  ["hypothetical sine/cosine frequency, amplitude and phase","bounded time window"],
  ["no exact recovery of the recorded audio/spectrum from the screenshot","no execution of thinkdsp Python or audio download","no invented measured Fourier coefficients"],
  "Static descriptions are correct if only measured recordings are modeled or a safe symbolic demo is unsupported."),
 ("regression","statistics",list(range(355,361)),"equation-heavy quantitative relationship","OpenIntro / Diez, Cetinkaya-Rundel, Barr","OpenIntro Statistics 4e screen-reader edition: Least Squares Regression",OPEN,"CC BY-SA 3.0 text; excluded branding/cover",False,False,
  ["sum of squared residuals","b1=(sy/sx)R","line passes through means","interpretation of slope/intercept","prediction limitations"],
  ["numeric_lab","formal comparison","concept map"],
  ["50-student sample","means 101780/19940; sd 63200/5460; R=-0.499","fitted slope -0.0431 and intercept 24.319 in thousands","empirical source dots"],
  ["prediction input inside observed range","explicitly hypothetical trial line separate from fitted source coefficients"],
  ["no causal scholarship policy claim","no real student data reconstruction","do not make fitted estimates adjustable without a hypothetical distinction"],
  "A formal equation and source plot is correct if fixed empirical data cannot be represented; no drag of observed dots."),
 ("probability","statistics",list(range(93,101)),"probability/discrete structure","OpenIntro / Diez, Cetinkaya-Rundel, Barr","OpenIntro Statistics 4e screen-reader edition: Defining Probability",OPEN,"CC BY-SA 3.0 text; excluded branding/cover",True,True,
  ["disjoint events","die outcome sets A={1,2}, B={4,6}, D={2,3}","inclusive or and intersection correction","complement","non-uniform dice-sum distribution"],
  ["probability_sets","formal comparison","concept map"],
  ["six fair die outcomes and source memberships","52-card counts","two-dice sum weights","given income/loan proportions"],
  ["local event selection/set operations","Monte Carlo sample count with original probabilities"],
  ["do not treat dice sums as uniformly likely","no arbitrary changes to source probabilities","no unlimited 52-outcome world if contract exceeds bounds"],
  "A bounded six-outcome die subset is honest with scope disclosed; other examples may stay formal. Dragging geometry is N/A."),
 ("search","python",[226,227],"process/state/algorithm","Green Tea Press / Allen B. Downey","Think Python 2e Appendix B: Analysis of Algorithms, Search",GREEN,"CC BY-NC 3.0 (PDF copyright page)",False,False,
  ["sequential search O(n)","sorted-list bisection O(log n)","constant-time list operations","hashing and dictionaries"],
  ["process_flow","formal flow","comparison"],
  ["algorithm correctness and complexity assumptions","source contains no measured timing dataset"],
  ["local navigation through declared process","explicit hypothetical sorted input only if safely resolved"],
  ["no execution of generated Python","no unsupported arbitrary binary-search machine","no invented measured benchmarks"],
  "A read-only flow/comparison is correct when bounded execution is unsupported."),
 ("complexity","python",[223,224,225],"comparison/conceptual structure","Green Tea Press / Allen B. Downey","Think Python 2e Appendix B: Order of Growth",GREEN,"CC BY-NC 3.0 (PDF copyright page)",False,False,
  ["asymptotic analysis","linear vs quadratic","100n+1 vs n^2+n+1","Big-O growth table"],
  ["comparison","numeric_lab","concept map"],
  ["source example coefficients 100 and 1","Big-O definitions and table classes"],
  ["positive integer input size n for illustrative operation counts"],
  ["do not present operation count as measured wall-clock time","no changing source algorithm coefficients","no source-supported hardware benchmark claim"],
  "A comparison/table is sufficient; numeric count curves are optional and must stay illustrative."),
 ("spectrum","spectrum",[35],"diagram/table-heavy reference","NASA / Ginger Butcher","Tour of the Electromagnetic Spectrum 3e: Unit Conversion Scale",NASA,"NASA general educational/informational media permission; attribution; no endorsement",True,False,
  ["frequency/wavelength/energy unit conventions","scientific notation","unit conversion scale table","positive wavelength values"],
  ["comparison","numeric_lab","formal table"],
  ["every source table cell and size comparison","vacuum conversion baseline approximately c=3e8 m/s if explained as general physics"],
  ["explicitly hypothetical positive wavelength/frequency conversion within numeric limits"],
  ["no zero wavelength","no invented full spectrum dataset or new 3D propagation scene","no claimed exact page-box grounding before Atlas validation"],
  "Static table is correct if numeric dynamic ranges exceed the bounded evaluator. Only physical PDF page 35 is ingested: photo/stock pages are excluded."),
 ("debugging","python",[215,216],"honest static/formal control","Green Tea Press / Allen B. Downey","Think Python 2e Appendix A: Debugging",GREEN,"CC BY-NC 3.0 (PDF copyright page)",False,False,
  ["syntax/runtime/semantic errors","incremental testing","localizing syntax faults","debugging strategy"],
  ["formal flow","concept map","comparison"],
  ["error-category meanings","source advice"],
  ["local reading/selection only"],
  ["no numerical physics world","no fabricated executable debugger or source code","no justified numeric drag handle"],
  "Formal/static representation is the intended success, preserving selection/source navigation without fabricated manipulation."),
]

def write_new(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare():
    PUBLIC.mkdir(parents=True,exist_ok=True)
    target=PRIVATE/'subsets';target.mkdir(exist_ok=True)
    manifest=[];expectations=[]
    for case in CASES:
        cid,sid,pages,coverage,publisher,title,terms,license,deep,stability,concepts,families,fixed,adjustable,unsupported,fallback=case
        original=PRIVATE/'originals'/(sid+'.pdf');out=target/(cid+'.pdf')
        reader=PdfReader(original);writer=PdfWriter()
        for n in pages:writer.add_page(reader.pages[n-1])
        writer.add_metadata({'/Title':title,'/Subject':'Exact bounded educational page subset; no source rewriting','/Author':publisher})
        with out.open('xb') as f:writer.write(f)
        manifest.append(dict(material_id=cid,coverage=coverage,publisher=publisher,title=title,
            source_url=SOURCES[sid],terms_url=terms,license=license,original_physical_pdf_pages=pages,
            evaluation_to_original_pages={str(i+1):n for i,n in enumerate(pages)},
            original_total_pages=len(reader.pages),original_sha256=sha(original),subset_sha256=sha(out),
            subset_bytes=out.stat().st_size,subset_path=str(out.relative_to(ROOT)),
            subset_method='pypdf add_page in exact listed order; page content unmodified; stable metadata',
            source_pdf_committed=False,deep=deep,stability=stability,
            unfamiliarity_evidence='No matching source URL/path found in prior tracked benchmark corpus; not the Day26 projectile source. No claim about all prior human reading.'))
        expectations.append(dict(material_id=cid,concepts_present=concepts,
            important_original_pdf_pages=pages,reasonable_families=families,
            interactive_plausibility=cid!='debugging',direct_manipulation_plausibility=cid in ('circular','harmonic','circuits'),
            fixed_quantities=fixed,adjustable_quantities=adjustable,unsupported_semantics=unsupported,static_degradation_conditions=fallback))
    now=datetime.now(timezone.utc).isoformat()
    write_new(PUBLIC/'corpus-manifest.json',dict(created_utc=now,materials=manifest,
        scope='Ten exact public educational subsets from four publishers. Physical PDF page numbers mapped to renumbered evaluation pages 1..N. Originals and subsets are ignored.',
        exclusions=['Day26 MIT projectile','OpenStax AI-ingestion-restricted materials','NASA photo/stock-credit pages','audio/code execution']))
    write_new(PUBLIC/'expectations-draft.json',dict(status='AGENT_DRAFT_PENDING_HUMAN_ADOPTION',created_utc=now,
        author='Codex prepared source-grounded draft; not represented as human-authored',
        language='en',deep_subset=['circular','harmonic','circuits','probability','spectrum'],
        stability_subset=['circular','harmonic','circuits','probability'],
        stability_protocol='Use one fixed main analysis. Three independent identical production representation declarations per selected case. Prefer selected spatial/probability compiler; if unavailable use the planner declaration. These are predeclared stability samples, never semantic retries. Preserve rejection outcomes. Three extra declaration requests after the first-pass pipeline; first-pass request not counted among the three.',
        scoring={'PASS':'Evidence supports required source semantics and truthful supported behavior.',
                 'PARTIAL':'Useful bounded result with identified missing semantics/capability/grounding.',
                 'FAIL':'Unusable, invented, unsafe, wrong ownership or materially misleading behavior.',
                 'NOT APPLICABLE':'Capability not justified by the source, or a correctly static case. Not a substitute for untested.'},
        expectations=expectations))
    lines=['# Day 27 prospective expectation packet — awaiting human adoption','',
       'No paid model requests have been made. This is an agent-prepared draft based on the actual source pages. The user requested a human-authored packet before inference; human adoption or corrections are required before freezing it. It is not yet `frozen-expectations.json`.','',
       'Deep: circular, harmonic, circuits, probability, spectrum. Stability: circular, harmonic, circuits, probability; three independent declarations on one stored analysis. Gold never enters model context.','']
    for c,e in zip(manifest,expectations):
        lines.extend(['## '+c['material_id']+' — '+c['title'],'',f"Publisher: {c['publisher']}. Original physical PDF pages: {c['original_physical_pdf_pages']}. Evaluation pages: 1–{len(c['original_physical_pdf_pages'])}.",
          f"[Source]({c['source_url']}) · [Terms]({c['terms_url']}) · {c['license']}.",
          '', 'Concepts: '+ '; '.join(e['concepts_present'])+'.',
          'Families: '+ '; '.join(e['reasonable_families'])+'.',
          'Fixed: '+ '; '.join(e['fixed_quantities'])+'.',
          'Adjustable: '+ '; '.join(e['adjustable_quantities'])+'.',
          'Forbidden inventions: '+ '; '.join(e['unsupported_semantics'])+'.',
          'Honest degradation: '+e['static_degradation_conditions'],''])
    (PUBLIC/'EXPECTATION_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    production={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in ROOT.rglob('*')
        if p.is_file() and p.suffix in ('.py','.html','.js','.css','.json')
        and not any(part.startswith('.') or part in ('tests','docs','__pycache__','node_modules') for part in p.relative_to(ROOT).parts)}
    write_new(PUBLIC/'prebenchmark-baseline.json',dict(starting_branch='day17-learning-scene-wip',
        starting_head='477de4926220d0960b58500f292ea6df24154da6',starting_origin_main='477de4926220d0960b58500f292ea6df24154da6',
        starting_tree='clean',branch_switch_reset_commit_push=False,model='gpt-6.1-sol',reasoning_effort='medium',
        spatial_version='2.3',full_regression=dict(command='python -X utf8 -B -m unittest discover -s tests -q',
           tests=458,seconds=251.025,result='OK',complete_prebenchmark_runs=1,
           log_sha256=sha(PRIVATE.parent/'.day26-local/day27-full-prebenchmark.log')),
        focused=dict(initial_tests=152,initial_failures=2,repaired_tests=41,seconds=14.775,result='OK'),
        production_file_hashes=production,production_fingerprint=hashlib.sha256(json.dumps(production,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        paid_response_requests_so_far=0,historical_trace_note='Complete regression temporarily rewrote three Day25 numeric traces; restored exactly from unchanged HEAD. Historical frozen declarations untouched.'))
    print('Frozen ten corpus subsets; AGENT_DRAFT expectation packet awaiting human adoption; paid requests=0.')

def freeze_approved_review():
    """Apply only the six explicit review adjustments received from the user."""
    draft_path=PUBLIC/'expectations-draft.json'
    expected_draft_sha='5ba3276ba1a12468428e100981766f1e3d9cc6ba9f84ff59da175c6a59e45ace'
    if sha(draft_path)!=expected_draft_sha:
        raise ValueError('Reviewed draft bytes changed; do not freeze unseen content.')
    outputs=[PUBLIC/name for name in ('frozen-expectations.json','expectation-freeze.json','FROZEN_EXPECTATION_SUMMARY.md')]
    if any(path.exists() for path in outputs):
        raise FileExistsError('Approved packet already exists; never overwrite frozen expectations.')
    packet=json.loads(draft_path.read_text(encoding='utf-8'))
    manifest_path=PUBLIC/'corpus-manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    previous_manifest_sha=sha(manifest_path)
    baseline=json.loads((PUBLIC/'prebenchmark-baseline.json').read_text(encoding='utf-8'))
    for name,digest in baseline['production_file_hashes'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Production baseline changed: '+name)
    for case in manifest['materials']:
        if sha(ROOT/case['subset_path'])!=case['subset_sha256']:
            raise ValueError('Public source subset changed: '+case['material_id'])
    now=datetime.now(timezone.utc).isoformat()
    packet.update(status='FROZEN_APPROVED_BEFORE_MODEL_EXECUTION',
        author='AI-drafted, human-reviewed and approved before model execution.',
        frozen_utc=now,review_date='2026-10-11',review_timezone='Asia/Taipei',
        approval_provenance='Direct user review of the ten-case table, with six final adjustments. Approval covers freezing expectations; paid API execution remains prohibited in this turn.',
        original_reviewed_draft_sha256=expected_draft_sha,
        deep_subset=['circular','harmonic','circuits','probability','search'])
    by_id={case['material_id']:case for case in packet['expectations']}
    by_id['circular']['adjustable_quantities']=[
        'positive radius',
        'angular velocity: signed or positive according to source direction/coordinate semantics; never infer its domain from the parameter ID or label']
    by_id['circular']['domain_semantics']={
        'radius':'positive',
        'angular_velocity':'Source-dependent signed or positive. A signed directional angular velocity is distinct from a positive angular-speed magnitude. Names alone do not establish either domain.'}
    for identifier in ('circular','harmonic','circuits'):
        case=by_id[identifier]
        case['adjustable_quantities']=[value for value in case['adjustable_quantities'] if value!='time']
        case['runtime_controlled_semantic_time']={
            'classification':'runtime-controlled semantic time',
            'ordinary_material_adjustable_parameter':False,
            'behavior':'Playback/scrubbing use the existing bounded canonical semantic clock and validated duration policy. Time is not a general adjustable teaching-material parameter.'}
    by_id['regression']['adjustable_quantities']=['prediction input inside observed range']
    by_id['regression']['unsupported_semantics']=[
        'no causal scholarship policy claim','no real student data reconstruction',
        'empirical points, source statistics and fitted results remain source facts; no adjustable hypothetical trial line unless explicitly supported by the original source']
    by_id['regression']['fixed_quantities'].append('all fitted results remain source facts, not freely adjustable parameters')
    packet['scoring']={
        'PASS':'核心教材語意正確、representation 合理、固定/可調判斷合理、沒有捏造來源或互動；適用時 runtime 可完成，不適用時能誠實降級。',
        'PARTIAL':'核心語意大致正確，但 grounding / representation / runtime 有明顯缺口，且不至於誤導學習者。',
        'FAIL':'核心教材語意錯誤、固定/可調判斷會誤導、捏造公式/來源/affordance，或應可完成的核心流程無法使用。',
        'NOT_APPLICABLE':'該能力依來源本來就不適用，例如 static case 沒有 direct manipulation。'}
    packet['assessment_axes']={
        'A':{'name':'semantic/source correctness',
             'criteria':['core source concepts and relationships','source page/evidence fidelity','fixed versus adjustable judgment','domain legality according to source meaning','no invented formulas, source facts or justified affordances'],
             'evidence_requirement':'Compare the actual declaration and displayed content against the frozen source expectations and original pages. Validator/compiler acceptance is not semantic correctness evidence.'},
        'B':{'name':'engineering/runtime result',
             'criteria':['appropriate supported compilation or honest degradation','canonical commit and atomic rejection','synchronized views and source roundtrip','source immutability','local interaction request delta and browser behavior'],
             'evidence_requirement':'Use validator/compiler/runtime/browser observations; report missing evidence separately.'}}
    packet['assessment_rules']=[
        'Report A and B independently for every case; never replace A with validator/compile PASS.',
        'NOT_APPLICABLE is source-based capability inapplicability, never a label for work not performed.',
        'A static/formal result can PASS when justified by the source; direct manipulation is not mandatory.',
        'No source-dependent angular-velocity domain guessing by parameter IDs, labels or topic names.',
        'Gold is never sent to the model; frozen expectations are never edited after model execution.']
    reasons={
        'circular':('Geometric/physical linked state, exact inverse ownership and source roundtrip.','Domain, parameter identity, ownership, inverse and duration-policy drift.'),
        'harmonic':('A second physical system with coupled quantities, phase and initial conditions.','Coupled declarations, fixed baseline, domain and inverse drift.'),
        'circuits':('Cross-domain engineering: waveform/initial-condition grounding and canonical numerical state.','Fixed source examples versus hypothetical controls; ranges, domains and representation drift.'),
        'probability':('Discrete shared membership/focus and source roundtrip; no geometric drag is required.','Outcome/event membership, ownership, source references and acceptance drift.'),
        'search':('Process/state capability and source roundtrip, with honest read-only fallback when execution is unsupported.',None),
        'signals':(None,None),'regression':(None,None),'complexity':(None,None),'spectrum':(None,None),'debugging':(None,None)}
    for case in packet['expectations']:
        identifier=case['material_id']
        case['deep']=identifier in packet['deep_subset']
        case['stability']=identifier in packet['stability_subset']
        case['deep_selection_reason'],case['stability_selection_reason']=reasons[identifier]
    # This only corrects pre-execution subset selection metadata. PDF/source
    # URLs, bytes, hashes, pages and production files remain unchanged.
    for case in manifest['materials']:
        case['deep']=case['material_id'] in packet['deep_subset']
        case['stability']=case['material_id'] in packet['stability_subset']
    manifest['selection_review_date']='2026-10-11'
    manifest['selection_authority']='frozen-expectations.json'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    packet['corpus_manifest_sha256']=sha(manifest_path)
    write_new(outputs[0],packet)
    lines=['# Day 27 — final frozen expectation summary','',packet['author'],'',
        'Approved and frozen following the user review on 2026-10-11 (Asia/Taipei), before model execution. Paid response requests: 0. Paid API execution remains prohibited in this turn.','',
        'Deep: circular, harmonic, circuits, probability, search. NASA spectrum remains breadth only.','',
        'Stability: circular, harmonic, circuits, probability; one stored main analysis, three independent identical declaration requests per case under the already reviewed protocol. No requests have been made.','',
        '## Independent assessment axes','',
        '- A. semantic/source correctness — source concepts, evidence, fixed/adjustable judgments, domains and absence of invented semantics.','- B. engineering/runtime result — supported compilation, canonical state, atomic rejection, synchronized views, source roundtrip and local request/browser evidence.','- Validator/compile PASS never substitutes for A. NOT_APPLICABLE never means untested.','',
        '## Predefined outcomes','']
    for label,definition in packet['scoring'].items():lines.append('- **'+label+'**: '+definition)
    lines+=['','## Final adjustments','',
        '- Circular angular velocity uses source direction/coordinate semantics to choose signed or positive; no name-based inference.',
        '- Circular, SHM and RC time is runtime-controlled semantic time, excluded from ordinary adjustable material parameters.',
        '- Regression permits only prediction input within the observed range by default. Empirical points, statistics and fitted results stay source facts; no hypothetical trial-line adjustment without explicit original-source support.',
        '- Deep fifth case is search, replacing NASA. Stability four cases are unchanged.','',
        '## Ten cases','',
        '| Case | Original physical PDF pages | Representation | Ordinary adjustable quantities / local operations | Deep | Stability |',
        '|---|---|---|---|---|---|']
    for case in packet['expectations']:
        pages=case['important_original_pdf_pages'];page_label=str(pages[0]) if len(pages)==1 else str(pages[0])+'–'+str(pages[-1])
        lines.append('| '+case['material_id']+' | '+page_label+' | '+'; '.join(case['reasonable_families'])+' | '+'; '.join(case['adjustable_quantities'])+' | '+('yes' if case['deep'] else 'no')+' | '+('yes' if case['stability'] else 'no')+' |')
    lines+=['','Full per-case concepts, fixed quantities, prohibited inventions, manipulation plausibility and fallback conditions are in `frozen-expectations.json`. Original AI draft remains unchanged for audit.','']
    with outputs[2].open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines))
    files={path.name:sha(path) for path in (manifest_path,outputs[0],outputs[2],PUBLIC/'prebenchmark-baseline.json')}
    package_sha=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    write_new(outputs[1],dict(status='FROZEN_BEFORE_MODEL_EXECUTION',frozen_utc=now,
        attribution=packet['author'],approved_by='User via direct conversation review, 2026-10-11 Asia/Taipei',
        original_reviewed_draft_sha256=expected_draft_sha,previous_corpus_manifest_sha256=previous_manifest_sha,
        files_sha256=files,package_sha256=package_sha,paid_response_requests_at_freeze=0,
        model_execution_authorized_this_turn=False,
        scope='Expectation/corpus/baseline package only. First-pass/deep/stability/result artifacts do not yet exist and are not claimed frozen.'))
    print(json.dumps(dict(frozen_expectations_sha256=sha(outputs[0]),package_sha256=package_sha,
        cases=len(packet['expectations']),deep=packet['deep_subset'],stability=packet['stability_subset'],
        paid_response_requests=0,production_hashes_verified=len(baseline['production_file_hashes'])),indent=2))

if __name__=='__main__':
    import sys
    if sys.argv[1:]==['--freeze-approved']:freeze_approved_review()
    elif not sys.argv[1:]:prepare()
    else:raise SystemExit('Use no arguments for draft preparation, or --freeze-approved for the recorded review only.')
