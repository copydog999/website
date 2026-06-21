import json

filepath = r'd:\JOEST\database\data\nowbase.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0
for entry in data:
    fp = entry.get('filePath', '')
    if ' ' in fp:
        old_fp = fp
        new_fp = fp.replace(' ', '').replace('\t', '')
        entry['filePath'] = new_fp
        fixed_count += 1
        print(f'Entry {entry["id"]}: Fixed filePath')
        print(f'  Old: {old_fp}')
        print(f'  New: {new_fp}')

if fixed_count > 0:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\nFixed {fixed_count} filePath entries')
else:
    print('No filePath entries with spaces found')
