(function(root){
'use strict';
function analyze(data){
 const transactions=data.transactions.filter(t=>t.direction==='debit'&&t.currency==='INR'&&t.transaction_time>='2026-09-01'&&t.transaction_time<'2026-10-01');
 const alerts=[];
 for(const a of data.accounts){
  const rows=transactions.filter(t=>t.account_id===a.account_id).sort((a,b)=>a.transaction_time.localeCompare(b.transaction_time));
  const signals=[];
  const unusual=rows.filter(t=>t.amount>=200000&&t.amount>=5*a.baseline_amount);
  if(unusual.length)signals.push({policy:'POL-01',name:'Unusual payment amount',rows:unusual});
  const burstIds=new Set();
  for(let i=0;i<rows.length;i++){
   const end=Date.parse(rows[i].transaction_time+'Z');
   const window=rows.slice(0,i+1).filter(t=>end-Date.parse(t.transaction_time+'Z')<=15*60*1000);
   if(window.length>=4)window.forEach(t=>burstIds.add(t.transaction_id));
  }
  const burst=rows.filter(t=>burstIds.has(t.transaction_id));
  if(burst.length)signals.push({policy:'POL-02',name:'Rapid transfer burst',rows:burst});
  const fresh=rows.filter(t=>t.beneficiary_age_days<=7&&t.amount>=75000);
  if(fresh.length)signals.push({policy:'POL-03',name:'New beneficiary exposure',rows:fresh});
  if(signals.length){
   const ids=new Set(signals.flatMap(s=>s.rows.map(t=>t.transaction_id)));
   const evidence=rows.filter(t=>ids.has(t.transaction_id));
   alerts.push({...a,signals,evidence,exposure:evidence.reduce((s,t)=>s+t.amount,0),severity:signals.length>=2||evidence.some(t=>t.amount>=500000)?'High':'Medium'});
  }
 }
 alerts.sort((a,b)=>(a.severity==='High'?0:1)-(b.severity==='High'?0:1)||b.exposure-a.exposure);
 const ids=new Set(alerts.flatMap(a=>a.evidence.map(t=>t.transaction_id)));
 const flagged=transactions.filter(t=>ids.has(t.transaction_id));
 return {transactions,alerts,flagged,total:transactions.reduce((s,t)=>s+t.amount,0),exposure:flagged.reduce((s,t)=>s+t.amount,0)};
}
root.RiskEngine={analyze};
if(typeof module!=='undefined')module.exports={analyze};
})(globalThis);
