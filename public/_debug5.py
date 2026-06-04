import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()
scripts = re.findall(r'<script(?!\s+src)[^>]*>(.*?)</script>', content, re.DOTALL)
block6 = scripts[5]

# Check the last IIFE at offset 274044
print("Last IIFE area (offset 274044):")
print(block6[274044:274044+200])

# Let's also check: the block ends with }); for requestAnimationFrame
# But what opens the block? Let's see if there's a wrapping function
print("\n\nBlock 6 very start:")
print(block6[:100])

# Check if block 6 starts with something that needs a closing }
# Maybe it starts inside a function or IIFE
print("\n\nLet's check balance walking from start:")
balance = 0
lines = block6.split('\n')
for i, line in enumerate(lines, 1):
    o = line.count('{')
    c = line.count('}')
    balance += o - c
    if balance < 0:
        print(f"NEGATIVE at line {i}: balance={balance}")
        print(f"  Line: {line.strip()}")
        break
    if i <= 5:
        print(f"  L{i}: balance={balance}, o={o}, c={c}, line={line.strip()[:80]}")

# Check the end of block 5 to see if block 6 is supposed to be inside something
block5 = scripts[4]
print(f"\n\nBlock 5 last 200 chars:")
print(block5[-200:])
