#!/usr/bin/env python3
# Fix progress file - clean up wsaj full-title IDs
import json, re

PROGRESS_FILE = r'C:\Users\Mario\work\invest-sns\pipeline\data\godofIT_progress.json'

with open(PROGRESS_FILE, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print("Raw content length:", len(content))

# Parse manually to extract done list
# Keep only short IDs (valid YouTube IDs are typically 11 chars)
# wsaj_* full title entries need to be converted to just the YouTube ID

# Let's parse manually
# Find the done array
import re

# Extract clean IDs from the done list
clean_done = [
    '1NUkBQ9MQf8',
    '1iuRuDfMLUE', 
    '4wCO1fdl9iU',
    '8-hYd-8eojE',
    '8Nn3qerCt44',
    'I4Tt3tevuTU',
    'IjDhjDgC4Ao',
    'Ke7gQMbIFLI',
    'Sb3FpphamPo',
    'Xv-wNA91EPE',
    'XveVkr3JHs4',
    'f519DUfXkzQ',
    'jXME1wXZDRU',
    # wsaj processed ones - use extracted YouTube IDs
    '0pS0CTDgVmU',
    '57NbdmLvy6I',
    '5fhbkQ2Qidc',
    '7x3HE_uXttI',
]

progress = {
    'done': clean_done,
    'errors': [],
    'total_signals': 4,
    'total_cost': 2.536281
}

with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)

print(f"Fixed progress file: {len(clean_done)} done IDs")
print("Done IDs:", clean_done)
