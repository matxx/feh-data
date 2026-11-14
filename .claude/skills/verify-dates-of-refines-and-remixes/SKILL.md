---
name: verify-dates-of-refines-and-remixes
description: Verify or fix the release dates of weapon refines, new character-specific weapons and remixed skills (II/+ skills added to Legendary/Mythic Heroes) in data/skills.json for one or more FEH game versions, using the official "What's in Store for the X.Y.0 Update" notifications, and mark them release_date_verified "manually". Use when asked to check/verify/fix refine dates, remix dates, weapon release dates, or a version like "do 11.0".
---

# Verify refine dates against update notifications

Each FEH version update ("What's in Store for the X.Y.0 Update") lists the weapons that got a refine,
the new character-specific weapons and the skills remixed for Legendary/Mythic Heroes. Those skills
must carry the update's date and version in `data/skills.json`, marked as manually verified.

## What "correct" means

- Dates mean **when the skill was released in-game**, not when the hero first appeared.
- For every skill found on the update page, set:
  - `release_date` = the news date (date part only, `YYYY-MM-DD`)
  - `version` = `major.minor` (e.g. `"10.6"`, never `"10.6.0"`)
  - `release_date_verified` = `"manually"`, placed right after `release_date`. Do this **even if the
    date was already correct**, and even if the field was missing or was `bot_create`/`bot_update`:
    manual verification takes precedence, and unmarked entries can be reset by the data pipeline.
- **Refines of existing weapons**: update only the refined entry (the one with `base_id` and
  `refine_kind`), never the base weapon.
- **New character-specific weapons** ("can learn these new character-specific weapon skills"): update
  the base entry **and** its refined entry. A common error is the base carrying the hero's original
  release date (e.g. 2017).
- **Remixed skills** (section "New skills have been added for some Legendary Heroes" / "for a Legendary
  and Mythic Hero", "New skills for Legendary Heroes" in 5.x): only the skills flagged with the
  `News icon new skill.png` icon are new (e.g. Ice Mirror II, Sweet Dreams+, Atrocity II). The other
  skills listed for the hero already existed: leave them. Update only the remixed entry (the `・承` "II" or
  `・神` "+" one), never the skill it upgrades. The data pipeline tends to give remixes the date of the
  skill they upgrade (e.g. Ice Mirror II dated 2.0 instead of 5.2), years too early.
- **Other skills newly added by the update** (e.g. 2.0's staff `+` weapons, `+` assists and
  evolution-only weapons) also get the news date and version.
- The `refine_date` and `addition_date` fields no longer exist; never add them.

## Do NOT touch

- **Evolutions** (`X → Y` lines, e.g. "Mystletainn → Dark Mystletainn"). These aren't refines, and
  skills.json has no evolution field.
- **Generic weapons whose refine came out with the weapon**: staff Wrathful `_神` / Dazzling `_幻`
  refines (Respite+, Aid+, Sunlight+, Bouquet Baton+…) and weapons like Poleaxe+. They never appear in
  update news.
- **The non-flagged skills of a remixed hero** (e.g. Atk Res Hold in 7.11): they're inherited, not new.
- **Skills that aren't in the data**, such as My Summoner's Dire Breidablik (5.2): `MISSING` is expected.
- **Base weapons released with a hero** (e.g. Blade of Shadow, Wind Parthia): only their refines are
  in the news.
- **Dated in the wrong version**: if a skill's data version doesn't match the page, it may belong to
  another version. Check before moving it.
- Before 2.0 there was no Weapon Refinery, and the 1.x notes name no skills.

## Sources

1. **Wiki (up to 10.5)**: fetch wikitext through the API. Direct page fetches and `action=raw` are
   blocked by Cloudflare:
   `https://feheroes.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&titles=<title>`
   - Title: `What's In Store for the X.Y.0 Update (Notification)`. Some use a lowercase "in"
     (2.0–2.6, 2.8, 3.0, 9.9+, 10.x); 1.2 is "What's New in Version 1.2.0". When unsure, look at the
     wiki page `List_of_version_updates` (it stops at 10.0).
   - Date: `{{News|date=YYYY-MM-DDT…}}`. Keep the date part only.
   - Weapon section: the `{{NewsTitle|■ …}}` header mentioning weapons/refine. Weapon links may be
     piped (`[[Ginnungagap (weapon)|Ginnungagap]]`). 2.x pages use templates instead
     (`{{Wt|Name}}`, `{{NewsWeapon|Name|Red Sword}}`, `{{NewsWikilink|Name}}`) and say "unit-specific"
     or "character-specific"; refines start at "special effects" or "can now be strengthened/upgraded".
   - Remix lines: `[[File:News icon new skill.png…]]{{NewsIcon|Atrocity II.png}}[[Atrocity|Atrocity II]]`
     (5.5 flags them with `{{NewsIcon|Icon new.png}}` instead).
     Some pages (5.7, 5.11) link the base skill unpiped (`[[Laws of Sacae]]`); only the icon name keeps
     the " II"/"+".
2. **Official site (10.6 and later, and to cross-check)**: `https://fire-emblem-heroes.com/en/topics/`
   is filled by JavaScript from:
   - `https://fire-emblem-heroes.com/en/include/topics_title.html`: titles with dates (`M/D/YYYY`)
   - `https://fire-emblem-heroes.com/en/include/topics_detail.html`: full text. Search for
     `What's in Store for the X.Y.0 Update` and read the `■ … weapon … refine …` section and the
     `■ New skills have been added for …` section.

## Workflow

1. Run `python3 -I .claude/skills/verify-refine-dates/extract.py <version-prefix> [versions…]` (e.g.
   `10.` or `10. 10.1 10.2`). It prints, per version, the news date, the new weapons, the refines,
   the remixed skills (`REMIX`, from the "new skill" icon, piped links resolved to the displayed name,
   " II"/"+" taken from the icon when the link drops it), every matching skill entry with its current
   values, and `MISMATCH` lines. 2.0 also gets `OTHER`: the second column of its "prereq → added skill"
   tables (evolution-only weapons, staff `+`, assist `+`), checked on the base entry only. Some of those
   evolution targets were already wielded by a hero before 2.0 (Divine Tyrfing, Blazing Durandal, Dark
   Aura, Dark Excalibur, Divine Naga): their `MISMATCH` is expected, leave them. Known extraction gap:
   2.3 names Wind's Brand in plain text only, so its base isn't listed (check it by hand). It covers
   versions available on the wiki. For official-site versions, read the section and build the lists by
   hand.
2. Cross-check both ways:
   - every weapon on the page has a refined entry in the data;
   - every refined entry, and every `・承`/`・神` entry, whose `version` is in the range appears on a
     page. Anything left over is usually a generic staff (leave it), or an extraction miss (check the
     raw page). Exception: a `・承`/`・神` entry left over in an *earlier* range (e.g. 2.x) is not out of
     scope. It is a remix dated like the skill it upgrades, and its real update is later (Radiant
     Aether II is dated 2.1 but came in 5.2). Run the extractor on the later versions to find it.
3. Apply with `python3 .claude/skills/verify-refine-dates/fix.py <date> <version> <id> [<id>…]`. It
   sets the date, version and `"manually"`, prints the per-entry diff, and writes the file following
   `.editorconfig` (2 spaces, final newline).
4. Check `git diff --stat`. Only the intended lines should change. A whole-file diff means a formatting
   problem.
5. Report per version: what changed (with old values), what was only marked `"manually"`, and anything
   skipped or ambiguous (evolutions, dates that differ by a day, etc.). Don't commit unless asked.
