"""Offline public admission, durable accounting and root-app regression."""
import ast
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest
from paid_policy import Ledger, AdmissionDenied, BUDGET, RESERVATION, conservative_charge
from public_access import PublicConfig, principal, configuration
from metered_client import MeteredClient
from model_config import response_options
from production_safety import checked_pdf
from support import ROOT, fixture, sample_pdf


def completed(i=1000,o=100):
    return SimpleNamespace(status='completed',model='gpt-6.1-sol',service_tier='default',
                           output_text=json.dumps(fixture()),usage=SimpleNamespace(input_tokens=i,output_tokens=o))


def options():return dict(response_options(),instructions='Fixed instructions',input='Source',text={})


class LedgerFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'ledger.sqlite'
        self.connect=lambda:sqlite3.connect(self.db,timeout=3)
        self.store=Ledger(self.connect,'offline-policy','sqlite');self.store.initialize()
        self.person=hashlib.sha256(b'account A').hexdigest()
    def tearDown(self):self.tmp.cleanup()
    def finish(self,action='analysis',person=None,charge=1000):
        r=self.store.reserve(person or self.person,action);self.assertTrue(self.store.finish(r,charge));return r
    def client(self,action='analysis'):
        raw=MagicMock();raw.responses.create.return_value=completed();raw.files.create.return_value=SimpleNamespace(id='file-offline')
        return MeteredClient(raw,self.store,self.person,action),raw


class DurableCase(LedgerFixture):
    def test_restart_and_second_connection_cannot_reset_person(self):
        self.finish();self.finish()
        second=Ledger(self.connect,'offline-policy','sqlite')
        with self.assertRaisesRegex(AdmissionDenied,'personal_exhausted'):second.reserve(self.person,'analysis')
        self.assertEqual(second.inspect(self.person)['analyses'],2)

    def test_secondary_paths_share_six_generation_quota(self):
        for action in ('explain','review','scene','atlas','planner','analogy'):self.finish(action)
        with self.assertRaisesRegex(AdmissionDenied,'personal_exhausted'):self.store.reserve(self.person,'simulation')
        self.assertEqual(self.store.inspect(self.person)['generations'],6)

    def test_global_daily_quota_across_accounts(self):
        for n in range(20):self.finish(person=hashlib.sha256(str(n).encode()).hexdigest())
        with self.assertRaisesRegex(AdmissionDenied,'daily_exhausted'):self.store.reserve(self.person,'explain')

    def test_atomic_concurrency_across_connections(self):
        def admit(n):
            try:return Ledger(self.connect,'offline-policy','sqlite').reserve(hashlib.sha256(str(n).encode()).hexdigest(),'analysis')
            except AdmissionDenied:return None
        with ThreadPoolExecutor(max_workers=8) as executor:results=list(executor.map(admit,range(8)))
        winners=[r for r in results if r is not None]
        self.assertEqual(len(winners),1)
        self.assertEqual(self.store.inspect(self.person)['remaining'],BUDGET-RESERVATION)
        self.store.finish(winners[0],1000)

    def test_budget_reservation_checks_worst_case_before_call(self):
        self.finish(charge=3_000_001)
        with self.assertRaisesRegex(AdmissionDenied,'budget_exhausted'):self.store.reserve(self.person,'analysis')
        self.assertGreater(self.store.inspect(self.person)['remaining'],0)

    def test_pending_crash_and_uncertain_timeout_never_expire(self):
        r=self.store.reserve(self.person,'analysis')
        second=Ledger(self.connect,'offline-policy','sqlite')
        with self.assertRaises(AdmissionDenied):second.reserve(self.person,'analysis')
        self.assertFalse(second.finish(r))
        self.assertTrue(second.inspect(self.person)['paused'])
        self.assertFalse(second.finish(r,0))
        self.assertEqual(second.inspect(self.person)['remaining'],BUDGET-RESERVATION)

    def test_duplicate_finish_cannot_refund_or_release_twice(self):
        r=self.finish(charge=1000)
        self.assertFalse(self.store.finish(r,0))
        self.assertEqual(self.store.inspect(self.person)['remaining'],BUDGET-1000)

    def test_missing_store_and_policy_change_fail_closed(self):
        with self.assertRaises(AdmissionDenied):Ledger(self.connect,'changed-key','sqlite').reserve(self.person,'analysis')
        with self.assertRaises(AdmissionDenied):self.store.initialize()
        missing=Ledger(lambda:sqlite3.connect(Path(self.tmp.name)/'missing.sqlite'),'x','sqlite')
        with self.assertRaises(AdmissionDenied):missing.reserve(self.person,'analysis')

    def test_price_expiry_closes_admission(self):
        original=self.store.sql
        def future(c,statement,args=()):
            if statement=='SELECT CURRENT_DATE':return SimpleNamespace(fetchone=lambda:('2030-01-01',))
            return original(c,statement,args)
        self.store.sql=future
        with self.assertRaisesRegex(AdmissionDenied,'pricing_review_required'):self.store.reserve(self.person,'analysis')

    def test_bad_identity_action_or_charge_cannot_create_credit(self):
        for person,action in [('session-id','analysis'),(self.person,'shell')]:
            with self.assertRaises(AdmissionDenied):self.store.reserve(person,action)
        r=self.store.reserve(self.person,'analysis');self.assertFalse(self.store.finish(r,-1))
        self.assertEqual(self.store.inspect(self.person)['remaining'],BUDGET-RESERVATION)

    def test_success_charged_conservatively_no_retry(self):
        client,raw=self.client();response=client.responses.create(**options())
        self.assertIs(response,raw.responses.create.return_value)
        self.assertEqual(raw.responses.create.call_count,1)
        self.assertEqual(raw.responses.create.call_args.kwargs['service_tier'],'default')
        self.assertEqual(self.store.inspect(self.person)['remaining'],BUDGET-conservative_charge(response))

    def test_every_action_uses_same_admission(self):
        for action in ('analysis','explain','review','scene','atlas','planner','analogy','simulation'):
            self.person=hashlib.sha256(action.encode()).hexdigest()
            client,raw=self.client(action);client.responses.create(**options());raw.responses.create.assert_called_once()
        self.assertEqual(self.store.inspect(self.person)['daily'],8)

    def test_paid_error_keeps_full_reservation_and_blocks_next_call(self):
        client,raw=self.client();raw.responses.create.side_effect=TimeoutError('secret-canary')
        with self.assertRaises(AdmissionDenied) as error:client.responses.create(**options())
        self.assertNotIn('secret-canary',str(error.exception));self.assertEqual(raw.responses.create.call_count,1)
        next_client,next_raw=self.client()
        with self.assertRaises(AdmissionDenied):next_client.responses.create(**options())
        next_raw.responses.create.assert_not_called()
        self.assertEqual(self.store.inspect(self.person)['remaining'],BUDGET-RESERVATION)

    def test_unknown_usage_retains_charge_and_pauses(self):
        client,raw=self.client();raw.responses.create.return_value=SimpleNamespace(status='completed',usage=None)
        with self.assertRaises(AdmissionDenied):client.responses.create(**options())
        self.assertTrue(self.store.inspect(self.person)['paused'])

    def test_forbidden_options_remote_files_tools_and_url_before_upstream(self):
        for patch_options in [dict(model='other'),dict(max_output_tokens=999999),dict(store=True),dict(tools=[]),
                dict(stream=True),dict(service_tier='priority'),dict(reasoning={'effort':'high'}),
                dict(input=[{'role':'user','content':[{'type':'input_file','file_id':'file-foreign'}]}]),
                dict(input=[{'role':'user','content':[{'type':'input_image','image_url':'https://invalid.example'}]}])]:
            client,raw=self.client();value=options();value.update(patch_options)
            with self.assertRaises(AdmissionDenied):client.responses.create(**value)
            raw.responses.create.assert_not_called()
        self.assertEqual(self.store.inspect(self.person)['daily'],0)

    def test_pdf_upload_is_reserved_once_expires_and_deletes(self):
        client,raw=self.client()
        from pypdf import PdfReader,PdfWriter
        writer=PdfWriter();writer.add_page(PdfReader(io.BytesIO(sample_pdf())).pages[0]);stream=io.BytesIO();writer.write(stream)
        data=stream.getvalue();client.files.create(file=('uploaded.pdf',data,'application/pdf'),purpose='user_data')
        self.assertEqual(self.store.inspect(self.person)['daily'],1)
        value=options();value['input']=[{'role':'user','content':[{'type':'input_file','file_id':'file-offline'}]}]
        client.responses.create(**value)
        self.assertEqual(self.store.inspect(self.person)['daily'],1)
        raw.files.delete.assert_called_once_with('file-offline')
        self.assertEqual(raw.files.create.call_args.kwargs['expires_after']['seconds'],3600)

    def test_small_pdf_limit_before_reservation_or_upload(self):
        from pypdf import PdfWriter
        writer=PdfWriter()
        for _ in range(3):writer.add_blank_page(100,100)
        stream=io.BytesIO();writer.write(stream)
        for data in (stream.getvalue(),b'%PDF-'+b'x'*(2*1024*1024)):
            client,raw=self.client()
            with self.assertRaises(ValueError):client.files.create(file=('uploaded.pdf',data,'application/pdf'),purpose='user_data')
            raw.files.create.assert_not_called()
        self.assertEqual(self.store.inspect(self.person)['daily'],0)

    def test_atlas_native_rasters_accept_bounded_detail(self):
        client,raw=self.client('atlas');value=options()
        value['input']=[{'role':'user','content':[{'type':'input_image','image_url':'data:image/png;base64,AA==','detail':'high'}]}]
        client.responses.create(**value);raw.responses.create.assert_called_once()


class ConfigurationTests(unittest.TestCase):
    def config(self):return PublicConfig('synthetic-private','proj_offline','postgresql://localhost/offline','https://issuer.example','s'*32)

    def google_secrets(self):
        return dict(public_ai=dict(api_key='synthetic-private',project_id='proj_offline',
                    ledger_dsn='postgresql://localhost/offline',identity_issuer='https://accounts.google.com',
                    quota_hmac_secret='s'*32,dedicated_project_verified=True,budget_microusd=BUDGET,
                    price_review_date='2026-10-13'),
                    auth=dict(redirect_uri='https://staging.example/oauth2callback',cookie_secret='c'*32,
                    client_id='synthetic.apps.googleusercontent.com',client_secret='synthetic-client-secret',
                    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',expose_tokens=[]))

    def test_google_configuration_accepts_only_matching_provider_and_https_callback(self):
        valid=self.google_secrets()
        with patch('streamlit.secrets',valid):self.assertEqual(configuration().issuer,'https://accounts.google.com')
        for section,key,value in [('public_ai','identity_issuer','https://issuer.example'),
                ('auth','server_metadata_url','https://issuer.example/.well-known/openid-configuration'),
                ('auth','client_id','other-provider'),('auth','client_secret',True),
                ('auth','redirect_uri','http://staging.example/oauth2callback'),
                ('auth','redirect_uri','https://staging.example/wrong'),
                ('auth','redirect_uri','https://staging.example/oauth2callback?token=bad'),
                ('auth','redirect_uri','https://user:password@staging.example/oauth2callback'),
                ('auth','expose_tokens',['id']),('public_ai','budget_microusd',BUDGET+1)]:
            invalid=copy.deepcopy(valid);invalid[section][key]=value
            with self.subTest(section=section,key=key,value=value),patch('streamlit.secrets',invalid):
                with self.assertRaisesRegex(AdmissionDenied,'configuration_required'):configuration()

    def test_two_google_subjects_are_isolated_and_session_changes_do_not_reset_identity(self):
        with patch('streamlit.secrets',self.google_secrets()):config=configuration()
        def identity(subject,email):
            user=SimpleNamespace(is_logged_in=True,get={'iss':config.issuer,'sub':subject,'email':email}.get)
            with patch('streamlit.user',user):return principal(config)
        first=identity('account-a','old@example.test')
        self.assertEqual(first,identity('account-a','new@example.test'))
        self.assertNotEqual(first,identity('account-b','old@example.test'))

    def test_verified_subject_persists_without_email_or_session_id(self):
        config=self.config();user=SimpleNamespace(is_logged_in=True,get=lambda k: {'iss':config.issuer,'sub':'stable-user'}.get(k))
        with patch('streamlit.user',user):a=principal(config);b=principal(config)
        self.assertEqual(a,b);self.assertEqual(len(a),64);self.assertNotIn('stable-user',a)

    def test_forged_wrong_issuer_missing_subject_or_expired_identity(self):
        for claims in ({'iss':'wrong','sub':'user'},{'iss':self.config().issuer},*[
                {'iss':self.config().issuer,'sub':'u','exp':exp} for exp in (0,float('nan'),float('inf'))]):
            with patch('streamlit.user',SimpleNamespace(is_logged_in=True,get=claims.get)):
                with self.assertRaises(AdmissionDenied):principal(self.config())
        with patch('streamlit.user',SimpleNamespace(is_logged_in=False)):
            with self.assertRaises(AdmissionDenied):principal(self.config())

    def test_secret_repr_and_fingerprint_changes(self):
        value=self.config();self.assertNotIn('synthetic-private',repr(value));self.assertNotIn(value.salt,repr(value))
        altered=PublicConfig(value.api_key,value.project,value.dsn,value.issuer,'x'*32)
        self.assertNotEqual(value.fingerprint,altered.fingerprint)

    def test_cost_bounds_reasoning_rounding_and_unknown(self):
        self.assertEqual(conservative_charge(completed(1,0)),6)
        self.assertLess(conservative_charge(completed(1_050_000,16_000)),RESERVATION)
        for value in [completed(-1,0),completed(1,16_001),completed(True,1),SimpleNamespace(status='incomplete')]:
            self.assertIsNone(conservative_charge(value))
        unknown=completed();unknown.model='gpt-6.1-sol-ultrafast'
        self.assertIsNone(conservative_charge(unknown))

    def test_constructor_ignores_legacy_key_and_forces_project_transport(self):
        import production_safety
        config=self.config();store=MagicMock()
        with patch.dict(os.environ,{'VLL_LIVE_AI':'limited-public'}),patch('public_access.configuration',return_value=config),patch('public_access.principal',return_value='a'*64),patch('public_access.ledger',return_value=store),patch('openai.OpenAI') as sdk:
            client=production_safety.create_client(api_key='legacy-key',base_url='https://evil.example',max_retries=900,action='review')
            self.assertIsInstance(client,MeteredClient)
            args=sdk.call_args.kwargs
            self.assertEqual(args['api_key'],config.api_key);self.assertEqual(args['project'],config.project)
            self.assertEqual(args['base_url'],'https://api.openai.com/v1');self.assertEqual(args['max_retries'],0)

    def test_configuration_missing_ledger_never_falls_back_to_legacy(self):
        with patch('streamlit.secrets',{'OPENAI_API_KEY':'synthetic-legacy'}):
            with self.assertRaises(AdmissionDenied):configuration()

    def test_all_eight_owned_constructors_have_actions(self):
        actions=[]
        for name in ['app.py','scene/compiler.py','source_atlas/compiler.py','dynamic_simulation.py','learning_world/runtime.py','analogy/runtime.py']:
            tree=ast.parse((ROOT/name).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='OpenAI':
                    self.assertEqual(len(node.keywords),1)
                    self.assertEqual(node.keywords[0].arg,'action');actions.append(node.keywords[0].value.value)
        self.assertEqual(sorted(actions),sorted(['analysis','explain','review','scene','atlas','planner','analogy','simulation']))


class WorkerTests(unittest.TestCase):
    def data(self):
        from pypdf import PdfReader,PdfWriter
        writer=PdfWriter();writer.add_page(PdfReader(io.BytesIO(sample_pdf())).pages[0])
        stream=io.BytesIO();writer.write(stream);return stream.getvalue()

    def test_public_extract_raster_native_anchor_and_no_credentials_in_child(self):
        import pdf_ingest
        from pdf_renderer import render,anchors
        original=pdf_ingest.subprocess.Popen;environments=[]
        def launch(*args,**kwargs):environments.append(kwargs['env']);return original(*args,**kwargs)
        with patch.dict(os.environ,{'VLL_LIVE_AI':'limited-public','OPENAI_API_KEY':'synthetic-child-canary','DATABASE_URL':'synthetic-db-canary'}),patch('pdf_ingest.subprocess.Popen',side_effect=launch):
            text=pdf_ingest.run_worker('extract',self.data(),name='uploaded.pdf',mime='application/pdf')
            raster=render(self.data(),1,144,1800)
            boxes=anchors(self.data(),1,'Incoming material enters the process.')
        self.assertEqual(text['analyzed_page_numbers'],[1]);self.assertIn('Incoming material',text['text'])
        self.assertTrue(raster['png'].startswith(b'\x89PNG'));self.assertTrue(boxes)
        for env in environments:
            self.assertNotIn('OPENAI_API_KEY',env);self.assertNotIn('DATABASE_URL',env);self.assertNotIn('PYTHONPATH',env)

    def test_worker_timeout_kills_child_and_releases_slot(self):
        import pdf_ingest
        fake=MagicMock();fake.communicate.side_effect=pdf_ingest.subprocess.TimeoutExpired('fixed-worker',20)
        fake.poll.return_value=None
        with patch('pdf_ingest.subprocess.Popen',return_value=fake),patch('pdf_ingest.windows_job',return_value=lambda:None):
            with self.assertRaises(ValueError):pdf_ingest.run_worker('inspect',self.data())
        fake.kill.assert_called_once();fake.wait.assert_called_once()
        self.assertTrue(pdf_ingest.PDF_WORKERS.acquire(blocking=False));pdf_ingest.PDF_WORKERS.release()

    def test_compressed_600_mib_page_rejected_inside_memory_boundary(self):
        import zlib
        from pypdf import PdfWriter
        from pypdf.generic import EncodedStreamObject,NameObject,DictionaryObject
        from pdf_ingest import run_worker
        compressor=zlib.compressobj();chunks=[compressor.compress(b'BT /F1 12 Tf (')];chunk=b'x'*(1024*1024)
        for _ in range(600):chunks.append(compressor.compress(chunk))
        chunks.append(compressor.compress(b') Tj ET'));chunks.append(compressor.flush())
        stream=EncodedStreamObject();stream._data=b''.join(chunks);stream[NameObject('/Filter')]=NameObject('/FlateDecode')
        writer=PdfWriter();page=writer.add_blank_page(100,100);page[NameObject('/Contents')]=writer._add_object(stream)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        output=io.BytesIO();writer.write(output);self.assertLess(len(output.getvalue()),2*1024*1024)
        with self.assertRaises(ValueError):run_worker('extract',output.getvalue(),name='uploaded.pdf',mime='application/pdf')


class DeploymentBoundaryTests(unittest.TestCase):
    def test_postgres_transaction_locks_policy_and_uses_bound_parameters(self):
        connection=MagicMock();connection.execute.return_value.fetchone.return_value=('fingerprint',BUDGET,0,False)
        store=Ledger(lambda:connection,'fingerprint')
        with store.transaction() as current:
            store.policy(current);store.sql(current,'SELECT ?',(42,))
        statements=[call.args for call in connection.execute.call_args_list]
        self.assertIn(("SET LOCAL TIME ZONE 'UTC'",),statements)
        self.assertIn(("SET LOCAL lock_timeout = '2000ms'",),statements)
        self.assertIn(('SELECT fingerprint,budget,committed,paused FROM vll_paid_policy WHERE id=1 FOR UPDATE',()),statements)
        self.assertIn(('SELECT %s',(42,)),statements);connection.close.assert_called_once()

    def test_production_driver_requires_verified_tls_and_fails_closed(self):
        from public_access import ledger
        config=ConfigurationTests().config()
        connect=MagicMock(side_effect=RuntimeError('secret-dsn-canary'))
        with patch.dict(sys.modules,{'psycopg':SimpleNamespace(connect=connect)}):
            with self.assertRaises(AdmissionDenied) as error:ledger(config).inspect('a'*64)
        self.assertNotIn('secret-dsn-canary',str(error.exception))
        self.assertEqual(connect.call_args.kwargs,dict(connect_timeout=3,sslmode='verify-full',sslrootcert='system'))

    def test_real_sdk_multipart_expiry_and_single_attempt_with_mock_transport(self):
        # Isolated process keeps the suite's external request guard intact.
        # MockTransport has no socket/network access; real SDK serialization is
        # tested, including a 429 and max_retries=0.
        script='''
import httpx
from openai import OpenAI, RateLimitError
seen=[]
def handler(request):
 seen.append(request)
 assert request.headers['OpenAI-Project']=='proj_offline'
 body=request.read()
 assert b'expires_after[anchor]' in body and b'created_at' in body
 assert b'expires_after[seconds]' in body and b'3600' in body
 return httpx.Response(429,json={'error':{'message':'offline','type':'rate_limit_error'}})
with OpenAI(api_key='synthetic-offline',project='proj_offline',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(handler))) as client:
 try:client.files.create(file=('uploaded.pdf',b'%PDF-offline','application/pdf'),purpose='user_data',expires_after={'anchor':'created_at','seconds':3600})
 except RateLimitError:pass
assert len(seen)==1
print('mock SDK transport: one attempt, expiry serialized, no network')
'''
        result=subprocess.run([sys.executable,'-I','-B','-c',script],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr[-1200:]);self.assertIn('no network',result.stdout)


class PublicAppTests(LedgerFixture):
    def test_paid_off_accepts_google_verification_without_enabling_any_request(self):
        secrets=ConfigurationTests().google_secrets()
        user=SimpleNamespace(is_logged_in=True,get={'iss':'https://accounts.google.com','sub':'google-account'}.get)
        for logged_in in (False,True):
            active=user if logged_in else SimpleNamespace(is_logged_in=False)
            with self.subTest(logged_in=logged_in),patch.dict(os.environ,{'VLL_LIVE_AI':''}),patch('streamlit.user',active),patch('public_access.ledger',return_value=self.store),patch('openai.OpenAI') as sdk:
                app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
                app.secrets.clear();app.secrets.update(secrets);app.run()
                self.assertFalse(app.exception);self.assertTrue(app.button(key='analyze-material').disabled)
                if logged_in:
                    self.assertEqual(len(app.success),1)
                    self.assertTrue(any('帳本已驗證' in x.value for x in app.caption))
                    self.assertEqual(self.store.inspect('a'*64)['daily'],0)
                else:self.assertIsNotNone(app.button(key='public-sign-in'))
                app.button(key='prepared-open').click().run();self.assertFalse(app.exception)
                self.assertTrue(app.session_state['prepared_demo']);sdk.assert_not_called()

    def test_not_configured_public_mode_prepared_always_works(self):
        with patch.dict(os.environ,{'VLL_LIVE_AI':'limited-public'}),patch('openai.OpenAI') as sdk:
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30);app.secrets.clear();app.run()
            self.assertFalse(app.exception);self.assertTrue(app.button(key='analyze-material').disabled)
            app.button(key='prepared-open').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.session_state['analysis']);sdk.assert_not_called()

    def test_verified_public_main_response_and_then_exhausted_prepared(self):
        config=PublicConfig('offline-only','proj_offline','postgresql://localhost/offline','https://issuer.example','s'*32)
        raw=MagicMock();raw.responses.create.return_value=completed()
        with patch.dict(os.environ,{'VLL_LIVE_AI':'limited-public'}),patch('public_access.configuration',return_value=config),patch('public_access.principal',return_value=self.person),patch('public_access.ledger',return_value=self.store),patch('openai.OpenAI',return_value=raw):
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30);app.secrets.clear();app.run()
            self.assertFalse(app.exception);self.assertFalse(app.button(key='analyze-material').disabled)
            app.text_area(key='material-text').set_value('User source for the offline public-path regression.')
            app.button(key='analyze-material').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.session_state['analysis']);raw.responses.create.assert_called_once()
            source=copy.deepcopy(app.session_state['source_context'])
            with closing(self.connect()) as c:
                with c:c.execute('UPDATE vll_paid_policy SET committed=? WHERE id=1',(BUDGET,))
            app.session_state['_public_gate']={};app.run()
            self.assertTrue(app.button(key='analyze-material').disabled)
            self.assertEqual(app.session_state['source_context'],source)
            app.button(key='prepared-open').click().run()
            self.assertFalse(app.exception);self.assertTrue(app.session_state['prepared_demo'])
            self.assertEqual(raw.responses.create.call_count,1)


if __name__=='__main__':unittest.main()
