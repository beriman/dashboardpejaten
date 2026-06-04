import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()

# Check brace balance
scripts = re.findall(r'<script(?!\s+src)[^>]*>(.*?)</script>', content, re.DOTALL)
all_ok = True
for i, s in enumerate(scripts):
    o = s.count('{')
    c = s.count('}')
    diff = o - c
    status = "OK" if diff == 0 else f"ERROR diff={diff}"
    if diff != 0:
        all_ok = False
    print(f"Block {i+1}: {{ = {o}, }} = {c}, {status}")

# Also check the tail of the file
print("\n=== Last 20 lines ===")
lines = content.split('\n')
for i, line in enumerate(lines[-20:], start=len(lines)-19):
    print(f"L{i}: {line}")

# Check for stray closing braces/parens
print("\n=== Checking for stray }); patterns ===")
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped == '});':
        # Check context
        prev_lines = lines[max(0,i-4):i-1]
        print(f"L{i}: {stripped}  (prev: {[l.strip() for l in prev_lines]})")

if all_ok:
    print("\nAll script blocks pass brace balance check!")
else:
    print("\nWARNING: Some blocks have unbalanced braces!")
