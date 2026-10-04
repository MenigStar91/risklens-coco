"""Python application: offline reference mode or explicit Snowflake-connected mode."""
import json,os,re
from pathlib import Path
import pandas as pd
import streamlit as st
from risk_engine import analyze
st.set_page_config(page_title='RiskLens',page_icon='🔎',layout='wide')
st.title('RiskLens — Payment Risk Investigation Copilot')
mode=os.getenv('RISKLENS_MODE','demo')
session=None
if mode=='snowflake':
    try:
        from snowflake_adapter import get_session,load_snapshot,verify_sql_results
        session=get_session();data=load_snapshot(session);result=analyze(data);verify_sql_results(session,result)
        st.success('Connected to Snowflake · SQL rule results verified against reference engine')
    except Exception as e:
        st.error('Snowflake setup or verification failed. No demo fallback was used. Check your connection, seed and rule views.');st.stop()
else:
    data=json.loads((Path(__file__).parent/'data/demo.json').read_text());result=analyze(data)
    st.info('Offline demo · synthetic data · deterministic analysis · no live Snowflake or AI calls')
st.caption('September 2026 · INR only · signals require analyst review and do not establish fraud.')
cols=st.columns(4)
for c,label,value in zip(cols,['Payments','Accounts flagged','Unique evidence rows','Flagged amount'],[len(result['transactions']),len(result['alerts']),len(result['flagged']),f"₹{result['exposure']:,.0f}"]):c.metric(label,value)
tabs=st.tabs(['Investigations','Copilot','Policies'])
with tabs[0]:
    st.dataframe(pd.DataFrame([{k:a[k] for k in ['account_id','customer_name','severity','exposure']} for a in result['alerts']]),use_container_width=True,hide_index=True)
    if result['alerts']:
        selected=st.selectbox('Account',[a['account_id'] for a in result['alerts']]);case=next(a for a in result['alerts'] if a['account_id']==selected)
        st.subheader(case['customer_name'])
        for signal in case['signals']:
            p=next(p for p in data['policies'] if p['id']==signal['policy']);st.write(f"**{p['id']} · {p['name']} · v{p['version']}** — {p['rule']}")
        st.dataframe(pd.DataFrame(case['evidence']),use_container_width=True,hide_index=True)
        notes=st.text_area('Reviewer notes',key='notes_'+selected,max_chars=5000)
        state=st.selectbox('Review status',['Open','In review','Escalated','Closed'],key='state_'+selected)
        report={**case,'report_type':'Synthetic-data investigation draft','review_status':state,'reviewer_notes':notes,'limitations':['Not a fraud verdict or regulatory filing','Session-local review state; no tamper-proof audit log'],'policies':data['policies']}
        st.download_button('Download investigation JSON',json.dumps(report,indent=2,default=str),file_name=f'CASE-{selected}.json',mime='application/json')
        st.download_button('Download evidence CSV',pd.DataFrame(case['evidence']).to_csv(index=False),file_name=f'{selected}-evidence.csv',mime='text/csv')
with tabs[1]:
    st.caption('Supported analytics are deterministic. Optional Cortex explanations run only with an explicit Snowflake connection.')
    question=st.text_input('Ask about alerts, exposure, policies or account A104',max_chars=400)
    ai_enabled=st.checkbox('Use Cortex for evidence-grounded account explanations',disabled=session is None)
    if st.button('Answer') and question:
        q=question.lower();found=re.search(r'\bA\d{3}\b',question,re.I)
        if re.search(r'202[0-57-9]|october|august|last month|today|yesterday|this year',q):st.warning('This snapshot covers September 2026 only. Ask using that period.')
        elif found:
            account_id=found.group().upper();case=next((a for a in result['alerts'] if a['account_id']==account_id),None)
            if case:
                st.json({k:v for k,v in case.items() if k!='evidence'});st.dataframe(pd.DataFrame(case['evidence']),hide_index=True)
                if ai_enabled and session:
                    from snowflake_adapter import ai_explain
                    try:st.write(ai_explain(session,question,case,data['policies']))
                    except Exception:st.error('Cortex request failed. Computed evidence above remains available. Check model availability and AI privileges.')
            elif any(a['account_id']==account_id for a in data['accounts']):st.write('No configured rule fired. This does not establish that this account is risk-free.')
            else:st.warning('Account is not present in this dataset.')
        elif any(w in q for w in ['policy','policies','rule','threshold']):st.dataframe(pd.DataFrame(data['policies']),hide_index=True)
        elif any(w in q for w in ['exposure','total','amount','how much']):st.write(f"₹{result['exposure']:,.0f} in {len(result['flagged'])} unique flagged payments. This is not an estimate of loss.")
        elif any(w in q for w in ['accounts','alerts','flagged','suspicious','risk']):st.dataframe(pd.DataFrame([{k:a[k] for k in ['account_id','customer_name','severity','exposure']} for a in result['alerts']]),hide_index=True)
        else:st.warning('Supported: list alerts, explain A104, show A104 evidence, flagged exposure, policy explanations.')
with tabs[2]:
    st.dataframe(pd.DataFrame(data['policies']),use_container_width=True,hide_index=True)
    st.write('Internal invented demo policies. No confidential data, regulatory filing automation, or verified legal compliance claims.')
