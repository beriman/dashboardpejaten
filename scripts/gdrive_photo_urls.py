#!/usr/bin/env python3
"""Generate Google Drive direct image URLs and inject into dashboard data.

Uses rclone to list files in Google Drive Dokumentasi folder,
then generates direct image URLs for each photo.

Direct URL format: https://lh3.googleusercontent.com/d/{FILE_ID}=w{size}-h{size}-no
Alternative: https://drive.google.com/uc?export=view&id={FILE_ID}
"""

import json
import subprocess
import re
import sys
from pathlib import Path
from datetime import datetime

# Config
GDRIVE_BASE = "Work in Progress/08 Laporan Progress Proyek/Dokumentasi"
BUILD_SCRIPT_DIR = Path(__file__).parent.parent

MONTH_FOLDERS = {
    "April": "1. Dokumentasi April",
    "Mei": "2. Dokumentasi Mei",
    "Juni": "3. Dokumentasi Juni",
}

MONTH_NUM = {
    "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
    "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
    "September": "09", "Oktober": "10", "November": "11", "Desember": "12",
}

BUILDING_CODES = ["B", "D", "K"]


def rclone_lsjson(path):
    """List files in Google Drive folder via rclone.
    Path should use the EXACT folder names from Google Drive (may include fullwidth slashes)."""
    full_path = f"gdrive:{GDRIVE_BASE}/{path}"
    result = subprocess.run(
        ["rclone", "lsjson", full_path],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        print(f"  ERROR listing {path}: {result.stderr[:200]}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def rclone_lsf_dirs(path):
    """List directories in Google Drive folder via rclone."""
    full_path = f"gdrive:{GDRIVE_BASE}/{path}"
    result = subprocess.run(
        ["rclone", "lsf", full_path, "--dirs-only"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        return []
    return [d.strip() for d in result.stdout.strip().split("\n") if d.strip()]


def generate_direct_url(file_id, size=800):
    """Generate Google Drive direct image URL."""
    return f"https://lh3.googleusercontent.com/d/{file_id}=w{size}-h{size}-no"


def parse_date_folder(folder_name):
    """Parse date from folder name like '04 06 2026' or '04／06／2026'."""
    # Normalize fullwidth slashes
    normalized = folder_name.replace("／", "/").replace(" ", "/")
    parts = normalized.split("/")
    if len(parts) == 3:
        day, month, year = parts
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None


def collect_photos_for_date(month_folder, date_folder):
    """Collect all photos for a specific date across all buildings.
    date_folder should use EXACT Google Drive folder name (may include fullwidth slashes)."""
    # Normalize for display only
    date_display = date_folder.replace("／", "/").rstrip("/")
    date_path = f"{month_folder}/{date_folder}"
    buildings = {}
    
    for bcode in BUILDING_CODES:
        b_path = f"{date_path}/{bcode}"
        files = rclone_lsjson(b_path)
        photos = []
        for f in files:
            if not f.get("IsDir") and f.get("MimeType", "").startswith("image/"):
                photos.append({
                    "id": f["ID"],
                    "name": f["Name"],
                    "url": generate_direct_url(f["ID"]),
                    "size": f.get("Size", 0),
                })
        if photos:
            buildings[bcode] = photos
    
    return buildings, date_display


def main():
    print("=== Google Drive Photo URL Generator ===\n")
    
    # Find the latest date folder in the latest month
    latest_month = "3. Dokumentasi Juni"
    print(f"Scanning {latest_month}...")
    
    date_folders_raw = rclone_lsf_dirs(latest_month)
    if not date_folders_raw:
        print("  No date folders found!")
        return
    # Keep original names for rclone, normalized for display
    date_folders = [d.rstrip("/") for d in date_folders_raw]
    
    # Sort by date (newest first) — use normalized for sorting
    date_folders.sort(key=lambda d: d.replace("／", "/"), reverse=True)
    latest_date = date_folders[0]
    latest_date_display = latest_date.replace("／", "/")
    print(f"  Latest date folder: {latest_date_display}")
    
    # Collect photos
    buildings, date_display = collect_photos_for_date(latest_month, latest_date)
    
    total = 0
    for bcode, photos in buildings.items():
        print(f"  {bcode}: {len(photos)} photos")
        total += len(photos)
    print(f"\n  Total: {total} photos")
    
    # Output as JSON for build script consumption
    output = {
        "date_folder": date_display,
        "date_iso": parse_date_folder(date_display),
        "buildings": {
            bcode: [
                {
                    "src": p["url"],
                    "name": re.sub(r'\s+\(\d+\)', '', p["name"]).replace('.JPG', '').replace('.jpg', '').strip(),
                    "takenDate": parse_date_folder(latest_date) or latest_date,
                    "fileId": p["id"],
                }
                for p in photos
            ]
            for bcode, photos in buildings.items()
        }
    }
    
    # Write to file for build script to consume
    output_path = BUILD_SCRIPT_DIR / "scripts" / "gdrive_photos.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Written to: {output_path}")
    
    # Also print summary
    print("\n=== Summary ===")
    print(f"Date: {date_display}")
    for bcode, photos in output["buildings"].items():
        print(f"  {bcode}: {len(photos)} photos")
        for p in photos[:2]:
            print(f"    - {p['name'][:50]}")
        if len(photos) > 2:
            print(f"    ... and {len(photos)-2} more")


if __name__ == "__main__":
    main()
