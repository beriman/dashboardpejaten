"""Check dataSets JSON validity."""
import re, json
from pathlib import Path

html = Path(r'H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html').read_text(encoding='utf-8', errors='ignore')

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

for i, script in enumerate(scripts):
    if 'const dataSets' in script:
        idx = script.find('const dataSets = ')
        if idx >= 0:
            data_start = script[idx + len('const dataSets = '):]
            print(f'After const dataSets = : {repr(data_start[:100])}')
            
            # Simple brace counting
            depth = 0
            end_pos = -1
            for j, c in enumerate(data_start):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        end_pos = j
                        break
            
            if end_pos > 0:
                data_str = data_start[:end_pos+1]
                print(f'dataSets length: {len(data_str)}')
                
                try:
                    data = json.loads(data_str)
                    print(f'JSON VALID!')
                    print(f'Buildings: {[b["name"] for b in data.get("daily", {}).get("buildings", [])]}')
                except json.JSONDecodeError as e:
                    print(f'JSON Error: {e}')
                    pos = e.pos
                    print(f'Context: {data_str[max(0,pos-30):pos+30]}')
            break
