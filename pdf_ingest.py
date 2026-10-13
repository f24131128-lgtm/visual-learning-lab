"""Bounded fixed-code PDF worker; no model code, credentials or source filenames."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

PDF_WORKERS = threading.BoundedSemaphore(1)  # Local process admission, no queue.
WORKER = Path(__file__).resolve().with_name('pdf_worker.py')
MEMORY_BYTES = 512*1024*1024
TIMEOUT = 20


def windows_job(process):
    """Assign memory/process limits before sending the PDF to the child."""
    import ctypes
    from ctypes import wintypes as w
    class Basic(ctypes.Structure):
        _fields_=[('user',ctypes.c_int64),('job',ctypes.c_int64),('flags',w.DWORD),
                  ('min',ctypes.c_size_t),('max',ctypes.c_size_t),('active',w.DWORD),
                  ('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
    class IO(ctypes.Structure):_fields_=[(n,ctypes.c_uint64) for n in ('ro','wo','oo','rt','wt','ot')]
    class Extended(ctypes.Structure):
        _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),
                  ('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];kernel.CreateJobObjectW.restype=w.HANDLE
    kernel.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
    kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
    kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
    kernel.CloseHandle.argtypes=[w.HANDLE]
    handle=kernel.CreateJobObjectW(None,None)
    if not handle:raise ValueError('PDF resource boundary')
    # Windows venv python.exe is a redirector that launches the actual Python
    # child. Bound the whole job to the same 512 MiB, including both processes.
    info=Extended();info.basic.flags=0x100|0x200|0x2000|0x8
    info.basic.active=2;info.process_memory=MEMORY_BYTES;info.job_memory=MEMORY_BYTES
    child=kernel.OpenProcess(0x100|0x1|0x1000,False,process.pid)
    try:
        if not child or not kernel.SetInformationJobObject(handle,9,ctypes.byref(info),ctypes.sizeof(info)) or not kernel.AssignProcessToJobObject(handle,child):
            raise ValueError('PDF resource boundary')
    except Exception:
        kernel.CloseHandle(handle);raise
    finally:
        if child:kernel.CloseHandle(child)
    return lambda:kernel.CloseHandle(handle)


def run_worker(operation, data, **parameters):
    if operation not in ('inspect','extract','render','anchors') or not isinstance(data,bytes) or not 0<len(data)<=10*1024*1024:
        raise ValueError('PDF worker envelope')
    if not PDF_WORKERS.acquire(blocking=False):raise ValueError('PDF worker busy')
    process=None;release_job=lambda:None
    try:
        # Keep only runtime OS paths; no inherited API, DB, OIDC credentials or
        # arbitrary PYTHONPATH/sitecustomize. The CLI is fixed and shell=False.
        environment={n:os.environ[n] for n in ('SYSTEMROOT','WINDIR','TEMP','TMP','PATH','LANG') if n in os.environ}
        environment.update(VLL_LIVE_AI='',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
        process=subprocess.Popen([sys.executable,'-I','-B',str(WORKER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,env=environment,cwd=str(WORKER.parent),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        if os.name=='nt':release_job=windows_job(process)
        request=json.dumps(dict(operation=operation,data=base64.b64encode(data).decode(),parameters=parameters)).encode()
        output,_=process.communicate(request,timeout=TIMEOUT)
        if process.returncode!=0 or len(output)>8*1024*1024:raise ValueError('PDF worker rejected')
        result=json.loads(output)
        if result.get('ok') is not True:raise ValueError('PDF worker rejected')
        value=result['value']
        if operation=='render':value['png']=base64.b64decode(value['png'],validate=True)
        if operation=='extract':value['analyzed_page_texts']={int(k):v for k,v in value['analyzed_page_texts'].items()}
        return value
    except Exception:
        raise ValueError('PDF worker unavailable or rejected') from None
    finally:
        if process is not None:
            if process.poll() is None:process.kill()
            process.wait()
            for pipe in (process.stdin,process.stdout):
                if pipe is not None:pipe.close()
        release_job();PDF_WORKERS.release()
