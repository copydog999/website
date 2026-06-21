import json
import re

filepath = r'd:\JOEST\database\data\nowbase.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check filePath for spaces
for entry in data:
    fp = entry.get('filePath', '')
    if ' ' in fp:
        print(f'Entry {entry["id"]}: filePath has spaces')

# Count entries with references
ref_count = sum(1 for e in data if e.get('references'))
print(f'Total entries: {len(data)}')
print(f'Entries with references: {ref_count}')

# Now clean URLs in references
# Pattern: match https?:// (with optional spaces) up to a delimiter
# Delimiters: comma, newline, closing bracket, closing paren, or end of string
url_pattern = re.compile(r'https?\s*:\s*//[^,\]\\)\n]+')

total_replacements = 0
for entry in data:
    refs = entry.get('references', '')
    if not refs:
        continue
    
    original_refs = refs
    
    def clean_url(match):
        url = match.group(0)
        cleaned = url.replace(' ', '').replace('\t', '')
        return cleaned
    
    cleaned_refs = url_pattern.sub(clean_url, refs)
    
    if cleaned_refs != original_refs:
        entry['references'] = cleaned_refs
        # Count how many URLs were cleaned
        original_urls = url_pattern.findall(original_refs)
        total_replacements += len(original_urls)
        print(f'Entry {entry["id"]}: Cleaned {len(original_urls)} URLs')

print(f'\nTotal URLs cleaned: {total_replacements}')

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('File written successfully')
