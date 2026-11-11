"""Usage: python3 -I .claude/skills/fix-weapon-restrictions/fix.py [--apply]
Run from the repo root.

Lists every skill in data/skills.json whose restrictions.weapons is null, reads the skill's
canUseWeapon from the FEH wiki (by fandom_id) and prints the value it maps to.
With --apply, writes the mapped values to data/skills.json (2-space indent, final newline).
Skills whose wiki value is missing or unknown are reported and left untouched."""
import json, sys, urllib.parse, urllib.request

P = 'data/skills.json'
API = 'https://feheroes.fandom.com/api.php'
MAPPING = {
    '{{WeaponList|All}}': {'none': True},
    '{{WeaponList|exclude=Staff}}': {'can_not_use': ['Colorless Staff']},
}


def fetch_can_use_weapon(title):
    q = urllib.parse.urlencode({
        'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main',
        'format': 'json', 'formatversion': 2, 'redirects': 1, 'titles': title,
    })
    req = urllib.request.Request(f'{API}?{q}', headers={'User-Agent': 'feh-data-bot'})
    page = json.load(urllib.request.urlopen(req))['query']['pages'][0]
    if 'revisions' not in page:
        return None, page.get('title')
    text = page['revisions'][0]['slots']['main']['content']
    for line in text.splitlines():
        line = line.strip().lstrip('|').strip()
        if line.startswith('canUseWeapon='):
            return line.split('=', 1)[1].strip(), page['title']
    return '', page['title']


apply = '--apply' in sys.argv[1:]
text = open(P, encoding='utf-8').read()
skills = json.loads(text)
targets = [s for s in skills if 'weapons' in (s.get('restrictions') or {}) and s['restrictions']['weapons'] is None]
print(f'{len(targets)} skill(s) with "weapons": null')

cache = {}
changed = 0
for s in targets:
    title = urllib.parse.unquote(s.get('fandom_id') or s['name'])
    if title not in cache:
        cache[title] = fetch_can_use_weapon(title)
    value, page_title = cache[title]
    new = MAPPING.get(value)
    status = json.dumps(new) if new else f'UNKNOWN ({"page missing" if value is None else repr(value)})'
    print(f"{s['id']} | {s['name']} | wiki: {page_title} | {value} -> {status}")
    if new and apply:
        s['restrictions']['weapons'] = new
        changed += 1

if apply:
    out = json.dumps(skills, indent=2, ensure_ascii=False) + '\n'
    open(P, 'w', encoding='utf-8').write(out)
    print(f'{changed} skill(s) updated in {P}')
