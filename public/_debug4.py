import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()

# Get block 6 (last inline script)
scripts = re.findall(r'<script(?!\s+src)[^>]*>(.*?)</script>', content, re.DOTALL)
block6 = scripts[5]

# Find ALL standalone }); lines and check if they have a matching opening
# Let's trace: the block should start with some code and end cleanly
print("Block 6 first 300 chars:")
print(block6[:300])
print("\nBlock 6 last 300 chars:")
print(block6[-300:])

# Let's find all IIFE patterns
iife_starts = []
for match in re.finditer(r'\(\s*function\s*\(\)\s*\{', block6):
    iife_starts.append(match.start())
    print(f"\nIIFE found at offset {match.start()}")
    
# Find all (() => { or similar
arrow_iife = []
for match in re.finditer(r'\(\s*\(\s*\)\s*=>\s*\{', block6):
    arrow_iife.append(match.start())
    print(f"Arrow IIFE found at offset {match.start()}")

# Count everything in block 6
print(f"\nBlock 6 stats:")
print(f"  {{ : {block6.count('{')}")
print(f"  }} : {block6.count('}')}")
print(f"  ( : {block6.count('(')}")
print(f"  ) : {block6.count(')')}")

# Let's check: maybe there's an extra } somewhere
# Walk through and find balance
balance = 0
lines = block6.split('\n')
for i, line in enumerate(lines, 1):
    o = line.count('{')
    c = line.count('}')
    balance += o - c
    if balance < 0:
        print(f"\nBalance went negative at line {i}: balance={balance}, line: {line.strip()}")
        break
