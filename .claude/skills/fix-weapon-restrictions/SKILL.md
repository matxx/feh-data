---
name: fix-weapon-restrictions
description: Find skills in data/skills.json whose weapon restrictions are missing ("weapons": null under "restrictions"), look up the correct canUseWeapon on the FEH fandom wiki, and fill them in. Use when asked to fix/fill/check weapon restrictions, "weapons": null, or after a data update leaves skills without weapon restrictions.
---

# Fill missing weapon restrictions

After a data update, some skills in `data/skills.json` can end up with `"weapons": null` in their
`restrictions`. The correct value comes from the skill's `canUseWeapon` on the FEH wiki.

## Mapping

| Wiki `canUseWeapon` | `restrictions.weapons` in skills.json | Example |
|---|---|---|
| `{{WeaponList\|All}}` | `{"none": true}` | Counter Savvy |
| `{{WeaponList\|exclude=Staff}}` | `{"can_not_use": ["Colorless Staff"]}` | Mirror Stance |

Anything else is out of scope: report it and don't guess. Only change `weapons`. Leave `moves` and
the other fields alone.

## Wiki lookup

- Use the API. Direct page fetches are blocked by Cloudflare:
  `https://feheroes.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&redirects=1&titles=<title>`
- The page title is the skill's **`fandom_id`** (URL-decoded, e.g. `S_D_Crux%3A_Con` → `S_D_Crux:_Con`),
  **not** its `name`. Names with `/` or a rank suffix (`Atk/Def Liberate`, `Squad Ace DH 1`) have no
  page. All ranks of a skill share one page (`Squad_Ace_DH`).

## Workflow

1. Run `python3 -I .claude/skills/fix-weapon-restrictions/fix.py` from the repo root. It lists every
   skill with `"weapons": null`, its wiki page, the raw `canUseWeapon` and the mapped value. It
   doesn't write anything yet.
2. Check `UNKNOWN` lines (missing page, or a value outside the mapping). Look at the raw page and ask
   the user before handling them.
3. Run it again with `--apply`. It writes only the mapped skills, following `.editorconfig`
   (2 spaces, final newline, non-ASCII kept as-is).
4. Check `git diff --stat`. Each fixed skill should add about 3 lines and remove 1. A whole-file diff
   means a formatting problem. Then confirm `grep -c '"weapons": null' data/skills.json` is 0, or
   that what's left is only the reported `UNKNOWN` skills.
5. Report a table of the skills fixed (name, wiki page, value) and anything skipped. Don't commit
   unless asked. Commit style: `fix: add weapon restrictions for <skills>`.
