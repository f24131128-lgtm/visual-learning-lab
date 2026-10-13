"""Only public SDK surface: bounded file upload and one metered Responses call."""
import json
from paid_policy import AdmissionDenied, conservative_charge


class ResponseEndpoint:
    def __init__(self, owner):self.owner=owner
    def create(self, **kwargs):return self.owner.respond(kwargs)


class FileEndpoint:
    def __init__(self, owner):self.owner=owner
    def create(self, **kwargs):return self.owner.upload(kwargs)


class MeteredClient:
    def __init__(self, raw, ledger, principal, action):
        self._raw,self._ledger,self._principal,self._action=raw,ledger,principal,action
        self._reservation=None
        self._file_ids=set()
        self.responses,self.files=ResponseEndpoint(self),FileEndpoint(self)

    def admit(self):
        if self._reservation is None:self._reservation=self._ledger.reserve(self._principal,self._action)

    def invalidate_ui(self):
        try:
            import streamlit as st
            st.session_state.pop('_public_gate',None)
        except Exception:pass

    def uncertain(self):
        if self._reservation is not None:
            self._ledger.finish(self._reservation)
        self.invalidate_ui()

    def upload(self, options):
        from production_safety import checked_pdf
        if self._action!='analysis' or self._file_ids or set(options)!={'file','purpose'} or options['purpose']!='user_data':
            raise AdmissionDenied('file_forbidden')
        file=options['file']
        if not isinstance(file,tuple) or len(file)!=3 or file[0]!='uploaded.pdf' or file[2]!='application/pdf':
            raise AdmissionDenied('file_forbidden')
        checked_pdf(file[1],file[0],file[2],public=True)
        self.admit()
        try:
            result=self._raw.files.create(**options,expires_after={'anchor':'created_at','seconds':3600})
            if not isinstance(result.id,str) or not result.id.startswith('file-') or len(result.id)>160:
                raise AdmissionDenied('file_forbidden')
            self._file_ids.add(result.id)
            return result
        except Exception:
            self.uncertain()
            raise AdmissionDenied('request_unavailable') from None

    def cleanup(self):
        for identifier in self._file_ids:
            try:self._raw.files.delete(identifier)
            except Exception:pass  # Expiry remains the bounded fallback; no retry.
        self._file_ids.clear()

    def respond(self, options):
        from production_safety import MAX_OUTPUT_TOKENS
        try:
            allowed={'model','reasoning','max_output_tokens','store','instructions','input','text'}
            if set(options)-allowed or options.get('model')!='gpt-6.1-sol' or options.get('store') is not False:
                raise AdmissionDenied('request_forbidden')
            cap=options.get('max_output_tokens')
            if type(cap) is not int or not 1<=cap<=MAX_OUTPUT_TOKENS or options.get('reasoning')!={'effort':'medium'}:
                raise AdmissionDenied('request_forbidden')
            if len(json.dumps(options,ensure_ascii=False).encode())>12*1024*1024:
                raise AdmissionDenied('request_forbidden')
            # Prevent arbitrary pre-existing files, URLs, tools or binary input.
            self.check_input(options['input'])
            self.admit()
            response=self._raw.responses.create(**options,service_tier='default')
            cost=conservative_charge(response)
            if not self._ledger.finish(self._reservation,cost):raise AdmissionDenied('request_unavailable')
            return response
        except Exception:
            self.uncertain()
            raise AdmissionDenied('request_unavailable') from None
        finally:
            self.cleanup()
            self.invalidate_ui()
            self._reservation=None

    def check_input(self, value):
        if isinstance(value,str):return
        if not isinstance(value,list) or len(value)>4:raise AdmissionDenied('request_forbidden')
        for message in value:
            if not isinstance(message,dict) or set(message)!={'role','content'} or message['role']!='user':
                raise AdmissionDenied('request_forbidden')
            if not isinstance(message['content'],list) or len(message['content'])>8:raise AdmissionDenied('request_forbidden')
            for item in message['content']:
                kind=item.get('type') if isinstance(item,dict) else None
                if kind=='input_text' and set(item)=={'type','text'} and isinstance(item['text'],str):continue
                if kind=='input_file' and set(item)=={'type','file_id'} and item['file_id'] in self._file_ids:continue
                if kind=='input_image' and set(item)<= {'type','image_url','detail'} and item.get('detail','high')=='high' and isinstance(item.get('image_url'),str) and item['image_url'].startswith('data:image/png;base64,'):continue
                raise AdmissionDenied('request_forbidden')


def public_client(action):
    import public_access
    from openai import OpenAI
    config=public_access.configuration()
    person=public_access.principal(config)
    store=public_access.ledger(config)
    # A read here fails closed before initializing a client. reserve() remains
    # the authoritative atomic decision immediately before each upstream call.
    store.inspect(person)
    raw=OpenAI(api_key=config.api_key,project=config.project,max_retries=0,timeout=90,
               base_url='https://api.openai.com/v1')
    return MeteredClient(raw,store,person,action)
