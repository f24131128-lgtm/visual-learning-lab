"""Server-owned public release configuration and verified OIDC identity."""
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import math
import os
import re
from urllib.parse import urlparse

from paid_policy import AdmissionDenied, Ledger, BUDGET, PRICE_VALID_UNTIL

GOOGLE_ISSUER = 'https://accounts.google.com'
GOOGLE_METADATA = GOOGLE_ISSUER + '/.well-known/openid-configuration'


def mode():
    if 'VLL_LIVE_AI' in os.environ:return os.environ['VLL_LIVE_AI']
    try:
        import streamlit as st
        return st.secrets.get('VLL_LIVE_AI','')
    except Exception:return ''


@dataclass(frozen=True)
class PublicConfig:
    api_key: str = field(repr=False)
    project: str
    dsn: str = field(repr=False)
    issuer: str
    salt: str = field(repr=False)
    ca_cert: str = 'system'

    @property
    def fingerprint(self):
        # Changes to key/issuer/salt cannot silently reset person or budget IDs.
        value=[self.project,self.issuer,hashlib.sha256(self.api_key.encode()).hexdigest(),
               hashlib.sha256(self.salt.encode()).hexdigest(),BUDGET,PRICE_VALID_UNTIL,'policy-v1']
        return hashlib.sha256(json.dumps(value).encode()).hexdigest()


def check_auth_configuration():
    """Validate Google independently, so login can be checked with paid AI off."""
    reason='auth_load'
    try:
        import streamlit as st
        auth=st.secrets['auth']
        for n in ('redirect_uri','cookie_secret','client_id','client_secret','server_metadata_url'):
            reason='auth_field_'+n
            if not isinstance(auth.get(n),str) or not auth[n]:raise ValueError()
        reason='auth_cookie_length'
        if len(auth['cookie_secret'])<32:raise ValueError()
        reason='auth_callback'
        callback=urlparse(auth['redirect_uri'])
        if (callback.scheme!='https' or not callback.hostname or callback.username or callback.password
                or callback.path!='/oauth2callback' or callback.query or callback.fragment):raise ValueError()
        reason='auth_metadata'
        if auth['server_metadata_url']!=GOOGLE_METADATA:raise ValueError()
        reason='auth_client_id'
        if not auth['client_id'].endswith('.apps.googleusercontent.com'):raise ValueError()
        reason='auth_token_exposure'
        if auth.get('expose_tokens'):raise ValueError()
    except Exception:
        import logging
        logging.getLogger(__name__).warning('Google configuration unavailable: %s',reason)
        raise AdmissionDenied('configuration_required') from None


def configuration():
    try:
        import streamlit as st
        raw=st.secrets['public_ai']
        key,project,dsn,issuer,salt=(raw[n] for n in ('api_key','project_id','ledger_dsn','identity_issuer','quota_hmac_secret'))
        if not all(isinstance(v,str) for v in (key,project,dsn,issuer,salt)):raise ValueError()
        if not key or not re.fullmatch(r'proj_[A-Za-z0-9_-]{4,100}',project):raise ValueError()
        if not dsn.startswith(('postgresql://','postgres://')) or not urlparse(dsn).hostname:raise ValueError()
        if issuer!=GOOGLE_ISSUER or len(salt)<32:raise ValueError()
        if raw.get('dedicated_project_verified') is not True:raise ValueError()
        if raw.get('budget_microusd')!=BUDGET:raise ValueError()
        if raw.get('price_review_date')!='2026-10-13':raise ValueError()
        check_auth_configuration()
        return PublicConfig(key,project,dsn,issuer,salt,raw.get('ca_cert','system'))
    except Exception:
        raise AdmissionDenied('configuration_required') from None


def verified_subject(issuer):
    try:
        import streamlit as st
        user=st.user
        if not user.is_logged_in:raise ValueError()
        subject=user.get('sub')
        if user.get('iss')!=issuer or not isinstance(subject,str) or not 0<len(subject)<=256:raise ValueError()
        # Streamlit validates the OIDC cookie/signature; never accept a form,
        # query parameter, session UUID, arbitrary email or client-supplied ID.
        expiry=user.get('exp')
        if expiry is not None:
            import time
            if type(expiry) not in (int,float) or not math.isfinite(expiry) or expiry<=time.time():raise ValueError()
        return subject
    except Exception:raise AdmissionDenied('identity_required') from None


def principal(config):
    subject=verified_subject(config.issuer)
    return hmac.new(config.salt.encode(),(config.issuer+'\0'+subject).encode(),'sha256').hexdigest()


def ledger(config):
    def connect():
        import psycopg
        # No SQLite fallback, connection retry or URL supplied by visitors.
        return psycopg.connect(config.dsn,connect_timeout=3,sslmode='verify-full',sslrootcert=config.ca_cert)
    return Ledger(connect,config.fingerprint)


def public_available():
    try:
        import streamlit as st
        import time
        config=configuration();person=principal(config)
        cache=st.session_state.get('_public_gate',{})
        signature=config.fingerprint+person
        if cache.get('signature')!=signature or time.monotonic()-cache.get('time',0)>2:
            status=ledger(config).inspect(person)
            cache=dict(signature=signature,time=time.monotonic(),status=status)
            st.session_state['_public_gate']=cache
        status=cache['status']
        return any(ledger_reason(status,a) is None for a in ('analysis','explain'))
    except Exception:return False


def ledger_reason(status, action):return Ledger.reason(status,action)


def render_public_access():
    import streamlit as st
    from i18n import tr
    selected=mode()
    if selected=='private':return
    if selected!='limited-public':
        try:check_auth_configuration()
        except AdmissionDenied:
            try:
                if 'auth' in st.secrets:st.info(tr('Google sign-in configuration is unavailable. Paid AI remains disabled.'))
            except Exception:pass
            return
        st.caption(tr('Prepared mode · live AI generation is disabled by server policy.'))
        try:verified_subject(GOOGLE_ISSUER)
        except AdmissionDenied:
            if st.button(tr('Verify Google sign-in'),key='public-sign-in'):
                try:st.login()
                except Exception:st.error(tr('Sign-in is unavailable. Please use the prepared example.'))
            if st.user.is_logged_in and st.button(tr('Sign out'),key='public-sign-out'):st.logout()
            return
        st.success(tr('Google sign-in verified. Paid AI remains disabled.'))
        if st.button(tr('Sign out'),key='public-sign-out'):st.logout()
        try:
            config=configuration();status=ledger(config).inspect(principal(config))
            st.caption(tr('Persistent ledger verified. No AI request was made.'))
            st.caption(tr('Limited AI: {analyses} analyses and {generations} extra generations remaining.',
                          analyses=max(0,2-status['analyses']),generations=max(0,6-status['generations'])))
        except AdmissionDenied:
            st.info(tr('The persistent ledger is not verified yet. Paid AI remains disabled.'))
        return
    try:
        config=configuration()
    except AdmissionDenied:
        st.info(tr('Limited AI is unavailable. The prepared example remains available.'))
        return
    try:
        person=principal(config)
    except AdmissionDenied:
        st.info(tr('Sign in to use your limited AI allowance. Prepared exploration needs no login.'))
        if st.button(tr('Sign in with Google for limited AI'),key='public-sign-in'):
            try:st.login()
            except Exception:st.error(tr('Sign-in is unavailable. Please use the prepared example.'))
        return
    if st.button(tr('Sign out'),key='public-sign-out'):st.logout()
    try:
        status=ledger(config).inspect(person)
        st.session_state.pop('_public_gate',None)
        st.caption(tr('Limited AI: {analyses} analyses and {generations} extra generations remaining.',
                      analyses=max(0,2-status['analyses']),generations=max(0,6-status['generations'])))
        if status['paused'] or status['remaining']<7_000_000:
            st.info(tr('The shared AI allowance is unavailable. Local exploration and the prepared example still work.'))
    except AdmissionDenied:
        st.info(tr('Limited AI is unavailable. The prepared example remains available.'))
