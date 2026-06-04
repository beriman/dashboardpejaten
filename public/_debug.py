import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()

# 1. Check script src references
scripts_src = re.findall(r'<script[^>]+src=["\'](.*?)["\']', content)
print("External script sources:")
for s in scripts_src:
    print(f"  {s}")

# 2. Check is-loading references
print("\nis-loading references:")
for i, line in enumerate(content.split('\n'), 1):
    if 'is-loading' in line:
        print(f"  L{i}: {line.strip()}")

# 3. Check the loader/loading init logic
print("\nLoader init logic:")
idx = content.find('is-loading')
if idx >= 0:
    start = max(0, idx - 300)
    end = min(len(content), idx + 500)
    print(content[start:end])

# 4. Check for DOMContentLoaded or window.addEventListener('load')
print("\n\nLoad event listeners:")
for match in re.finditer(r'(DOMContentLoaded|window\.onload|window\.addEventListener\s*\(\s*["\']load)', content):
    idx = match.start()
    line_num = content[:idx].count('\n') + 1
    print(f"  L{line_num}: ...{content[idx:idx+100]}...")

# 5. Check how body gets is-loading class
print("\nBody is-loading assignment:")
for match in re.finditer(r'classList\.(add|remove)\s*\(\s*["\']is-loading', content):
    idx = match.start()
    line_num = content[:idx].count('\n') + 1
    context_start = content.rfind('\n', 0, idx-50) + 1
    context_end = content.find('\n', idx+80)
    print(f"  L{line_num}: ...{content[context_start:context_end]}...")
