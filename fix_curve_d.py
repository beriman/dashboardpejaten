#!/usr/bin/env python3
"""Rebuild Gedung D daily curve data from PDFs and update dashboard HTML."""

import fitz, re, os
from pathlib import Path
from datetime import datetime
import json

# ─── Extract all Gedung D harian data ───

base = Path(r'H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Laporan Harian\Laporan Harian Gedung D')
pdfs = sorted(base.rglob('*.pdf'), key=lambda p: p.stat().st_mtime)

MONTHS = {
    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4,
    'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8,
    'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
}

def parse_date(s):
    parts = s.strip().split()
    if len(parts) != 3:
        return None
    try:
        day = int(parts[0])
        month = MONTHS.get(parts[1].capitalize(), 0)
        year = int(parts[2])
        if month > 0:
            return datetime(year, month, day)
    except:
        pass
    return None

records = []
for pdf in pdfs:
    try:
        doc = fitz.open(pdf)
        if len(doc) < 3:
            doc.close()
            continue
        text = doc[2].get_text()
        doc.close()
        
        m = re.search(r'Date\s*(\d{1,2}\s+\w+\s+\d{4})', text)
        if not m:
            continue
        dt = parse_date(m.group(1))
        if not dt:
            continue
        
        m = re.search(r'Kum Renc\s*:\s*([\d.]+)%', text)
        kum_plan = float(m.group(1)) if m else None
        m = re.search(r'Kum Real\s*:\s*([\d.]+)%', text)
        kum_real = float(m.group(1)) if m else None
        
        if kum_plan is not None and kum_real is not None:
            records.append({'dt': dt, 'plan': kum_plan, 'real': kum_real})
    except Exception as e:
        print(f'ERROR: {pdf.name}: {e}')

# Sort by date and deduplicate (keep last per date)
records.sort(key=lambda x: x['dt'])
seen = {}
for r in records:
    key = r['dt'].strftime('%Y-%m-%d')
    seen[key] = r
deduped = sorted(seen.values(), key=lambda x: x['dt'])

print(f"Extracted {len(deduped)} unique daily records for Gedung D")
for r in deduped:
    print(f"  {r['dt'].strftime('%d %b %Y')}: Plan={r['plan']:.2f}% Real={r['real']:.2f}%")

# Build curve arrays
labels = []
curve_plan = []
curve_real = []
for r in deduped:
    labels.append(r['dt'].strftime('%d %b'))
    curve_plan.append(round(r['plan'], 2))
    curve_real.append(round(r['real'], 2))

latest = deduped[-1]
new_d = {
    'labels': labels,
    'curvePlan': curve_plan,
    'curveReal': curve_real,
    'dailyPlan': round(latest['plan'] - (deduped[-2]['plan'] if len(deduped) > 1 else 0), 2),
    'dailyReal': round(latest['real'] - (deduped[-2]['real'] if len(deduped) > 1 else 0), 2),
    'cumPlan': latest['plan'],
    'cumReal': latest['real'],
    'deviation': round(latest['real'] - latest['plan'], 2),
    'date': latest['dt'].strftime('%d %B %Y'),
}

print(f"\nNew Gedung D data:")
print(f"  Labels: {len(labels)} points")
print(f"  Date: {new_d['date']}")
print(f"  Cum Plan: {new_d['cumPlan']}%  Cum Real: {new_d['cumReal']}%  Dev: {new_d['deviation']}%")

# ─── Update dashboard HTML ───

html_path = r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html"
html = open(html_path, encoding='utf-8').read()

# Replace Gedung D building block in daily section
# Find the daily section and replace only Gedung D's data

# The pattern: find "name: \"Gedung D\"," in the daily section and replace the whole building block
import re

# Find daily section
daily_match = re.search(r'(daily: \{.*?buildings: \[)', html, re.DOTALL)
if not daily_match:
    print("ERROR: Could not find daily section!")
    exit(1)

daily_start = daily_match.end()

# Find Gedung D block within daily section — it starts with name: "Gedung D" and ends before the next name: or end of array
# We need to find the block for Gedung D specifically
d_pattern = r'(\{\s*name: "Gedung D",.*?\n\s*\})'
d_match = re.search(d_pattern, html[daily_start:], re.DOTALL)
if not d_match:
    print("ERROR: Could not find Gedung D block!")
    exit(1)

d_start = daily_start + d_match.start()
d_end = daily_start + d_match.end()

# Build new Gedung D block
labels_js = json.dumps(new_d['labels'])
plan_js = json.dumps(new_d['curvePlan'])
real_js = json.dumps(new_d['curveReal'])

new_d_block = f"""{{
            name: "Gedung D",
            date: "{new_d['date']}",
            dailyPlan: {new_d['dailyPlan']},
            dailyReal: {new_d['dailyReal']},
            cumPlan: {new_d['cumPlan']},
            cumReal: {new_d['cumReal']},
            deviation: {new_d['deviation']},
            note: "Data progres terbaca dari laporan harian.",
            labels: {labels_js},
            curvePlan: {plan_js},
            curveReal: {real_js},
            photos: []
          }}"""

new_html = html[:d_start] + new_d_block + html[d_end:]

# Also update source date
new_html = re.sub(
    r'(daily: \{[^}]*sourceDate: ")[^"]*(")',
    rf'\1Laporan harian cutoff {new_d["date"]}\2',
    new_html,
    flags=re.DOTALL
)

open(html_path, 'w', encoding='utf-8').write(new_html)
print(f"\n✅ Updated dashboard HTML: {html_path}")

# Verify
html_check = open(html_path, encoding='utf-8').read()
d_check = re.search(r'name: "Gedung D",.*?curveReal: \[.*?\]', html_check, re.DOTALL)
if d_check:
    # Extract just the key info
    m = re.search(r'date: "([^"]+)"', d_check.group())
    print(f"  Verified: date={m.group(1) if m else '?'}")
    m = re.search(r'cumPlan: ([\d.]+)', d_check.group())
    print(f"  Verified: cumPlan={m.group(1) if m else '?'}")
    m = re.search(r'labels: \[(.*?)\]', d_check.group(), re.DOTALL)
    if m:
        labels_in_html = m.group(1)
        print(f"  Verified: {len(labels_in_html.split(','))} labels")
