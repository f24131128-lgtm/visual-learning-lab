"""Stage product-only source and measure no-key clean AppTest smoke."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'.day29-local/clean'
MODULES=('analogy','document_intelligence','learning_world','manipulation','scene','source_atlas','workspace','prepared')


def stage():
    TARGET.mkdir(parents=True,exist_ok=True)
    for file in ROOT.glob('*.py'):shutil.copy2(file,TARGET/file.name)
    for folder in MODULES:
        shutil.copytree(ROOT/folder,TARGET/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    (TARGET/'.streamlit').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'.streamlit/config.toml',TARGET/'.streamlit/config.toml')
    for name in ('requirements.txt','README.md','THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT/name,TARGET/name)


def smoke():
    os.environ.pop('VLL_LIVE_AI',None);os.environ.pop('OPENAI_API_KEY',None)
    os.chdir(TARGET);sys.path.insert(0,str(TARGET))
    from streamlit.testing.v1 import AppTest
    from unittest.mock import patch
    from prepared_demo import prepare
    measured={}
    with patch('openai.resources.responses.Responses.create',side_effect=AssertionError('No paid calls')) as requests, \
         patch('openai.resources.files.Files.create',side_effect=AssertionError('No uploads')) as files:
        start=time.perf_counter();a=AppTest.from_file(str(TARGET/'app.py'),default_timeout=40).run();measured['cold_homepage_seconds']=time.perf_counter()-start
        assert not a.exception
        assert a.button(key='analyze-material').disabled
        start=time.perf_counter();a.run();measured['warm_homepage_seconds']=time.perf_counter()-start
        start=time.perf_counter();a.button(key='prepared-open').click().run();measured['prepared_load_seconds']=time.perf_counter()-start
        assert not a.exception and a.session_state['analysis']
        material=a.session_state['analysis_id'];source=a.session_state['source_context'];pdf=a.session_state['learning_canvas']['source']['pdf_bytes']
        start=time.perf_counter();a.radio(key='workspace-mode-'+material).set_value('source').run();measured['source_navigation_seconds']=time.perf_counter()-start
        assert not a.exception
        for box in a.selectbox:
            if box.key and str(box.key).startswith('workspace-control-concept-'):box.select('amplitude_phase').run()
        button=a.button(key='workspace-source-controls')
        button.click().run();assert not a.exception
        start=time.perf_counter();slider=next(s for s in a.slider if 'trial_amplitude' in s.key);before=slider.value;slider.set_value(before-.1).run();measured['parameter_update_seconds']=time.perf_counter()-start
        assert not a.exception
        back=a.button(key='workspace-controls-source')
        back.click().run();assert not a.exception
        assert a.session_state['source_context']==source and a.session_state['learning_canvas']['source']['pdf_bytes']==pdf
        measured.update(request_calls=requests.call_count,file_calls=files.call_count,source_immutable=True)
    measured.update(python=sys.version,isolated_prefix=sys.prefix,hidden_test_directory_present=(TARGET/'tests').exists(),
        ignored_corpus_present=(TARGET/'.day27-local').exists(),pymupdf_available=importlib.util.find_spec('pymupdf') is not None,
        optional_pdfplumber_available=importlib.util.find_spec('pdfplumber') is not None)
    try:
        import ctypes
        # Process Working Set, not Python allocations. Windows-only measurement.
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
        counters=Counters();counters.cb=ctypes.sizeof(counters)
        ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
        if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(ctypes.windll.kernel32.GetCurrentProcess()),ctypes.byref(counters),counters.cb):
            measured.update(process_working_set_bytes=counters.WorkingSetSize,process_peak_working_set_bytes=counters.PeakWorkingSetSize)
    except Exception:pass
    (ROOT/'docs/day29/clean-smoke-results.json').write_text(json.dumps(measured,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(measured))


if __name__=='__main__':
    stage()
    if '--stage-only' not in sys.argv:smoke()
