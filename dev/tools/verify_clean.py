import json, re

with open(r'd:\JOEST\database\data\nowbase.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check a few entries with cleaned references
check_ids = [1, 45, 73]
for entry in data:
    if entry['id'] in check_ids:
        refs = entry.get('references', '')
        # Find URLs in references
        urls = re.findall(r'https?://[^\s,)\]]+', refs)
        print(f'Entry {entry["id"]}:')
        for u in urls[:4]:
            print(f'  {u}')
        print()

# Verify no spaces in any URL within references
all_refs = ' '.join(e.get('references', '') for e in data)
space_urls = re.findall(r'https?\s+://', all_refs)
if space_urls:
    print(f'WARNING: Found {len(space_urls)} URLs with spaces remaining!')
else:
    print('OK: No URLs with spaces found in references')

# Verify filePath
for entry in data:
    if ' ' in entry.get('filePath', ''):
        print(f'WARNING: Entry {entry["id"]} filePath still has spaces!')
        break
else:
    print('OK: All filePath entries are clean')
