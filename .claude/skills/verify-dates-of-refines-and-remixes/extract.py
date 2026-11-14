"""Usage (from the repo root): python3 -I .claude/skills/verify-dates-of-refines-and-remixes/extract.py <version-prefix> [versions...]
e.g. `extract.py 6.` (all 6.x listed on the wiki) or `extract.py 10. 10.1 10.2` (explicit versions).
Prints per version: news date, new character-specific weapons, refines, remixed skills (new skills
added to Legendary/Mythic Heroes), other new skills (2.0-style "prereq -> added skill" tables, e.g.
staff +, assist + and evolution-only weapons; check those by hand, an evolution target may predate
the update), matching skill entries (id | name | base/refine/remix/other release_date
release_date_verified version) and MISMATCH lines.
Handles both link styles: [[Name]] (3.x+) and {{Wt|Name}} / {{NewsWeapon|Name|...}} /
{{NewsWikilink|Name}} (2.x). Evolution lines (`X → Y`) are skipped."""
import json, re, sys, urllib.request, urllib.parse
API = 'https://feheroes.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&titles='
def wiki(title):
  return json.load(urllib.request.urlopen(urllib.request.Request(API + urllib.parse.quote(title), headers={'User-Agent': 'Mozilla/5.0'})))['query']['pages'][0]

# weapon names: [[Name]] right after an icon/link, or a 2.x template whose first argument is the name
NAME = re.compile(r'(?:(?<=\}\})|(?<=\]\]))\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]|\{\{(?:Wt|NewsWeapon|NewsWikilink)\|([^}|]+)')
STOP = {'Weapon Refinery', 'Book I, Chapter 13', 'Chapter 13', 'The Rite of Blades', 'Intermission',
        'Arena', 'Arena Medal', 'Arena Medals', 'Divine Dew', 'Refining Stones', 'Learn Skills', 'Allies menu'}
def names(text):
  out = []
  for line in text.splitlines():
    if '→' in line: continue  # evolution, not a refine
    for m in NAME.finditer(line):
      n = re.sub(r' \((?:weapon|sword|lance|axe|bow|dagger|tome|staff|breath|beast)\)$', '', (m.group(1) or m.group(2)).strip())
      if ':' in n or n in STOP or n in out: continue  # heroes ("Name: Title"), files
      out.append(n)
  return out
REFINE_START = re.compile(r'special effects|can now be (?:strengthened|upgraded)')

c = wiki('List_of_version_updates')['revisions'][0]['slots']['main']['content']
skills = json.load(open('data/skills.json'))
pref = sys.argv[1]
vers = re.findall(r"'''Version (" + re.escape(pref) + r"\d+)\.0'''", c)
if len(sys.argv) > 2: vers = sys.argv[2:]
for v in sorted(set(vers), key=lambda s: [int(x) for x in s.split('.')]):
  i = c.find("'''Version " + v + ".0'''")
  t = re.search(r'\[\[([^\]]+)\]\]', c[i:]).group(1) if i >= 0 else "What's in Store for the " + v + ".0 Update (Notification)"
  p = wiki(t)
  if 'revisions' not in p: print('=====', v, t, 'MISSING PAGE'); continue
  s = p['revisions'][0]['slots']['main']['content']
  date = re.findall(r'\{\{News\|date=([^|}T]*)', s)
  print('=====', v, date, t)
  heads = re.findall(r'NewsTitle\|(■[^}]*)', s)
  new, ref, other = [], [], []
  for h in heads:
    if not re.search(r'(?i)weapon|refin|stave|staff', h): continue
    a = s.find(h); b = s.find('{{NewsTitle|■', a + 10); sec = s[a:b if b > 0 else None]
    m = re.search('special effects', sec) or REFINE_START.search(sec)
    k = m.start() if m else -1
    x = max(sec.find('character-specific'), sec.find('unit-specific'))
    if x >= 0:
      ends = [e for e in (sec.find('・', x), k if k > x else -1) if e > 0]
      new += [n for n in names(sec[x:min(ends) if ends else None]) if n not in new]
    if k >= 0: ref += [n for n in names(sec[k:]) if n not in ref]
    # 2.0-style tables: "| {{Wt|prereq}}\n| {{Wt|added skill}}"
    other += [n for n in re.findall(r'\{\{!\}\} \{\{(?:Wt|At)\|[^}]+\}\}\n\{\{!\}\} \{\{(?:Wt|At)\|([^}]+)\}\}', sec) if n not in other]
  # remixed skills: only those flagged with the "new skill" icon (the rest of the hero's kit already existed);
  # piped links point to the base skill page ([[Atrocity|Atrocity II]]), so keep the displayed name;
  # some pages (5.7, 5.11) link the base skill unpiped, only the icon keeps the suffix
  # ({{NewsIcon|Laws of Sacae II.png}}[[Laws of Sacae]]), so take " II"/"+"/" E" from the icon
  # (" E" = Emblem Hero remix, id suffix ・紋, e.g. Great Aether E in 10.10)
  remix = []
  # the flag is "News icon new skill.png", or "Icon new.png" on some pages (5.5)
  for icon, t, d in re.findall(r'(?:News icon new skill|Icon new)\.png[^\n]*?(?:\{\{NewsIcon\|([^}|]*)\.png\}\})?\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', s):
    n = d or t
    suf = re.search(r'( II|\+| E)$', icon)
    if suf and not n.endswith(suf.group(1)): n += suf.group(1)
    if n not in remix and n not in new and n not in ref: remix.append(n)
  other = [re.sub(r' \((?:weapon|sword|lance|axe|bow|dagger|tome|staff|breath|beast)\)$', '', n) for n in other]
  other = [n for n in other if n not in new and n not in remix]
  print(' NEW:', new); print(' REFINE:', ref); print(' REMIX:', remix)
  if other: print(' OTHER:', other)
  for kind, ns in (('new', new), ('ref', ref), ('remix', remix), ('other', other)):
    for n in ns:
      # Falchion's variants are named "Falchion (Mystery)", "Falchion (Awakening)"...
      xs = [x for x in skills if x['name'] == n] or [x for x in skills if x['name'].startswith(n + ' (')]
      if not xs: print('   MISSING', n)
      for x in xs:
        if kind == 'ref' and not x.get('base_id'): continue
        if kind == 'other' and x.get('base_id'): continue  # their refines came later
        label = 'remix' if kind == 'remix' else 'refine' if x.get('base_id') else 'other' if kind == 'other' else 'base'
        print('  ', x['id'], '|', x['name'], '|', label, x.get('release_date'), x.get('release_date_verified'), x.get('version'))
        if (x.get('release_date'), x.get('version')) != (date[0] if date else None, v): print('   MISMATCH', x['id'], x['name'])
