#!/usr/bin/env python3
"""Bandingkan file antara folder Drive (baru) dan folder lokal (lama) untuk deteksi duplikat."""
import os, hashlib, json
from pathlib import Path

BASE = r"H:\My Drive\Work in Progress\02 DED (gambar dari Perencana)\Gedung D"

# Folder yang baru di-download dari Drive
drive_folders = [
    "05. ARSITEKTUR_Drive",
    "06. INTERIOR_Drive", 
    "07. STRUKTUR_Drive",
    "08. INFRASTRUKTUR_Drive",
    "09. MEKANIKAL_Drive",
    "10. ELEKTRIKAL_Drive",
    "11. OUTLINE_SPEK_Drive",
    "12. RKS_Drive",
]

# Folder lokal yang sudah ada sebelumnya
local_folders = [
    "01. ARSITEKTUR-20260504T035629Z-3-001",
    "02. INTERIOR",
    "02. INTERIOR-20260504T035629Z-3-001",
    "03. STRUKTUR-20260504T035630Z-3-001",
    "04. INFRASTRUKTUR",
    "04. INFRASTRUKTUR-20260504T035630Z-3-001",
    "05. MEKANIKAL-20260504T035631Z-3-001",
    "06. ELEKTRIKAL",
    "06. ELEKTRIKAL-20260504T035637Z-3-001",
]

EXTS = {".pdf", ".dwg", ".dxf", ".xlsx", ".xls", ".docx", ".doc", ".pptx", ".rvt", ".ifc", ".pcp", ".rar"}

def scan_files(folders):
    """Scan all files in given folders, return {filename: [paths]}."""
    files = {}
    for folder in folders:
        fp = Path(BASE) / folder
        if not fp.exists():
            continue
        for f in fp.rglob("*"):
            if f.is_file() and f.suffix.lower() in EXTS:
                name = f.name.lower()
                if name not in files:
                    files[name] = []
                files[name].append(str(f))
    return files

print("Scanning Drive folders...")
drive_files = scan_files(drive_folders)
print(f"  Drive: {len(drive_files)} unique filenames")

print("Scanning local folders...")
local_files = scan_files(local_folders)
print(f"  Local: {len(local_files)} unique filenames")

# Find duplicates (same filename)
duplicates = []
drive_only = []
local_only = []

for name in sorted(drive_files.keys()):
    in_drive = name in drive_files
    in_local = name in local_files
    if in_drive and in_local:
        duplicates.append({
            "filename": name,
            "drive_paths": drive_files[name],
            "local_paths": local_files[name],
        })
    elif in_drive:
        drive_only.append(name)

for name in sorted(local_files.keys()):
    if name not in drive_files:
        local_only.append(name)

print(f"\n{'='*60}")
print(f"DUPLIKAT (nama file sama): {len(duplicates)}")
print(f"{'='*60}")
for d in duplicates[:50]:  # Show first 50
    print(f"\n  📄 {d['filename']}")
    for p in d['drive_paths']:
        print(f"     DRIVE: {p}")
    for p in d['local_paths']:
        print(f"     LOCAL: {p}")

if len(duplicates) > 50:
    print(f"\n  ... dan {len(duplicates) - 50} duplikat lainnya")

print(f"\n{'='*60}")
print(f"HANYA ADA DI DRIVE (baru): {len(drive_only)}")
print(f"{'='*60}")
for n in sorted(drive_only)[:30]:
    print(f"  + {n}")
if len(drive_only) > 30:
    print(f"  ... dan {len(drive_only) - 30} lainnya")

print(f"\n{'='*60}")
print(f"HANYA ADA DI LAMA (tidak ada di Drive): {len(local_only)}")
print(f"{'='*60}")
for n in sorted(local_only)[:30]:
    print(f"  - {n}")
if len(local_only) > 30:
    print(f"  ... dan {len(local_only) - 30} lainnya")

# Save report
report_path = Path(BASE) + r"\DUPLICATE_REPORT.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "duplicates": duplicates,
        "drive_only": drive_only,
        "local_only": local_only,
    }, f, indent=2, ensure_ascii=False)
print(f"\n📄 Report saved: {report_path}")
