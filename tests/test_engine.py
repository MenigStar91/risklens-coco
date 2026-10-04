import unittest,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from risk_engine import analyze
class EngineTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((Path(__file__).resolve().parents[1]/'data/demo.json').read_text())
 def test_known_alerts_and_deduplicated_exposure(self):
  m=analyze(self.data);self.assertEqual(m['exposure'],2170000);self.assertEqual(len(m['flagged']),13);self.assertEqual(len(m['transactions']),229)
  a=next(a for a in m['alerts'] if a['account_id']=='A104');self.assertEqual(a['exposure'],780000);self.assertEqual(len(a['evidence']),6);self.assertEqual(len(a['signals']),3)
 def test_out_of_period_and_credit_excluded(self):
  t=self.data['transactions'][-1].copy();t.update(transaction_id='OUT',amount=99999999,transaction_time='2026-10-01T00:00:00');self.data['transactions'].append(t)
  c=t.copy();c.update(transaction_id='CREDIT',direction='credit',transaction_time='2026-09-02T12:00:00');self.data['transactions'].append(c)
  self.assertEqual(analyze(self.data)['exposure'],2170000)
 def test_inclusive_burst_boundary_and_overlap(self):
  base=self.data['transactions'][0];self.data['accounts']=self.data['accounts'][:1]
  self.data['transactions']=[{**base,'transaction_id':str(i),'transaction_time':f'2026-09-01T10:{minute:02d}:00','amount':1000} for i,minute in enumerate([0,5,10,15,16])]
  a=analyze(self.data)['alerts'][0];self.assertEqual(len(a['evidence']),5);self.assertEqual(a['exposure'],5000)
 def test_no_burst_outside_window(self):
  base=self.data['transactions'][0];self.data['accounts']=self.data['accounts'][:1]
  self.data['transactions']=[{**base,'transaction_id':str(i),'transaction_time':f'2026-09-01T10:{minute:02d}:00','amount':1000} for i,minute in enumerate([0,5,10,16])]
  self.assertEqual(analyze(self.data)['alerts'],[])
 def test_thresholds_inclusive(self):
  a=self.data['accounts'][0];a['baseline_amount']=40000;self.data['accounts']=[a]
  self.data['transactions']=[{**self.data['transactions'][0],'amount':200000,'beneficiary_age_days':7}]
  self.assertEqual({s['policy'] for s in analyze(self.data)['alerts'][0]['signals']},{'POL-01','POL-03'})
if __name__=='__main__':unittest.main()
