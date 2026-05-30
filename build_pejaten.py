"""Build Vercel-ready index.html from Google Drive dashboard files.

Reads the local dashboard HTML + JS data files from Google Drive,
inlines everything into a single self-contained HTML file,
copies photo documentation from the Dokumentasi folder,
and writes to public/index.html for Vercel deployment.
"""

import json, re, shutil
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(r"C:\Users\bim\dashboardpejaten")
PUBLIC_DIR = REPO_DIR / "public"
SHARED_DIR = Path(r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard")
DOKUMEN_DIR = Path(r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dokumentasi")

DASHBOARD_FILE = "Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html"
DATA_FILES = [
    "shopdrawing_monitoring_data.js",
    "rfi_monitoring_data.js",
    "approval_material_monitoring_data.js",
    "pile_monitoring_data.js",
]
ASSET_FILES = [
    "denah_pancang_gedung_K.png",
]

MODELS_DIR = SHARED_DIR / "models"
PUBLIC_MODELS_DIR = PUBLIC_DIR / "models"

# Map Indonesian month names to folder names and number
MONTH_FOLDER = {
    "April": "1. Dokumentasi April",
    "Mei": "2. Dokumentasi Mei",
    "Juni": "3. Dokumentasi Juni",
}
MONTH_NUM = {
    "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
    "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
    "September": "09", "Oktober": "10", "November": "11", "Desember": "12",
}

# Mapping dashboard building names to Dokumentasi folder codes
BUILDING_CODE = {
    "Gedung B": "B",
    "Gedung D": "D",
    "Gedung K": "K",
}


def read_source(name: str) -> str:
    p = SHARED_DIR / name
    return p.read_text(encoding="utf-8", errors="ignore")


def source_path(name: str) -> Path:
    return SHARED_DIR / name


def inline_data_scripts(html: str) -> str:
    for name in DATA_FILES:
        js = read_source(name)
        js = js.replace("</script>", "<\\/script>")
        tag = f'<script src="{name}"></script>'
        replacement = f'<script>\n/* Inlined from {name} for web deployment */\n{js}\n</script>'
        if tag not in html:
            print(f"  WARNING: tag not found: {tag}")
            continue
        html = html.replace(tag, replacement)
        print(f"  Inlined: {name} ({len(js)} chars)")
    return html


def inject_build_info(html: str) -> str:
    stamp = datetime.now().strftime("%d %B %Y %H:%M")
    build_id = datetime.now().strftime("%Y%m%d%H%M%S")
    webchat_url = "https://t.me/Pejaten_bot"
    note = (
        f"<!-- Built from Google Drive on {stamp} WIB -->\n"
        f'<meta name="dashboard-build" content="Pejaten dashboard static build">\n'
        f'<meta name="dashboard-build-id" content="{build_id}">'
    )
    html = html.replace("</head>", f"  {note}\n</head>", 1)
    if 'meta name="webchat-url"' in html:
        html = html.replace(
            'meta name="webchat-url" content=""',
            f'meta name="webchat-url" content="{webchat_url}"',
        )
    html = html.replace(
        "</head>",
        f'<script>window.DASHBOARD_WEBCHAT_URL="{webchat_url}";</script>\n</head>',
        1,
    )
    return html


def copy_assets():
    for name in ASSET_FILES:
        src = source_path(name)
        dst = PUBLIC_DIR / name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied: {name} ({dst.stat().st_size} bytes)")
        else:
            print(f"  SKIP: {name} not found")


def copy_models():
    """Copy IFC 3D models from Google Drive to public/models for Vercel deployment."""
    if PUBLIC_MODELS_DIR.exists():
        shutil.rmtree(PUBLIC_MODELS_DIR)
    if MODELS_DIR.exists():
        shutil.copytree(MODELS_DIR, PUBLIC_MODELS_DIR)
        ifc_files = list(PUBLIC_MODELS_DIR.rglob("*.ifc"))
        print(f"  📦 Copied models/: {len(ifc_files)} IFC files")
        for f in ifc_files:
            rel = f.relative_to(PUBLIC_MODELS_DIR)
            print(f"     ✓ {rel} ({f.stat().st_size // 1024} KB)")
    else:
        print(f"  SKIP: models/ not found in Dashboard")


# ─── Dokumentasi Foto ────────────────────────────────────────────────────────

def parse_date_id(date_str: str):
    """Parse an Indonesian date string into (month_folder, date_folder) tuple.

    Handles formats:
      - "25 Mei 2026"          (daily mode)
      - "M9 (25 MEI 2026)"     (weekly mode — extracts from parentheses)
      - "BULAN 2 s.d. M6"      (monthly mode — returns None, handled separately)

    Returns (month_folder, date_folder) or None if unparseable.
    """
    date_str_clean = date_str.strip()

    # Try "M9 (25 MEI 2026)" format — extract the parenthesised part
    m = re.search(r'\((\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\)', date_str_clean)
    if m:
        day, month_name, year = m.group(1), m.group(2).capitalize(), m.group(3)
    else:
        # Try "25 Mei 2026" format
        parts = date_str_clean.split()
        if len(parts) != 3:
            return None
        day, month_name, year = parts
        month_name = month_name.capitalize()

    month_num = MONTH_NUM.get(month_name)
    month_folder = MONTH_FOLDER.get(month_name)
    if not month_num or not month_folder:
        return None

    day_padded = day.zfill(2)
    date_folder = f"{day_padded} {month_num} {year}"
    return (month_folder, date_folder)


def find_photo_dir(month_folder: str, date_folder: str):
    """Find the photo directory for a given date, handling edge cases.

    1. Try exact match first.
    2. Try prefix match (handles "01 05 2026 (1)" etc.)
    3. Fallback to the latest available date in the same month that is <= target date.
       Returns (path, actual_date_folder) so the caller knows which date was used.
    """
    from datetime import datetime
    base = DOKUMEN_DIR / month_folder

    # 1. Exact match
    exact = base / date_folder
    if exact.is_dir():
        return exact, date_folder

    # 2. Prefix match (handles "01 05 2026 (1)" etc.)
    for d in base.iterdir():
        if d.is_dir() and d.name.startswith(date_folder):
            return d, d.name

    # 3. Fallback: find latest date <= target
    # Parse target date for comparison
    try:
        target_dt = datetime.strptime(date_folder, "%d %m %Y")
    except ValueError:
        return None, None

    best_dir = None
    best_date_str = None
    best_dt = None

    if base.is_dir():
        for d in sorted(base.iterdir()):
            if not d.is_dir():
                continue
            # Try to parse folder name like "25 05 2026" or "25 05 2026 (1)"
            folder_date_str = d.name.split(" (")[0]  # strip "(1)" suffix
            try:
                folder_dt = datetime.strptime(folder_date_str, "%d %m %Y")
            except ValueError:
                continue
            if folder_dt <= target_dt:
                if best_dt is None or folder_dt > best_dt:
                    best_dt = folder_dt
                    best_dir = d
                    best_date_str = d.name

    return best_dir, best_date_str


def get_building_photos(building_dir: Path):
    """Get sorted list of (filename, filepath) tuples from a building folder.

    Returns files sorted by modification time (newest first).
    """
    if not building_dir.is_dir():
        return []
    files = sorted(
        [(f.name, f) for f in building_dir.iterdir()
         if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")],
        key=lambda x: x[1].stat().st_mtime,
        reverse=True,
    )
    return files


def get_latest_photo_date() -> str:
    """Find the most recent date folder across all Dokumentasi months."""
    latest = None
    latest_path = None
    for month_dir in sorted(DOKUMEN_DIR.iterdir()):
        if not month_dir.is_dir() or month_dir.name == "desktop.ini":
            continue
        for date_dir in month_dir.iterdir():
            if not date_dir.is_dir() or date_dir.name == "desktop.ini":
                continue
            # Try to parse date from folder name
            m = re.match(r'(\d{2})\s+(\d{2})\s+(\d{4})', date_dir.name)
            if m:
                day, month, year = m.group(1), m.group(2), m.group(3)
                try:
                    dt = datetime(int(year), int(month), int(day))
                    if latest is None or dt > latest:
                        latest = dt
                        latest_path = date_dir
                except ValueError:
                    continue
    return latest_path


def build_photo_objects(photo_dir: Path, building_code: str, taken_date: str):
    """Build photo objects array for a building.

    Photo objects: { src, name, takenDate }
    src is a relative web path under fotos/<building>/
    """
    building_dir = photo_dir / building_code
    photos = get_building_photos(building_dir)

    photo_out_dir = PUBLIC_DIR / "fotos" / building_code
    photo_out_dir.mkdir(parents=True, exist_ok=True)

    result = []
    for filename, filepath in photos:
        # Copy (or overwrite) to public/fotos/<building>/
        dst = photo_out_dir / filename
        if not dst.exists() or filepath.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(filepath, dst)

        # Build clean name (remove extension, clean up)
        name = Path(filename).stem
        # Clean up common patterns
        name = re.sub(r'\s+\(\d+\)', '', name)  # remove " (1)", " (2)", etc.
        name = name.strip().capitalize()

        # URL-encode the src path for the web
        src = f"fotos/{building_code}/{filename.replace(' ', '%20')}"

        result.append({
            "src": src,
            "name": name,
            "takenDate": taken_date,
        })

    return result


def photo_json_array(photos: list) -> str:
    """Render a JS `photos: [...]` array, indented nicely for inlining."""
    if not photos:
        return "photos: []"
    lines = ["photos: ["]
    for i, p in enumerate(photos):
        comma = "," if i < len(photos) - 1 else ""
        lines.append(
            f'            {{"src": "{p["src"]}", '
            f'"name": "{p["name"]}", '
            f'"takenDate": "{p["takenDate"]}"}}{comma}'
        )
    lines.append("          ]")
    return "\n".join(lines)


def populate_photos(html: str) -> str:
    """Find every `photos: []` in the dataSets and replace with actual photos."""
    
    print("\n[FOTO] Scanning Dokumentasi folder...")

    # Build a cache: (month_folder, date_folder, building_code) → photo objects
    photo_cache = {}

    def get_cached_photos(month_folder, date_folder, building_code):
        key = (month_folder, date_folder, building_code)
        if key not in photo_cache:
            photo_dir, actual_date = find_photo_dir(month_folder, date_folder)
            if photo_dir:
                # Use actual_date from the folder that was found (may differ from requested)
                taken_date = actual_date if actual_date else date_folder
                photo_cache[key] = build_photo_objects(photo_dir, building_code, taken_date)
                photo_cache[key + ('_actual_date',)] = taken_date  # store for logging
            else:
                photo_cache[key] = []
        return photo_cache[key]

    # Strategy: find each building block in the dataSets, extract its date field,
    # look up photos, and replace the photos: [] inside that block.
    #
    # We match patterns like:
    #   name: "Gedung B",
    #   date: "25 Mei 2026",
    #   ...
    #   photos: []
    #
    # We use regex to find each building block and replace its photos: [] line.

    replacement_count = 0

    # Match each building block: from `name: "Gedung X"` until the next `}` or end
    # More precisely: find `photos: []` and look backwards for the date and name.
    
    # Pattern: a building object inside dataSets
    # We'll find all `photos: []` occurrences and try to resolve each one.
    
    lines = html.split("\n")
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this line is "photos: []" or "photos: []," 
        if re.match(r'\s*photos:\s*\[\]', stripped):
            # Look back through previous lines to find name and date
            building_name = None
            building_date = None
            for j in range(i - 1, max(i - 20, -1), -1):
                prev = lines[j]
                m_name = re.search(r'name:\s*"([^"]+)"', prev)
                if m_name:
                    building_name = m_name.group(1)
                    break
            
            for j in range(i - 1, max(i - 20, -1), -1):
                prev = lines[j]
                m_date = re.search(r'date:\s*"([^"]+)"', prev)
                if m_date:
                    building_date = m_date.group(1)
                    break
            
            if building_name and building_date:
                building_code = BUILDING_CODE.get(building_name)
                
                # Try to parse the date
                date_info = parse_date_id(building_date)
                
                if date_info and building_code:
                    month_folder, date_folder = date_info

                    photos = get_cached_photos(month_folder, date_folder, building_code)
                    actual_date = photo_cache.get((month_folder, date_folder, building_code, '_actual_date'), '')

                    if photos:
                        indent = line[:len(line) - len(line.lstrip())]
                        repl = photo_json_array(photos)
                        repl_lines = repl.split("\n")
                        repl_indented = "\n".join(
                            indent + rl if rl.strip() else rl
                            for rl in repl_lines
                        )
                        new_lines.append(repl_indented)
                        date_info = f"foto: {actual_date}" if actual_date and actual_date != date_folder else building_date
                        print(f"  ✅ {building_name} ({building_date}): {len(photos)} foto → fotos/{building_code}/ [{date_info}]")
                        replacement_count += 1
                        i += 1
                        continue

            # If we get here, no replacement happened
            # If it has trailing comma, leave it
            if stripped.endswith(","):
                # Check if it has a trailing comma
                new_lines.append(line.rstrip())
            else:
                new_lines.append(line.rstrip())
        
        elif re.match(r'\s*photos:\s*\[\],', stripped):
            # Same logic but with trailing comma
            # Look back for name and date
            building_name = None
            building_date = None
            for j in range(i - 1, max(i - 20, -1), -1):
                prev = lines[j]
                m_name = re.search(r'name:\s*"([^"]+)"', prev)
                if m_name:
                    building_name = m_name.group(1)
                    break
            
            for j in range(i - 1, max(i - 20, -1), -1):
                prev = lines[j]
                m_date = re.search(r'date:\s*"([^"]+)"', prev)
                if m_date:
                    building_date = m_date.group(1)
                    break
            
            if building_name and building_date:
                building_code = BUILDING_CODE.get(building_name)
                date_info = parse_date_id(building_date)
                
                if date_info and building_code:
                    month_folder, date_folder = date_info

                    photos = get_cached_photos(month_folder, date_folder, building_code)
                    actual_date = photo_cache.get((month_folder, date_folder, building_code, '_actual_date'), '')

                    if photos:
                        indent = line[:len(line) - len(line.lstrip())]
                        repl = photo_json_array(photos)
                        repl_lines = repl.split("\n")
                        repl_indented = "\n".join(
                            indent + rl if rl.strip() else rl
                            for rl in repl_lines
                        )
                        new_lines.append(repl_indented)
                        date_info = f"foto: {actual_date}" if actual_date and actual_date != date_folder else building_date
                        print(f"  ✅ {building_name} ({building_date}): {len(photos)} foto → fotos/{building_code}/ [{date_info}]")
                        replacement_count += 1
                        i += 1
                        continue

            # Fall through
            new_lines.append(line.rstrip())

        else:
            new_lines.append(line.rstrip())
        
        i += 1
    
    if replacement_count > 0:
        print(f"\n  📸 Total: {replacement_count} building-mode combo diperbarui dengan foto!")
    else:
        print(f"\n  ⚠️  Tidak ada foto yang ditemukan — periksa format tanggal di dashboard.")
    
    return "\n".join(new_lines)


# ─── Weighted Average Patch ───────────────────────────────────────────────────

CONTRACT_VALUES = {
    "Gedung B": 26851505405.41,
    "Gedung D": 31590007207.21,
    "Gedung K": 51151511711.71,
}


def inject_contract_values(html: str) -> str:
    """Inject contractValue into each building data object for weighted average calculation."""
    import re
    # Match: { name: "Gedung X",\n            date: ...
    # Insert contractValue right after the name field
    contract_map = {
        "Gedung B": 26851505405.41,
        "Gedung D": 31590007207.21,
        "Gedung K": 51151511711.71,
    }
    for name, value in contract_map.items():
        # Only inject if not already present
        # Pattern: name: "Gedung X",\n            date: "..."
        # We want to insert contractValue between name and date
        pattern = rf'(name:\s*"{re.escape(name)}",)(\s*\n\s*date:)'
        replacement = rf'\1\n            contractValue: {value},\2'
        if f'contractValue: {value}' not in html:
            new_html = re.sub(pattern, replacement, html)
            if new_html != html:
                print(f"  ✓ Injected contractValue for {name}")
                html = new_html
            else:
                print(f"  ⚠️  Pattern not found for {name}")
        else:
            print(f"  → contractValue for {name} already present, skipping")
    return html


def patch_weighted_average(html: str) -> str:
    """Replace simple average calculation with weighted average."""
    # Replace the avgProgress calculation
    old_code = "    const avg = arr => arr.reduce((a,b) => a+b,0) / arr.length;\n    const avgProgress = available.length ? avg(available.map(b => b.cumReal)) : 0;"
    new_code = """    const avg = arr => arr.reduce((a,b) => a+b,0) / arr.length;
    // Weighted average: sum(realization) / sum(contract) for accurate combined progress
    const avgProgress = available.length
      ? available.reduce((sum, b) => sum + (b.cumReal * (b.contractValue || 1)), 0) /
        available.reduce((sum, b) => sum + (b.contractValue || 1), 0)
      : 0;"""
    if old_code in html:
        html = html.replace(old_code, new_code)
        print("  ✓ Patched avgProgress to weighted average")
    else:
        print("  ⚠️  Could not find avgProgress code to patch — may already be patched")

    # Update card label
    old_label = 'Rata-rata progres gedung terbaca</div>\n              <div class="n">${avgProgress.toFixed(2)}%</div>\n              <div class="sub">rata-rata kumulatif realisasi Gedung B, D, dan K</div>'
    new_label = 'Rata-rata progres gedung tertimbang</div>\n              <div class="n">${avgProgress.toFixed(2)}%</div>\n              <div class="sub">rata-rata tertimbang realisasi Gedung B, D, dan K (berdasarkan nilai kontrak)</div>'
    if old_label in html:
        html = html.replace(old_label, new_label)
        print("  ✓ Updated card label")

    # Update combined chart subtitle
    old_subtitle = "'Gabungan sementara menggunakan rata-rata progres kumulatif dari gedung yang datanya sudah tersedia'"
    new_subtitle = "'Gabungan menggunakan rata-rata tertimbang berdasarkan nilai kontrak (B=Rp26,85M, D=Rp31,59M, K=Rp51,15M)'"
    if old_subtitle in html:
        html = html.replace(old_subtitle, new_subtitle)
        print("  ✓ Updated Kurva S subtitle")

    # Update footnote
    old_note = "Catatan: kurva gabungan ini masih bersifat indikatif karena bobot masing-masing gedung belum dibaca dari dokumen sumber, dan data DPT belum tersedia pada folder laporan harian yang dicek."
    new_note = "Kurva gabungan menggunakan rata-rata tertimbang berdasarkan nilai kontrak (B=Rp26,85M, D=Rp31,59M, K=Rp51,15M). Data DPT belum tersedia."
    if old_note in html:
        html = html.replace(old_note, new_note)
        print("  ✓ Updated footnote")

    return html

def cleanup_old_photos():
    """Remove old photos from public/fotos/ before copying new ones."""
    foto_dir = PUBLIC_DIR / "fotos"
    if foto_dir.is_dir():
        shutil.rmtree(foto_dir)
        print("  🧹 Cleaned old fotos/")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] Reading dashboard HTML...")
    html = read_source(DASHBOARD_FILE)
    print(f"  Loaded: {DASHBOARD_FILE} ({len(html)} chars)")

    print("[2/4] Populating photo documentation from Dokumentasi folder...")
    cleanup_old_photos()
    html = populate_photos(html)

    print("\n[3/4] Inlining data JS files...")
    html = inline_data_scripts(html)

    print("\n[4/4] Injecting build info & chat URL...")
    html = inject_build_info(html)

    # Inject contract values for weighted average calculation
    html = inject_contract_values(html)
    # Patch avgProgress to use weighted average instead of simple average
    html = patch_weighted_average(html)

    print("\n--- Writing index.html ---")
    out = PUBLIC_DIR / "index.html"
    out.write_text(html, encoding="utf-8")

    copy_assets()
    copy_models()

    # Also copy ifc-viewer.html and mobile-ui.js to public/
    viewer_src = SHARED_DIR / "ifc-viewer.html"
    viewer_dst = PUBLIC_DIR / "ifc-viewer.html"
    if viewer_src.exists():
        shutil.copy2(viewer_src, viewer_dst)
        print(f"  Copied: ifc-viewer.html")
    mobile_js_src = SHARED_DIR / "mobile-ui.js"
    mobile_js_dst = PUBLIC_DIR / "mobile-ui.js"
    if mobile_js_src.exists():
        shutil.copy2(mobile_js_src, mobile_js_dst)
        print(f"  Copied: mobile-ui.js")

    print(f"\n✅ DONE: {out} ({out.stat().st_size:,} bytes)")
    print(f"   Sekarang tinggal git add → commit → push, Vercel auto-deploy! 🚀")


if __name__ == "__main__":
    main()