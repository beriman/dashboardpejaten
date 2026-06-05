"""Extract all script blocks and check each for syntax errors."""
import re, subprocess, tempfile
from pathlib import Path

html = Path(r'C:\Users\bim\dashboardpejaten\public\index.html').read_text(encoding='utf-8', errors='ignore')

# Extract script blocks
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

print(f'Found {len(scripts)} script blocks')

for i, script in enumerate(scripts):
    if len(script.strip()) < 10:
        continue
    
    # Write to temp file
    temp = Path(tempfile.gettempdir()) / f'script_{i+1}.js'
    temp.write_text(script, encoding='utf-8')
    
    # Check with Node.js
    result = subprocess.run(
        ['node', '--check', str(temp)],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        print(f'\n*** ERROR in Script {i+1} (len={len(script)}) ***')
        print(f'Error: {result.stderr[:500]}')
        
        # Show first and last 3 lines of the script
        lines = script.split('\n')
        print(f'\nFirst 3 lines:')
        for line in lines[:3]:
            print(f'  {line[:100]}')
        print(f'Last 3 lines:')
        for line in lines[-3:]:
            print(f'  {line[:100]}')
    else:
        print(f'Script {i+1}: OK (len={len(script)})')
    
    temp.unlink(missing_ok=True)
