"""Check the built index.html for JS syntax errors using Node.js."""
import subprocess
from pathlib import Path

result = subprocess.run(
    ['node', '-c', Path(r'C:\Users\bim\dashboardpejaten\public\index.html').read_text(encoding='utf-8')],
    capture_output=True,
    text=True,
    timeout=30
)

print(f'Exit code: {result.returncode}')
if result.stderr:
    print(f'STDERR:\n{result.stderr[:2000]}')
if result.stdout:
    print(f'STDOUT:\n{result.stdout[:500]}')
