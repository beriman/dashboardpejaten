import re

content = open(r'C:\Users\bim\.openclaw\workspace\deploy\pejaten-dashboard-web\public\index.html', 'r', encoding='utf-8').read()

# Find all inline script blocks (no src)
scripts = re.findall(r'<script(?!\s+src)[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"Found {len(scripts)} inline script blocks")

# Check each block for potential issues
for i, s in enumerate(scripts):
    lines = s.split('\n')
    print(f"\n--- Block {i+1}: {len(s)} chars, {len(lines)} lines ---")
    
    # Check for common issues
    # 1. Look for variables that might be undefined
    # Check if variables are used before declaration
    if 'exportDashboardPdf' in s or 'exportDashboardPpt' in s:
        print("  Contains export functions")
    
    # 2. Check for optional chaining issues  
    optional_chains = re.findall(r'\?\.\s*\w+', s)
    if optional_chains:
        print(f"  Optional chaining: {len(optional_chains)} instances")
    
    # 3. Check for function calls that might fail
    func_calls = re.findall(r'(document\.getElementById|querySelector|querySelectorAll)\s*\(', s)
    print(f"  DOM queries: {len(func_calls)}")

# Now let's check the MAIN script block (the big one) for the init flow
# Find the last script block which should contain the init code
last_script = scripts[-1] if scripts else ""
print(f"\n\n=== LAST SCRIPT BLOCK (first 500 chars) ===")
print(last_script[:500])
print(f"\n=== LAST SCRIPT BLOCK (last 500 chars) ===")
print(last_script[-500:])

# Check for the specific pattern: what removes is-loading
print("\n\n=== ALL is-loading remove patterns ===")
for match in re.finditer(r"classList\.remove\(['\"]is-loading['\"]\)", content):
    idx = match.start()
    line_num = content[:idx].count('\n') + 1
    context_start = max(0, idx - 100)
    context_end = min(len(content), idx + 50)
    print(f"L{line_num}: {content[context_start:context_end]}")
