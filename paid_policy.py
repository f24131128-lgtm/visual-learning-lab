"""Durable admission ledger. No source, credential or email enters these tables."""
from contextlib import contextmanager, closing
from dataclasses import dataclass
import uuid
import re

# Worst documented GPT-6.1 Sol context, long-context cache-write rate and
# regional premium: 1,050,000*5.5 + 16,000*16.5 = 6,039,000 micro USD.
# Fixed Standard processing only; rounding/margin rounds reservation up to $7.
RESERVATION = 7_000_000
BUDGET = 10_000_000
DAILY_REQUESTS = 20
USER_ANALYSES = 2
USER_GENERATIONS = 6
CONCURRENCY = 1
PRICE_VALID_UNTIL = '2026-11-01'


class AdmissionDenied(RuntimeError):
    """Controlled reason only; never include driver/SDK exception bodies."""


@dataclass(frozen=True)
class Reservation:
    id: str


SCHEMA = (
    'CREATE TABLE vll_paid_policy (id INTEGER PRIMARY KEY CHECK (id=1), '
    'fingerprint TEXT NOT NULL, budget BIGINT NOT NULL, committed BIGINT NOT NULL, paused BOOLEAN NOT NULL)',
    'CREATE TABLE vll_paid_requests (id TEXT PRIMARY KEY, principal TEXT NOT NULL, '
    'action TEXT NOT NULL, day TEXT NOT NULL, state TEXT NOT NULL, charge BIGINT NOT NULL)',
    'CREATE INDEX vll_paid_principal ON vll_paid_requests(principal)',
    'CREATE INDEX vll_paid_day ON vll_paid_requests(day)',
)


class Ledger:
    """PostgreSQL in deployment; SQLite dialect is for offline tests only.

    One persisted row lock serializes admission AND completion across processes.
    Pending/uncertain reservations never expire automatically. A process crash
    fails closed until an operator reconciles it, rather than minting new slots.
    """
    def __init__(self, connect, fingerprint, dialect='postgres'):
        if dialect not in ('postgres', 'sqlite'):
            raise ValueError('Ledger dialect')
        self.connect, self.fingerprint, self.dialect = connect, fingerprint, dialect

    def sql(self, connection, statement, args=()):
        return connection.execute(statement.replace('?', '%s') if self.dialect=='postgres' else statement, args)

    @contextmanager
    def transaction(self):
        try:
            with closing(self.connect()) as connection:
                with connection:
                    if self.dialect=='sqlite':
                        connection.execute('BEGIN IMMEDIATE')
                    else:
                        connection.execute("SET LOCAL TIME ZONE 'UTC'")
                        connection.execute("SET LOCAL statement_timeout = '3000ms'")
                        connection.execute("SET LOCAL lock_timeout = '2000ms'")
                    yield connection
        except AdmissionDenied:
            raise
        except Exception:
            raise AdmissionDenied('ledger_unavailable') from None

    def initialize(self):
        """Explicit operator operation only. Never reset or upsert an old budget."""
        with self.transaction() as c:
            for statement in SCHEMA:self.sql(c, statement)
            self.sql(c, 'INSERT INTO vll_paid_policy VALUES (1, ?, ?, 0, ?)',
                     (self.fingerprint, BUDGET, False))

    def policy(self, c):
        row=self.sql(c, 'SELECT fingerprint,budget,committed,paused FROM vll_paid_policy WHERE id=1'+
                     (' FOR UPDATE' if self.dialect=='postgres' else '')).fetchone()
        if row is None or row[0]!=self.fingerprint or row[1]!=BUDGET:
            raise AdmissionDenied('policy_mismatch')
        return row

    def snapshot(self, c, principal):
        row=self.policy(c)
        day=str(self.sql(c, 'SELECT CURRENT_DATE').fetchone()[0])
        if day>=PRICE_VALID_UNTIL:raise AdmissionDenied('pricing_review_required')
        active=self.sql(c, "SELECT COUNT(*) FROM vll_paid_requests WHERE state IN ('pending','uncertain')").fetchone()[0]
        daily=self.sql(c, 'SELECT COUNT(*) FROM vll_paid_requests WHERE day=?',(day,)).fetchone()[0]
        counts=self.sql(c, "SELECT COUNT(*),COALESCE(SUM(CASE WHEN action='analysis' THEN 1 ELSE 0 END),0) "
                        'FROM vll_paid_requests WHERE principal=?',(principal,)).fetchone()
        return dict(day=day,remaining=row[1]-row[2],paused=bool(row[3]),active=active,daily=daily,
                    analyses=counts[1],generations=counts[0]-counts[1])

    @staticmethod
    def reason(status, action='analysis'):
        if status['paused']:return 'paused_for_review'
        if status['remaining']<RESERVATION:return 'budget_exhausted'
        if status['daily']>=DAILY_REQUESTS:return 'daily_exhausted'
        if status['active']>=CONCURRENCY:return 'busy'
        if action=='analysis' and status['analyses']>=USER_ANALYSES:return 'personal_exhausted'
        if action!='analysis' and status['generations']>=USER_GENERATIONS:return 'personal_exhausted'
        return None

    def inspect(self, principal):
        with self.transaction() as c:return self.snapshot(c, principal)

    def reserve(self, principal, action):
        if not isinstance(principal,str) or len(principal)!=64 or any(ch not in '0123456789abcdef' for ch in principal):
            raise AdmissionDenied('identity_required')
        if action not in ('analysis','explain','review','scene','atlas','planner','analogy','simulation'):
            raise AdmissionDenied('action_forbidden')
        with self.transaction() as c:
            status=self.snapshot(c,principal)
            reason=self.reason(status,action)
            if reason:raise AdmissionDenied(reason)
            rid=uuid.uuid4().hex
            self.sql(c, 'INSERT INTO vll_paid_requests VALUES (?, ?, ?, ?, ?, ?)',
                     (rid,principal,action,status['day'],'pending',RESERVATION))
            self.sql(c, 'UPDATE vll_paid_policy SET committed=committed+? WHERE id=1',(RESERVATION,))
            return Reservation(rid)

    def finish(self, reservation, charge=None):
        """Unknown outcomes remain fully charged and block new traffic.

        Errors/duplicates cannot refund a reservation. Known costs are rounded
        upward at worst-case published rates, rather than relying on cache hits.
        """
        with self.transaction() as c:
            self.policy(c)
            row=self.sql(c, 'SELECT state,charge FROM vll_paid_requests WHERE id=?',(reservation.id,)).fetchone()
            if row is None:raise AdmissionDenied('unknown_reservation')
            if row[0]!='pending':return False
            known=type(charge) is int and 0<=charge<=row[1]
            if known:
                self.sql(c, 'UPDATE vll_paid_requests SET state=?,charge=? WHERE id=?',('complete',charge,reservation.id))
                self.sql(c, 'UPDATE vll_paid_policy SET committed=committed-? WHERE id=1',(row[1]-charge,))
            else:
                self.sql(c, 'UPDATE vll_paid_requests SET state=? WHERE id=?',('uncertain',reservation.id))
                self.sql(c, 'UPDATE vll_paid_policy SET paused=? WHERE id=1',(True,))
            return known


def conservative_charge(response):
    """Bill all input at $5.50/M and all output at $16.50/M, including reasoning.

    This deliberately overcounts cached input and short contexts. It is a
    conservative admission ledger, not the provider invoice. Unknown => None.
    """
    if getattr(response,'status',None)!='completed':return None
    if getattr(response,'service_tier','default')!='default':return None
    model=getattr(response,'model',None)
    if not isinstance(model,str) or not re.fullmatch(r'gpt-6\.1-sol(?:-\d{4}-\d{2}-\d{2})?',model):return None
    usage=getattr(response,'usage',None)
    i,o=getattr(usage,'input_tokens',None),getattr(usage,'output_tokens',None)
    if type(i) is not int or type(o) is not int or not 0<=i<=1_050_000 or not 0<=o<=16_000:return None
    return (i*55+o*165+9)//10
