"""Update dashboard HTML with 04 Juni 2026 progress data from PDF."""
import re, shutil

HTML_PATH = r'H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html'
html = open(HTML_PATH, encoding='utf-8', errors='ignore').read()

# Data 04 Juni dari PDF
new_data = {
    "Gedung B": {
        "date": "04 Juni 2026",
        "dailyPlan": 0.37,
        "dailyReal": 0.03,
        "cumPlan": 4.93,
        "cumReal": 5.18,
        "deviation": 0.25,
        "new_label": "4 Jun",
        "new_curvePlan": 4.93,
        "new_curveReal": 5.18,
    },
    "Gedung D": {
        "date": "04 Juni 2026",
        "dailyPlan": 0.27,
        "dailyReal": 0.30,
        "cumPlan": 6.83,
        "cumReal": 7.52,
        "deviation": 0.69,
        "new_label": "4 Jun",
        "new_curvePlan": 6.83,
        "new_curveReal": 7.52,
    },
    "Gedung K": {
        "date": "04 Juni 2026",
        "dailyPlan": 0.09,
        "dailyReal": 0.23,
        "cumPlan": 4.71,
        "cumReal": 5.59,
        "deviation": 0.88,
        "new_label": "4 Jun",
        "new_curvePlan": 4.71,
        "new_curveReal": 5.59,
    },
}

# Find daily section
daily_start = html.find('daily: {')
daily_end = html.find('mode: "weekly"', daily_start)
if daily_end < 0:
    daily_end = len(html)

daily_section = html[daily_start:daily_end]

# Find buildings array
buildings_start = daily_section.find('buildings: [')
inner = daily_section[buildings_start + 11:]

# Parse building objects
objs = []
depth = 0
obj_start = -1
for i, c in enumerate(inner):
    if c == '{':
        depth += 1
        if depth == 1:
            obj_start = i
    elif c == '}':
        depth -= 1
        if depth == 0:
            objs.append((obj_start, i + 1, inner[obj_start:i + 1]))
            if len(objs) >= 3:
                break

print(f"Found {len(objs)} buildings")

abs_buildings_start = daily_start + buildings_start + 11
modifications = []

for idx, (start, end, obj) in enumerate(objs[:3]):
    name_m = re.search(r'name:\s*"([^"]+)"', obj)
    name = name_m.group(1) if name_m else None
    if name not in new_data:
        print(f"  Skipping {name}")
        continue

    d = new_data[name]
    abs_start = abs_buildings_start + start

    print(f"\nUpdating {name}:")

    # 1. Update date
    date_pattern = r'(date:\s*")[^"]*(")'
    date_match = re.search(date_pattern, obj)
    if date_match:
        old_date = date_match.group(0)
        new_date = f'date: "{d["date"]}"'
        modifications.append((abs_start + date_match.start(), abs_start + date_match.end(), old_date, new_date))
        print(f"  date: {old_date} -> {new_date}")

    # 2. Update scalar fields
    for field in ['dailyPlan', 'dailyReal', 'cumPlan', 'cumReal', 'deviation']:
        pattern = r'(\b' + field + r'\s*:\s*)[0-9.-]+'
        m = re.search(pattern, obj)
        if m:
            old_val = m.group(0)
            new_val = f'{m.group(1)}{d[field]}'
            modifications.append((abs_start + m.start(), abs_start + m.end(), old_val, new_val))
            print(f"  {field}: {old_val} -> {new_val}")

    # 3. Append to labels array
    labels_pattern = r'(labels:\s*\[)(.*?)(\])'
    lm = re.search(labels_pattern, obj, re.DOTALL)
    if lm:
        old_labels = lm.group(0)
        if '4 Jun' not in old_labels:
            new_labels = lm.group(1) + lm.group(2).rstrip() + f', "{d["new_label"]}"' + lm.group(3)
            modifications.append((abs_start + lm.start(), abs_start + lm.end(), old_labels, new_labels))
            print(f"  labels: appended {d['new_label']}")

    # 4. Append to curvePlan
    cp_pattern = r'(curvePlan:\s*\[)(.*?)(\])'
    cpm = re.search(cp_pattern, obj, re.DOTALL)
    if cpm:
        old_cp = cpm.group(0)
        if str(d['new_curvePlan']) not in old_cp.split(',')[-1]:
            new_cp = cpm.group(1) + cpm.group(2).rstrip() + f', {d["new_curvePlan"]}' + cpm.group(3)
            modifications.append((abs_start + cpm.start(), abs_start + cpm.end(), old_cp, new_cp))
            print(f"  curvePlan: appended {d['new_curvePlan']}")

    # 5. Append to curveReal
    cr_pattern = r'(curveReal:\s*\[)(.*?)(\])'
    crm = re.search(cr_pattern, obj, re.DOTALL)
    if crm:
        old_cr = crm.group(0)
        if str(d['new_curveReal']) not in old_cr.split(',')[-1]:
            new_cr = crm.group(1) + crm.group(2).rstrip() + f', {d["new_curveReal"]}' + crm.group(3)
            modifications.append((abs_start + crm.start(), abs_start + crm.end(), old_cr, new_cr))
            print(f"  curveReal: appended {d['new_curveReal']}")

# Update sourceDate
source_pattern = r'(sourceDate:\s*")[^"]*(")'
sm = re.search(source_pattern, html[daily_start:daily_end])
if sm:
    abs_sm = daily_start + sm.start()
    old_source = sm.group(0)
    new_source = 'sourceDate: "Laporan harian cutoff 04 Juni 2026"'
    modifications.append((abs_sm, abs_sm + len(old_source), old_source, new_source))
    print(f"\n  sourceDate: {old_source} -> {new_source}")

# Apply modifications from bottom to top
modifications.sort(key=lambda x: x[0], reverse=True)

result = html
for start, end, old, new in modifications:
    result = result[:start] + new + result[end:]

# Backup and write
backup_path = HTML_PATH + '.backup_04jun'
shutil.copy2(HTML_PATH, backup_path)
print(f"\nBackup saved: {backup_path}")

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"HTML updated! Total modifications: {len(modifications)}")
