"""Observer controls are offline; no learner/production logic changed."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock,patch
import day27_benchmark as benchmark

class ObserverTests(unittest.TestCase):
    def kwargs(self):
        return dict(model='gpt-6.1-sol',reasoning={'effort':'medium'},input='bounded public context',
            text={'format':dict(name='test',strict=True,schema={'type':'object','properties':{},'additionalProperties':False})})
    def observer(self,tmp):
        with patch.object(benchmark,'PRIVATE',Path(tmp)):
            observer=benchmark.Observer(True)
        observer.case='offline';observer.stage='first-analysis'
        observer.client=MagicMock()
        observer.client.responses.create.return_value=SimpleNamespace(output_text='{}',status='completed',id='offline_response',model='gpt-6.1-sol',usage=None)
        return observer
    def test_one_attempt_then_exact_recorded_reuse(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(benchmark,'verify'):
            observer=self.observer(tmp);kwargs=self.kwargs()
            observer.create(**kwargs);observer.create(**kwargs)
            self.assertEqual(observer.client.responses.create.call_count,1)
            self.assertTrue(observer.path('.output.txt').exists())
            record=benchmark.read(observer.path('.json'))
            self.assertTrue(record['schema_valid']);self.assertEqual(record['semantic_retries'],0)
            kwargs['input']='changed context'
            with self.assertRaises(ValueError):observer.create(**kwargs)
            self.assertEqual(observer.client.responses.create.call_count,1)
    def test_failed_transport_never_retries(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(benchmark,'verify'):
            observer=self.observer(tmp)
            observer.client.responses.create.side_effect=TimeoutError('private sentinel must not be logged')
            with self.assertRaises(TimeoutError):observer.create(**self.kwargs())
            with self.assertRaises(RuntimeError):observer.create(**self.kwargs())
            self.assertNotIn('private sentinel',observer.path('.json').read_text())
            self.assertEqual(observer.client.responses.create.call_count,1)
    def test_local_and_wrong_model_calls_blocked_before_request(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(benchmark,'verify'):
            observer=self.observer(tmp);observer.local=True
            with self.assertRaises(AssertionError):observer.create(**self.kwargs())
            observer.local=False;kwargs=self.kwargs();kwargs['model']='old-model'
            with self.assertRaises(ValueError):observer.create(**kwargs)
            observer.client.responses.create.assert_not_called()
    def test_frozen_write_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'frozen.json';benchmark.write_new(path,{'original':True})
            with self.assertRaises(FileExistsError):benchmark.write_new(path,{'original':False})
            self.assertEqual(benchmark.read(path),{'original':True})
    def test_reference_report_preserves_invalid_raw_refs(self):
        report=benchmark.references({'source_pages':[1,9,True]},[1])
        self.assertFalse(report['valid']);self.assertEqual([r['page'] for r in report['invalid']],[9,True])

if __name__=='__main__':unittest.main()
