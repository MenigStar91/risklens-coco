"""Reproducible synthetic dataset. Contains no real financial records."""
import csv,json,random
from pathlib import Path
from datetime import datetime,timedelta
ROOT=Path(__file__).resolve().parent
rng=random.Random(42)
accounts=[{'account_id':f'A{100+i}','customer_name':n,'baseline_amount':b} for i,(n,b) in enumerate([('Meridian Textiles',35000),('Cedar Retail',18000),('Harbor Logistics',42000),('Pinecrest Foods',26000),('Atlas Components',20000),('Lumen Services',12000),('Solstice Trading',45000),('Maple Healthcare',38000),('Orion Packaging',15000),('Juniper Studios',22000),('Brookfield Supply',30000),('Ember Technologies',55000)])]
rows=[]
def add(account,amount,when,beneficiary='B001',age=180):
 rows.append({'transaction_id':f'TX{len(rows)+1:04d}','account_id':account,'amount':amount,'currency':'INR','transaction_time':when,'beneficiary_id':beneficiary,'beneficiary_age_days':age,'direction':'debit'})
for a in accounts:
 for j in range(18):
  d=datetime(2026,9,1)+timedelta(days=j*1.5,hours=rng.randrange(8,17),minutes=rng.randrange(60))
  add(a['account_id'],rng.randrange(3000,int(a['baseline_amount']*1.6)),d.isoformat(timespec='seconds'),f'B{rng.randrange(1,20):03d}')
add('A104',320000,'2026-09-22T10:00:00','B091',2)
for i in range(5):add('A104',90000+i*1000,f'2026-09-22T10:{5+i*3:02d}:00','B091',2)
add('A102',540000,'2026-09-18T14:30:00','B003',220)
for i in range(4):add('A106',70000,f'2026-09-15T09:{i*4:02d}:00','B004',80)
add('A108',160000,'2026-09-27T11:20:00','B088',1)
add('A111',410000,'2026-09-20T15:10:00','B005',90)
policies=[{'id':'POL-01','name':'Unusual payment amount','version':'1.0','rule':'Amount ≥ INR 200,000 AND amount ≥ 5 × account baseline.','description':'Account baseline is a declared synthetic historical typical-payment amount. A match is a review signal, not proof of fraud.'}, {'id':'POL-02','name':'Rapid transfer burst','version':'1.0','rule':'At least 4 outgoing transfers in an inclusive trailing 15-minute window.','description':'Evaluate per account in event-time order. Transactions participating in a qualifying window become evidence; overlapping windows are deduplicated.'}, {'id':'POL-03','name':'New beneficiary exposure','version':'1.0','rule':'Beneficiary age ≤ 7 days AND payment amount ≥ INR 75,000.','description':'Beneficiary age is measured at transaction time. A new beneficiary can be legitimate; reviewer judgement is required.'}]
data={'snapshot':'2026-09','currency':'INR','accounts':accounts,'transactions':rows,'policies':policies}
(ROOT/'dist/data.js').write_text('globalThis.RISKLENS_DATA = '+json.dumps(data,indent=2)+';\n')
(ROOT/'data').mkdir(exist_ok=True)
(ROOT/'data/demo.json').write_text(json.dumps(data,indent=2))
for name,rs in [('accounts',accounts),('transactions',rows),('policies',policies)]:
 with (ROOT/f'data/{name}.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
print(f'Generated {len(accounts)} accounts, {len(rows)} synthetic payments')
