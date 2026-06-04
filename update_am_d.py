#!/usr/bin/env python3
"""
Update monitoring approval material Gedung D berdasarkan Outline Spec terbaru.
- Update spesifikasi material yang sudah ada
- Tambah material baru dari outline spec
"""

import re, json

JS_PATH = r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\approval_material_monitoring_data.js"

with open(JS_PATH, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"window\.APPROVAL_MATERIAL_MONITORING_DATA\s*=\s*(\{.+\});", content, re.DOTALL)
data = json.loads(match.group(1))

# Find Gedung D building
gd = None
for b in data["buildings"]:
    if b.get("buildingCode") == "D":
        gd = b
        break

if not gd:
    print("ERROR: Gedung D not found!")
    exit(1)

print(f"Gedung D: {len(gd['materials'])} materials currently")

# ─── Updates: modify existing materials ───
updates = {
    # Beton ready mix - update spec
    "AM-GD-STR-106": {
        "specification": "fc' = 30 Mpa (Pile cap, dinding beton, kolom, balok, pelat, tiang bor); fc' = 45 Mpa khusus Tiang Pancang; Semen Portland Tipe 1; Agregat SNI 8321-2016 / ASTM C-33; Air SNI 7974:2016",
        "productRef": "Ready Mix: Karya Beton, Jaya Mix"
    },
    # Besi tulangan - update spec
    "AM-GD-STR-107": {
        "specification": "BJTS-420 (Yield Strength min. 420 Mpa, maks. 545 Mpa; Kuat tarik min. 525 Mpa); SNI 2052:2024",
        "productRef": "Master Steel, Interwood Steel, Cakra Tunggal Steel, Jaya Steel, Krakatau Steel"
    },
    # Baja struktur - update spec
    "AM-GD-STR-111": {
        "specification": "Pipa Schedule A-36; Baja Profil A-36; Las AWS E-70XX; Baut ASTM A-325",
        "productRef": "Gunung Garuda, Hanin Jaya Steel, Krakatau Osaka Steel, Garuda Yamato Steel"
    },
    # Waterproofing struktur - update spec
    "AM-GD-STR-114": {
        "specification": "MEMBRANE: Sika Bitusel T-130SG, Tamseal, Fosroc, Penetron atau setara (plat atap & plat exterior); SPRAY: Sika, Fosroc, Penetron; COATING: Sika, Fosroc, Penetron; INTEGRAL: untuk GWT & STP",
        "productRef": "Sika, Fosroc, Penetron atau setara"
    },
    # Tiang pancang - update spec
    "AM-GD-STR-104": {
        "specification": "Beton mutu fc' 45 Mpa; Baja Tulangan Ulir BJTS 420; Mutu strand ASTM A416 grade 270",
        "productRef": "PPI, JHS, Tripalindo P"
    },
}

updated = 0
for mat_id, changes in updates.items():
    for m in gd["materials"]:
        if m["id"] == mat_id:
            for key, val in changes.items():
                m[key] = val
            updated += 1
            print(f"  Updated: {mat_id} - {m['materialName']}")
            break

# ─── Add new materials from outline spec ───
new_materials = [
    {
        "id": "AM-GD-STR-175",
        "buildingCode": "D",
        "discipline": "STR",
        "workPackage": "Struktur Beton",
        "materialName": "Semen Portland",
        "specification": "Warna abu-abu, bentuk powder; SNI 2049:2015 / ASTM C 150/C150M-12 / BS 197-1:2000; Kemasan 40 kg, 50 kg",
        "productRef": "Semen Tiga Roda, Semen Gresik, Semen Merah Putih, Semen Padang",
        "referenceDocument": "Outline Spek Struktur - A.1",
        "priority": "Tinggi",
        "status": "notStarted",
        "approvalDate": None,
        "notes": "Perlu sample approval"
    },
    {
        "id": "AM-GD-STR-176",
        "buildingCode": "D",
        "discipline": "STR",
        "workPackage": "Struktur Beton",
        "materialName": "Beton fc' 45 Tiang Pancang",
        "specification": "Kuat tekan 45 Mpa khusus Tiang Pancang; Semen Portland Tipe 1; Agregat SNI 8321-2016; Air SNI 7974:2016",
        "productRef": "Ready Mix: Karya Beton, Jaya Mix",
        "referenceDocument": "Outline Spek Struktur - A.2",
        "priority": "Tinggi",
        "status": "notStarted",
        "approvalDate": None,
        "notes": "Terpisah dari beton fc'30 struktur umum"
    },
]

for nm in new_materials:
    # Check if already exists
    exists = any(m["id"] == nm["id"] for m in gd["materials"])
    if not exists:
        gd["materials"].append(nm)
        print(f"  Added: {nm['id']} - {nm['materialName']}")

# Update summary
total = len(gd["materials"])
approved = sum(1 for m in gd["materials"] if m.get("status") == "approved")
not_started = sum(1 for m in gd["materials"] if m.get("status") in ("notStarted", "draft"))
submitted = sum(1 for m in gd["materials"] if m.get("status") == "submitted")
revise = sum(1 for m in gd["materials"] if m.get("status") in ("reviseAndResubmit", "rejected", "hold"))

gd["summary"] = {
    "total": total,
    "notStartedOrDraft": not_started,
    "submitted": submitted,
    "approved": approved,
    "approvedAsNoted": 0,
    "reviseRejectedHold": revise,
    "highPriority": sum(1 for m in gd["materials"] if m.get("priority") == "Tinggi")
}

# Update lastUpdated
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=7))
data["lastUpdated"] = datetime.now(tz).isoformat()
data["sourceNote"] = f"Data di-update berdasarkan Outline Spec Gedung D terbaru. Total {total} item Gedung D."

# ─── Save ───
# Rebuild JS content
new_js = f"// approval_material_monitoring_data.js\n"
new_js += f"// Auto-generated by scripts/update_approval_material_monitoring_data.py\n"
new_js += f"// Source: H:\\\\My Drive\\\\Work in Progress\\\\07 Quality Control\\\\Approval Material\n"
new_js += f"// Generated: {datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}\n"
new_js += f"// Status: Gedung B: 0/84 approved (0.0%), Gedung D: {approved}/{total} approved ({approved/total*100:.1f}%), Gedung K: 0/72 approved (0.0%)\n"
new_js += f"window.APPROVAL_MATERIAL_MONITORING_DATA = {json.dumps(data, indent=2, ensure_ascii=False)};\n"

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(new_js)

print(f"\n✅ Updated Gedung D: {total} total materials ({updated} updated, {len(new_materials)} added)")
print(f"   Approved: {approved}, Not Started: {not_started}, Submitted: {submitted}, Revise: {revise}")
print(f"   Saved: {JS_PATH}")
