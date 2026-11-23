#!/usr/bin/env python3
"""Check all public package files without network access or modifying evidence."""
from pathlib import Path
import hashlib
import sys

root=Path(__file__).resolve().parent
manifest=root/'SHA256SUMS'
errors=[]
expected={}
for line in manifest.read_text(encoding='utf-8').splitlines():
    digest, name=line.split('  ',1)
    path=Path(name)
    if path.is_absolute() or '..' in path.parts:
        errors.append('Unsafe manifest path: '+name)
        continue
    expected[name]=digest
    p=root/path
    if not p.is_file() or p.is_symlink():
        errors.append('Missing or non-regular: '+name)
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        errors.append('Changed: '+name)
actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=manifest and p.relative_to(root).parts[0]!='.git'}
for name in sorted(actual-set(expected)):
    errors.append('Unlisted: '+name)
if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(expected)} files match SHA256SUMS; no unlisted files.')
print('Integrity only: hashes do not independently authenticate capture dates or source truth.')
