"""Check the generated index.html for JS syntax errors."""
import re
from pathlib import Path

p = Path(r'C:\Users\bim\dashboardpejaten\public\index.html')
html = p.read_text(encoding='utf-8', errors='ignore')

# Find all script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

print(f'Total script blocks: {len(scripts)}')

for i, script in enumerate(scripts):
    lines = script.split('\n')
    print(f'\n--- Script {i+1} ({len(lines)} lines) ---')
    print(f'  First 3 lines:')
    for line in lines[:3]:
        print(f'    {line[:100]}')
    print(f'  Last 3 lines:')
    for line in lines[-3:]:
        print(f'    {line[:100]}')
    
    # Check for common JS errors
    if 'Uncaught' in script or 'TypeError' in script or 'SyntaxError' in script:
        print(f'  ⚠️  Contains error messages!')
    
    # Check for unclosed braces
    open_braces = script.count('{')
    close_braces = script.count('}')
    if open_braces != close_braces:
        print(f'  ⚠️  Unbalanced braces: {open_braces} open, {close_braces} close')
    
    # Check for unclosed parens
    open_parens = script.count('(')
    close_parens = script.count(')')
    if open_parens != close_parens:
        print(f'  ⚠️  Unbalanced parens: {open_parens} open, {close_parens} close')

# Also check for dataSets specifically
print('\n\n--- DataSets check ---')
data_match = re.search(r'const dataSets = (\{.*?\});', html, re.DOTALL)
if data_match:
    data_str = data_match.group(1)
    print(f'DataSets length: {len(data_str)}')
    
    # Check for common issues
    if '"labels"' in data_str:
        labels_match = re.search(r'"labels":\s*(\[.*?\])', data_str, re.DOTALL)
        if labels_match:
            print(f'Labels found: {labels_match.group(1)[:100]}...')
    
    # Check for the buildings data
    buildings_match = re.search(r'"buildings":\s*(\[.*?\])', data_str, re.DOTALL)
    if buildings_match:
        print(f'Buildings found: {buildings_match.group(1)[:200]}...')
    
    # Check for unclosed arrays/braces in dataSets
    open_b = data_str.count('{')
    close_b = data_str.count('}')
    print(f'Braces in dataSets: {open_b} open, {close_b} close, balanced: {open_b == close_b}')
