"""Use Node.js to check for JS syntax errors in the HTML."""
import re, json
from pathlib import Path

html = Path(r'C:\Users\bim\dashboardpejaten\public\index.html').read_text(encoding='utf-8', errors='ignore')

# Extract the main script block (script 5 - dataSets)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

main_script = None
for script in scripts:
    if 'const dataSets' in script:
        main_script = script
        break

if main_script:
    print(f'Main script length: {len(main_script)} chars')
    
    # Write to temp file for Node.js check
    temp_file = Path(r'C:\Users\bim\dashboardpejaten\check_script.js')
    
    # Wrap in try-catch to find errors
    check_code = f'''
try {{
{main_script}
  console.log("SUCCESS: dataSets is", typeof dataSets);
}} catch(e) {{
  console.log("ERROR:", e.message);
  console.log("Stack:", e.stack ? e.stack.substring(0, 500) : "none");
}}
'''
    temp_file.write_text(check_code, encoding='utf-8')
    print(f'Written to {temp_file}')
    
    # Try to find syntax issues manually
    # Check for common issues:
    # 1. Unclosed strings
    # 2. Template literals with unmatched backticks
    # 3. Unclosed regex
    
    lines = main_script.split('\n')
    in_multiline_comment = False
    
    for i, line in enumerate(lines):
        # Check for template literals
        backticks = line.count('`')
        if backticks % 2 != 0:
            print(f'Line {i+1}: Odd backticks ({backticks}): {line[:80]}')
        
        # Check for unclosed strings (simplified)
        single_quotes = line.count("'") - line.count("\\'")
        double_quotes = line.count('"') - line.count('\\"')
        
        # Very basic check - might have false positives
        if single_quotes % 2 != 0 and 'http' not in line and '//' not in line:
            pass  # Could be legitimate
    
    print('\nChecking specific patterns...')
    
    # Check for the buildings array
    if '"buildings":' in main_script:
        idx = main_script.find('"buildings":')
        context = main_script[idx:idx+200]
        print(f'Buildings array start: {context[:100]}')
    
    # Check for buildings data with dailyPlan
    daily_plan_count = main_script.count('dailyPlan:')
    print(f'dailyPlan occurrences: {daily_plan_count}')
    
    # Check curveReal and curvePlan arrays
    curve_real = re.findall(r'"curveReal":\s*\[([^\[\]]+)\]', main_script)
    curve_plan = re.findall(r'"curvePlan":\s*\[([^\[\]]+)\]', main_script)
    
    print(f'curveReal arrays found: {len(curve_real)}')
    print(f'curvePlan arrays found: {len(curve_plan)}')
    
    if curve_real:
        for i, arr in enumerate(curve_real[-1:]):
            print(f'Last curveReal: [{arr[:100]}...]')
            # Check for trailing commas
            if arr.rstrip().endswith(','):
                print('  ⚠️  TRAILING COMMA!')
    
    if curve_plan:
        for i, arr in enumerate(curve_plan[-1:]):
            print(f'Last curvePlan: [{arr[:100]}...]')
            if arr.rstrip().endswith(','):
                print('  ⚠️  TRAILING COMMA!')
    
    # Check for makeChartSVG function
    if 'function makeChartSVG' in main_script:
        idx = main_script.find('function makeChartSVG')
        context = main_script[idx:idx+100]
        print(f'\nmakeChartSVG: {context}')
    
    # Check for isFirstOfMonth or xLabels
    if 'isFirstOfMonth' in main_script:
        print('\n✓ isFirstOfMonth found (x-axis fix active)')
    if 'function tooltipCircles' in main_script:
        print('✓ tooltipCircles function found')
    
    # Check for the specific error position
    # If error is at pos 8 in dataSets, check char at that position
    data_start = main_script.find('const dataSets = {')
    if data_start >= 0:
        data_obj = main_script[data_start + len('const dataSets = '):]
        print(f'\nDataSets object start: {repr(data_obj[:50])}')
