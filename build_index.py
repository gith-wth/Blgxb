import json
import csv
import os
import sys
from pathlib import Path

def infer_type(key, val):
    v = val.lower().strip()
    if 'iban' in key.lower() or (len(v) >= 15 and v[:2].isalpha() and v[2:].isdigit()):
        return 'iban'
    if 'email' in key.lower() or ('@' in v and '.' in v.split('@')[-1]):
        return 'email'
    if 'phone' in key.lower() or 'tel' in key.lower() or (v.replace('+','').replace(' ','').isdigit() and len(v) >= 8):
        return 'phone'
    if 'bic' in key.lower() or (len(v) in (8, 11) and v[:4].isalpha() and v[4:6].isalnum()):
        return 'bic'
    if 'name' in key.lower() or 'nom' in key.lower():
        return 'name'
    if 'address' in key.lower() or 'adresse' in key.lower():
        return 'address'
    return None

def process_file(filepath, records):
    ext = filepath.suffix.lower()
    if ext == '.csv':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for key, val in row.items():
                    if val and len(val.strip()) > 2:
                        dtype = infer_type(key, val)
                        if dtype:
                            records.append({
                                'type': dtype,
                                'value': val.strip(),
                                'full_data': json.dumps(row, ensure_ascii=False),
                                'source': filepath.stem
                            })
    elif ext == '.json':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for key, val in item.items():
                            if val and len(str(val).strip()) > 2:
                                dtype = infer_type(key, str(val))
                                if dtype:
                                    records.append({
                                        'type': dtype,
                                        'value': str(val).strip(),
                                        'full_data': json.dumps(item, ensure_ascii=False),
                                        'source': filepath.stem
                                    })
            elif isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    if v and len(str(v).strip()) > 2:
                                        dtype = infer_type(k, str(v))
                                        if dtype:
                                            records.append({
                                                'type': dtype,
                                                'value': str(v).strip(),
                                                'full_data': json.dumps(item, ensure_ascii=False),
                                                'source': filepath.stem
                                            })

def main():
    records = []
    data_dir = Path('leaks')
    if data_dir.exists():
        for filepath in data_dir.iterdir():
            if filepath.is_file():
                process_file(filepath, records)
    else:
        data_dir.mkdir()
        records.append({'type': 'test', 'value': 'FR7612345678901234567890123', 'full_data': '{}', 'source': 'demo'})

    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False)

    print(f"Index généré avec {len(records)} entrées")

if __name__ == '__main__':
    main()
