"""Usage: python3 fix.py <date> <version> <id> [<id> ...]
Sets addition_date/release_date/version and release_date_verified="manually" on the given skill ids.
Reports what changed per id. Preserves skills.json formatting (indent 2, no trailing newline)."""
import json, sys

P = 'data/skills.json'  # run from the repo root
date, version, *ids = sys.argv[1:]
ids = set(ids)
skills = json.load(open(P))
out = []
for x in skills:
    if x['id'] in ids:
        ids.discard(x['id'])
        before = {k: x.get(k) for k in ('addition_date', 'release_date', 'release_date_verified', 'version')}
        x.pop('release_date_verified', None)
        if 'release_date' not in x:
            x.update(addition_date=date, release_date=date, version=version)
        n = {}
        for k, v in x.items():
            n[k] = v
            if k == 'release_date':
                n['release_date_verified'] = 'manually'
        n['addition_date'] = n['release_date'] = date
        n['version'] = version
        after = {k: n.get(k) for k in before}
        diff = {k: (before[k], after[k]) for k in before if before[k] != after[k]}
        print(f"{x['id']} ({x['name']}):", diff or 'ok')
        x = n
    out.append(x)
if ids:
    sys.exit(f'NOT FOUND: {ids}')
open(P, 'w').write(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
