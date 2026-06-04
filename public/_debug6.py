import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()
scripts = re.findall(r'<script(?!\s+src)[^>]*>(.*?)</script>', content, re.DOTALL)
block6 = scripts[5]

# Walk through and find where balance goes wrong
balance = 0
lines = block6.split('\n')
problem_lines = []
for i, line in enumerate(lines, 1):
    o = line.count('{')
    c = line.count('}')
    balance += o - c
    if balance < 0:
        print(f"NEGATIVE at line {i}: balance={balance}")
        print(f"  Line: {line.strip()}")
        # Show context
        for j in range(max(0,i-5), min(len(lines), i+2)):
            print(f"  L{j+1}: {lines[j].strip()[:100]}")
        break
    
# Also let's check: is there an extra } somewhere?
# Look for } that appears right after another } on the same line or consecutive lines
print("\n\nLooking for suspicious consecutive closing braces:")
for i in range(len(lines)-1):
    stripped = lines[i].strip()
    next_stripped = lines[i+1].strip()
    if stripped == '}' and next_stripped in ['}', '});', '},']:
        print(f"  L{i+1}: {stripped} followed by L{i+2}: {next_stripped}")

# Check: the theme toggle section specifically
print("\n\nBrace tracking near theme toggle:")
in_section = False
for i, line in enumerate(lines, 1):
    if 'themeToggle' in line or 'applyTheme' in line or 'header-chat-btn' in line or 'requestAnimationFrame' in line:
        o = line.count('{')
        c = line.count('}')
        print(f"  L{i}: o={o}, c={c}, |{line.strip()[:100]}")
