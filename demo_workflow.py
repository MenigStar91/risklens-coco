"""Reproducible demo: validate input, detect signals, export case evidence.

Run this through an authenticated CoCo CLI session to capture real CLI evidence.
Running it directly is a local verification, not proof of CoCo usage.
"""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from risk_engine import analyze


def validate_input(path):
    data = json.loads(path.read_text())
    accounts = {row['account_id'] for row in data['accounts']}
    if len(accounts) != len(data['accounts']):
        raise ValueError('Duplicate account IDs')
    transaction_ids = set()
    for row in data['transactions']:
        if row['transaction_id'] in transaction_ids:
            raise ValueError('Duplicate transaction IDs')
        transaction_ids.add(row['transaction_id'])
        if row['account_id'] not in accounts:
            raise ValueError('Unknown account in transaction')
        if row['amount'] < 0 or row['beneficiary_age_days'] < 0:
            raise ValueError('Negative amount or beneficiary age')
        datetime.fromisoformat(row['transaction_time'])
    print(f'[1/3 INPUT VALIDATION] {len(accounts)} accounts, '
          f'{len(transaction_ids)} transactions; IDs and timestamps valid.', flush=True)
    return data


def detect_signals(data, account_id):
    result = analyze(data)
    case = next((a for a in result['alerts'] if a['account_id'] == account_id), None)
    if case is None:
        raise ValueError(f'No flagged case for {account_id}')
    print(f'[2/3 POLICY PROCESSING] {len(result["alerts"])} flagged accounts, '
          f'{len(result["flagged"])} unique flagged payments, '
          f'INR {result["exposure"]:,} flagged exposure.', flush=True)
    for signal in case['signals']:
        print(f'  {signal["policy"]}: {signal["name"]} '
              f'({len(signal["rows"])} matching evidence rows)', flush=True)
    print(f'  {account_id}: {case["severity"]}, INR {case["exposure"]:,}, '
          f'{len(case["evidence"])} distinct evidence rows.', flush=True)
    return result, case


def export_evidence(result, case, output):
    output.mkdir(parents=True, exist_ok=True)
    summary = {
        'execution': 'local Python reference engine',
        'snapshot': '2026-09', 'currency': 'INR', 'synthetic_data': True,
        'monitored_payments': len(result['transactions']),
        'flagged_accounts': len(result['alerts']),
        'unique_flagged_payments': len(result['flagged']),
        'flagged_exposure': result['exposure'],
        'case': case,
        'boundary': 'Review signals, not confirmed fraud or regulatory filings.',
    }
    report = output / f'{case["account_id"]}_case.json'
    report.write_text(json.dumps(summary, indent=2) + '\n')
    evidence = output / f'{case["account_id"]}_evidence.csv'
    with evidence.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(case['evidence'][0]))
        writer.writeheader()
        writer.writerows(case['evidence'])
    print(f'[3/3 EVIDENCE OUTPUT] Wrote {report} and {evidence}.', flush=True)
    print('Review required: validate beneficiary onboarding and request invoice support.', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path(__file__).parent / 'data/demo.json')
    parser.add_argument('--account', default='A104')
    parser.add_argument('--output', type=Path, default=Path('demo_output'))
    args = parser.parse_args()
    data = validate_input(args.input)
    result, case = detect_signals(data, args.account)
    export_evidence(result, case, args.output)


if __name__ == '__main__':
    main()
