"""Reference engine. Mirrors the Snowflake SQL rules and hosted JS engine."""
from datetime import datetime,timedelta
from decimal import Decimal

def analyze(data):
    tx=[t for t in data['transactions'] if t['direction']=='debit' and t['currency']=='INR' and '2026-09-01'<=t['transaction_time']<'2026-10-01']
    alerts=[]
    for account in data['accounts']:
        rows=sorted((t for t in tx if t['account_id']==account['account_id']),key=lambda t:t['transaction_time'])
        signals=[]
        large=[t for t in rows if Decimal(str(t['amount']))>=200000 and Decimal(str(t['amount']))>=5*Decimal(str(account['baseline_amount']))]
        if large: signals.append({'policy':'POL-01','name':'Unusual payment amount','rows':large})
        burst_ids=set()
        for i,end in enumerate(rows):
            end_time=datetime.fromisoformat(end['transaction_time'])
            window=[t for t in rows[:i+1] if end_time-datetime.fromisoformat(t['transaction_time'])<=timedelta(minutes=15)]
            if len(window)>=4: burst_ids.update(t['transaction_id'] for t in window)
        burst=[t for t in rows if t['transaction_id'] in burst_ids]
        if burst: signals.append({'policy':'POL-02','name':'Rapid transfer burst','rows':burst})
        fresh=[t for t in rows if t['beneficiary_age_days']<=7 and t['amount']>=75000]
        if fresh: signals.append({'policy':'POL-03','name':'New beneficiary exposure','rows':fresh})
        if signals:
            ids={t['transaction_id'] for s in signals for t in s['rows']}
            evidence=[t for t in rows if t['transaction_id'] in ids]
            alerts.append({**account,'signals':signals,'evidence':evidence,'exposure':sum(t['amount'] for t in evidence),'severity':'High' if len(signals)>=2 or any(t['amount']>=500000 for t in evidence) else 'Medium'})
    alerts.sort(key=lambda a:(a['severity']!='High',-a['exposure']))
    ids={t['transaction_id'] for a in alerts for t in a['evidence']}
    flagged=[t for t in tx if t['transaction_id'] in ids]
    return {'transactions':tx,'alerts':alerts,'flagged':flagged,'total':sum(t['amount'] for t in tx),'exposure':sum(t['amount'] for t in flagged)}
