#!/usr/bin/env python3
"""Clean up duplicate trailing data in dashboard HTML after buildings arrays."""

import re

html_path = r"H:\My Drive\Work in Progress\08 Laporan Progress Proyek\Dashboard\Dashboard_Perkembangan_Proyek_Renovasi_Pejaten.html"
html = open(html_path, encoding="utf-8").read()

print(f"Original size: {len(html):,} chars")

# The regex replacement left old data after each buildings array.
# We need to find each `buildings: [...]` array and remove any old data
# that follows it before the section closing `},`

# Strategy: For each section, find the NEW buildings array (which ends with `],\n        }`)
# and remove any trailing old building data that follows.

# Fix: After each buildings array closing `],` there should be nothing but whitespace
# before the next `      },` (section end). If there's old data, remove it.

# Daily section fix
# Find: `        ],` (end of daily buildings array) followed by old data until `      },`
# The old data starts with `            curvePlan:` or `            name:`

# Let's find and remove the duplicate data patterns
# Pattern 1: After daily buildings `],` there's old curvePlan/curveReal/name data
daily_end_marker = '        ],\n      },'
weekly_end_marker = '        ],\n      },'
monthly_end_marker = '        ],\n    }'

# For daily: find the first `        ],` after `daily: {` and ensure what follows is clean
# The issue is that old data was appended after the new buildings array

# Let's use a more targeted approach:
# Find each section, extract just the buildings array we want, and rebuild

# Actually, the simplest fix: the duplicate data always starts with `            curvePlan:`
# or `            name: "Gedung` after the new buildings array closing.
# We can find these and remove them.

# Remove duplicate trailing building data after each section's buildings array
# These are blocks that start with indentation + `curvePlan:` or `name: "Gedung` 
# and appear AFTER the new buildings array

# Pattern: after `        ],` (buildings array end), remove everything until section end
for section in ['daily', 'weekly', 'monthly']:
    # Find the section
    section_match = re.search(rf'      {section}: \{{', html)
    if not section_match:
        continue
    
    section_start = section_match.start()
    
    # Find the NEW buildings array end (the one we just wrote)
    # It ends with `],\n        }` (for daily/weekly) or `],\n    }` (for monthly)
    if section == 'monthly':
        end_pattern = r'        ],\n    \}'
    else:
        end_pattern = r'        ],\n      \}'
    
    # Find all occurrences of buildings array end
    # The LAST one before the section end is the correct one
    # But we need to find the FIRST `        ],` that's followed by old data
    
    # Find `buildings: [` in this section
    bm = re.search(r'buildings: \[', html[section_start:])
    if not bm:
        continue
    
    bldg_start = section_start + bm.start()
    
    # Now scan forward to find the end of the buildings array
    # Count brackets from the `[`
    depth = 0
    i = bldg_start
    bldg_end = None
    while i < len(html):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                bldg_end = i + 1
                break
        i += 1
    
    if bldg_end is None:
        continue
    
    # Now find where the section ends (next `      },` or `    }` for monthly)
    if section == 'monthly':
        section_end_match = re.search(r'\n    \}', html[bldg_end:])
    else:
        section_end_match = re.search(r'\n      \},', html[bldg_end:])
    
    if not section_end_match:
        continue
    
    section_end = bldg_end + section_end_match.end()
    
    # Check if there's duplicate data between bldg_end and section_end
    between = html[bldg_end:section_end]
    
    # The between should just be whitespace/commas
    # If it contains `name:` or `curvePlan:`, it's duplicate data
    if 'name:' in between or 'curvePlan' in between:
        # Remove the duplicate data, keep just the whitespace/newline before section end
        # Find the position of the section end marker
        if section == 'monthly':
            cleanup_end = bldg_end + section_end_match.start()
            # Keep a newline before the closing brace
            html = html[:bldg_end] + '\n    ' + html[cleanup_end:]
        else:
            cleanup_end = bldg_end + section_end_match.start()
            html = html[:bldg_end] + '\n      ' + html[cleanup_end:]
        
        print(f"  Cleaned {section}: removed duplicate data ({len(between)} chars)")

# Write back
open(html_path, 'w', encoding="utf-8").write(html)
print(f"Final size: {len(html):,} chars")
print("Done!")
