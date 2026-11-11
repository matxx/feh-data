"""Usage (from the repo root): python3 -I .claude/skills/verify-refine-dates/extract.py <version-prefix> [versions...]
e.g. `extract.py 6.` (all 6.x listed on the wiki) or `extract.py 10. 10.1 10.2` (explicit versions).
Prints per version: news date, new character-specific weapons, refines, matching skill entries
(id | name | base/refine addition_date release_date release_date_verified version) and MISMATCH lines."""
import json,re,sys,urllib.request,urllib.parse
API='https://feheroes.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&titles='
def wiki(title):
  return json.load(urllib.request.urlopen(urllib.request.Request(API+urllib.parse.quote(title),headers={'User-Agent':'Mozilla/5.0'})))['query']['pages'][0]
c=wiki('List_of_version_updates')['revisions'][0]['slots']['main']['content']
skills=json.load(open('data/skills.json'))
pref=sys.argv[1]
vers=re.findall(r"'''Version ("+re.escape(pref)+r"\d+)\.0'''",c)
if len(sys.argv)>2: vers=sys.argv[2:]
for v in sorted(set(vers),key=lambda s:[int(x) for x in s.split('.')]):
  i=c.find("'''Version "+v+".0'''")
  t=re.search(r'\[\[([^\]]+)\]\]',c[i:]).group(1) if i>=0 else "What's in Store for the "+v+".0 Update (Notification)"
  p=wiki(t)
  if 'revisions' not in p: print('=====',v,t,'MISSING PAGE');continue
  s=p['revisions'][0]['slots']['main']['content']
  date=re.findall(r'\{\{News\|date=([^|}T]*)',s)
  print('=====',v,date,t)
  secs=[h for h in re.findall(r'NewsTitle\|(■[^}]*)',s) if re.search(r'(?i)weapon|refin',h)]
  new,ref=[],[]
  for h in secs:
    a=s.find(h);b=s.find('{{NewsTitle|■',a+10);sec=s[a:b if b>0 else None]
    k=sec.find('special effects')
    if 'character-specific' in sec:
      x=sec.find('character-specific');y=sec.find('・',x);new+=[re.sub(r' \(weapon\)$','',a) for a in re.findall(r'(?:\}\}|\]\])\s*\[\[([^\]|]+)',sec[x:y])]
    if k>0: ref+=[re.sub(r' \(weapon\)$','',a) for a in re.findall(r'(?:\}\}|\]\])\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\]',sec[k:])]
  ref=[r for r in ref if r not in ('Weapon Refinery','Book I, Chapter 13','The Rite of Blades')]
  print(' NEW:',new);print(' REFINE:',ref)
  for kind,names in (('new',new),('ref',ref)):
    for n in names:
      xs=[x for x in skills if x['name']==n]
      if not xs: print('   MISSING',n)
      for x in xs:
        if kind=='ref' and not x.get('base_id'): continue
        print('  ',x['id'],'|',n,'| refine' if x.get('base_id') else '| base',x.get('addition_date'),x.get('release_date'),x.get('release_date_verified'),x.get('version'))
        if (x.get('addition_date'),x.get('release_date'),x.get('version'))!=(date[0] if date else None,)*2+(v,): print('   MISMATCH',x['id'],n)
