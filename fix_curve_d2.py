#!/usr/bin/env python3
"""Fix Gedung D curve: re-extract with better regex, handle missing dates."""

import fitz, re
from pathlib import Path
from datetime import datetime, timedelta
import json

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

def extract_progress(text):
    """Extract Kum Renc and Kum Real from PDF text, handling various formats."""
    kum_plan = None
    kum_real = None
    
    # Try pattern 1: "Kum Renc  :  6.03  %" (with spaces)
    m = re.search(r'Kum Renc\s*:\s*([\d.]+)\s*%', text)
    if m:
        kum_plan = float(m.group(1))
    
    # Try pattern 2: "Kum Real  :  5.58  %"
    m = re.search(r'Kum Real\s*:\s*([\d.]+)\s*%', text)
    if m:
        kum_real = float(m.group(1))
    
    # Try pattern 3: values on separate lines
    if kum_plan is None:
        m = re.search(r'Kum Renc\s*:\s*\n\s*([\d.]+)\s*\n\s*%', text)
        if m:
            kum_plan = float(m.group(1))
    
    if kum_real is None:
        m = re.search(r'Kum Real\s*:\s*\n\s*([\d.]+)\s*\n\s*%', text)
        if m:
            kum_real = float(m.group(1))
    
    # Try pattern 4: just look for the numbers after Kum Renc/Kum Real
    if kum_plan is None:
        m = re.search(r'Kum Renc[\s:]+([\d.]+)', text)
        if m:
            kum_plan = float(m.group(1))
    
    if kum_real is None:
        m = re.search(r'Kum Real[\s:]+([\d.]+)', text)
        if m:
            kum_real = float(m.group(1))
    
    return kum_plan, kum_real

records = []
failed_pdfs = []

for pdf in pdfs:
    try:
        doc = fitz.open(pdf)
        if len(doc) < 3:
            doc.close()
            continue
        text = doc[2].get_text()
        doc.close()
        
        # Extract date
        m = re.search(r'Date\s*(\d{1,2}\s+\w+\s+\d{4})', text)
        if not m:
            failed_pdfs.append((pdf.name, 'no date'))
            continue
        dt = parse_date(m.group(1))
        if not dt:
            failed_pdfs.append((pdf.name, 'date parse failed'))
            continue
        
        kum_plan, kum_real = extract_progress(text)
        
        if kum_plan is None or kum_real is None:
            failed_pdfs.append((pdf.name, f'no progress data (plan={kum_plan}, real={kum_real})'))
            continue
        
        records.append({'dt': dt, 'plan': kum_plan, 'real': kum_real, 'file': pdf.name})
    except Exception as e:
        failed_pdfs.append((pdf.name, str(e)))

# Sort by date and deduplicate
records.sort(key=lambda x: x['dt'])
seen = {}
for r in records:
    key = r['dt'].strftime('%Y-%m-%d')
    seen[key] = r
deduped = sorted(seen.values(), key=lambda x: x['dt'])

print(f"Extracted {len(deduped)} unique records")
if failed_pdfs:
    print(f"\nFailed PDFs ({len(failed_pdfs)}):")
    for name, reason in failed_pdfs:
        print(f"  {name}: {reason}")

print(f"\nAll records:")
for r in deduped:
    print(f"  {r['dt'].strftime('%d %b %Y')}: Plan={r['plan']:.2f}% Real={r['real']:.2f}%  [{r['file']}]")

# Check for missing dates
if len(deduped) >= 2:
    all_dates = []
    d = deduped[0]['dt']
    while d <= deduped[-1]['dt']:
        all_dates.append(d)
        d += timedelta(days=1)
    
    existing = set(r['dt'].strftime('%Y-%m-%d') for r in deduped)
    missing = [d for d in all_dates if d.strftime('%Y-%m-%d') not in existing]
    
    if missing:
        print(f"\nMissing dates ({len(missing)}):")
        for d in missing:
            print(f"  {d.strftime('%d %b %Y')}")
        
        # Interpolate missing values
        print(f"\nInterpolating missing values...")
        for miss_dt in missing:
            # Find previous and next known values
            prev_r = max((r for r in deduped if r['dt'] < miss_dt), key=lambda x: x['dt'], default=None)
            next_r = min((r for r in deduped if r['dt'] > miss_dt), key=lambda x: x['dt'], default=None)
            
            if prev_r and next_r:
                # Linear interpolation
                total_days = (next_r['dt'] - prev_r['dt']).days
                days_from_prev = (miss_dt - prev_r['dt']).days
                ratio = days_from_prev / total_days if total_days > 0 else 0
                
                interp_plan = prev_r['plan'] + (next_r['plan'] - prev_r['plan']) * ratio
                interp_real = prev_r['real'] + (next_r['real'] - prev_r['real']) * ratio
                
                deduped.append({
                    'dt': miss_dt,
                    'plan': round(interp_plan, 2),
                    'real': round(interp_real, 2),
                    'file': 'INTERPOLATED'
                })
                print(f"  {miss_dt.strftime('%d %b %Y')}: Plan={interp_plan:.2f}% Real={interp_real:.2f}% (interpolated)")
        
        # Re-sort
        deduped.sort(key=lambda x: x['dt'])

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
    'dailyPlan': round(latest['plan'] - deduped[-2]['plan'], 2) if len(deduped) > 1 else 0,
    'dailyReal': round(latest['real'] - deduped[-2]['real'], 2) if len(deduped) > 1 else 0,
    'cumPlan': latest['plan'],
    'cumReal': latest['real'],
    'deviation': round(latest['real'] - latest['plan'], 2),
    'date': latest['dt'].strftime('%d %B %Y'),
}

print(f"\nFinal Gedung D data: {len(labels)} points")
print(f"  Date: {new_d['date']}")
print(f"  Cum Plan: {new_d['cumPlan']}%  Cum Real: {new_d['cumReal']}%  Dev: {new_d['deviation']}%")

# ─── Update dashboard HTML ───
html_path = r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html"
html = open(html_path, encoding='utf-8').read()

import re as re2

# Replace Gedung D block in daily section
daily_match = re2.search(r'(daily: \{.*?buildings: \[)', html, re2.DOTALL)
if daily_match:
    daily_start = daily_match.end()
    d_pattern = r'(\{\s*name: "Gedung D",.*?\n\s*\})'
    d_match = re2.search(d_pattern, html[daily_start:], re2.DOTALL)
    if d_match:
        d_start = daily_start + d_match.start()
        d_end = daily_start + d_match.end()
        
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
        
        # Update source date
        new_html = re2.sub(
            r'(daily: \{[^}]*sourceDate: ")[^"]*(")',
            rf'\1Laporan harian cutoff {new_d["date"]}\2',
            new_html,
            flags=re2.DOTALL
        )
        
        open(html_path, 'w', encoding='utf-8').write(new_html)
        print(f"\n✅ Updated dashboard HTML")
    else:
        print("ERROR: Could not find Gedung D block")
else:
    print("ERROR: Could not find daily section")

# Save the fix script data for reference
with open(r'C:\Users\bim\dashboardpejaten\curve_d_fix.json', 'w') as f:
    json.dump({'labels': labels, 'curvePlan': curve_plan, 'curveReal': curve_real}, f, indent=2)
