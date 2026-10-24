# Meta Builder: project notes

Everything needed to pick this project back up. Last updated October 23, 2026.

## Links

- **Website (public):** https://itsmrchickenss.github.io/meta-builder/ (GitHub Pages, deploys automatically from `main`, root folder)
- **This repo (public, MIT):** https://github.com/itsmrchickenss/meta-builder
- **Older copy:** private repo `itsmrchickenss/Projects`, folder `deepwoken-shrine-planner/` (kept in sync so far; the website repo is now the main one)
- **Claude artifact (private to the owner):** https://claude.ai/artifact/BoupUctZcdQwYCUpkDoyFn
- Share links made in the tool always point at the website: `https://itsmrchickenss.github.io/meta-builder/#dw1…`

## How to change the site

1. Edit `src/template.html` (all HTML, CSS and JavaScript live in this one file).
2. Run `python3 src/build.py`. It fills the `@@PLACEHOLDERS@@` with `src/data/*.txt`, wraps the page in `src/head.html`, and writes `index.html` (served by Pages) and `dist/meta-builder.html` (the bare page for the Claude artifact; `dist/` is git-ignored).
3. Run `node tests/core-test.js`. It optimizes every preset; any `FAIL` line means a broken build.
4. Commit and push to `main`. Pages updates in a minute or two.

Never edit `index.html` by hand; it is overwritten by the build.

## Files

| Path | What it is |
|---|---|
| `src/template.html` | The whole app. Sections are marked `// ================= name =================`. Everything above `// ================= UI =================` is game logic with no DOM use, which is what `tests/core-test.js` loads. |
| `src/head.html` | `<head>` for the website: title, description, link-preview tags, icon. |
| `src/build.py` | Build script (see above). |
| `src/data/part1.txt`, `part2.txt` | `#T` talents, `#M` mantras, `#W` weapons, `#O` oath mantra slots (placeholder `@@DATA@@`). |
| `src/data/builds.txt` | 60 reference builds for recommendations (`@@BUILDS@@`). |
| `src/data/pop.txt` | Talent popularity in % across 802 top builds (`@@POP@@`). |
| `src/data/wdmg.txt` | Weapon damage, penetration, scaling (`@@WDMG@@`). |
| `src/data/mdmg.txt` | Mantra damage per level 1–5 and scaling (`@@MDMG@@`). |
| `src/data/syn.txt` | Talent synergy pairs (`@@SYN@@`). |
| `src/data/gear.txt` | `#E` equipment, `#O` outfits, `#OT` outfit talents, `#TD` gear-talent descriptions (`@@GEAR@@`). |
| `src/data/tdesc.txt` | Descriptions for every talent (`@@TDESC@@`). |
| `tests/core-test.js` | Node check of the core logic. |

### Data line formats

- Talent: `name|category|rarity+countFlag|stats|o=alts|a=combined|t=talents|m=mantras|x=exclusive|w=weapon|q`. Rarity letter C/R/A/Q/O; a `0` after it means it doesn't count toward the talent total. Stats look like `STR25 AGL20`, `PWR` is Power.
- Mantra: `name|attunement|category+stars+type|requirements…` (type N = normal and costs 2 talent slots; oath, monster and event mantras are free).
- Equipment: `name|type(H/A/L/T/F/E/R)|hp|physFlat|eleFlat|physPct|elePct|hpPct|pips(U1R1…)|req|set|flag|talents;…`
- Outfit: `name|phys%|ele%|durability|req|`
- Synergy: `A|B|kind` where kind is `c` (curated, weight 3), `m` (one description names the other, weight 2) or a lift number from build data.
- Stat codes: STR FTD AGL INT WLL CHA, weapons HVY MED LHT, attunements FLM ICE LTN WND SDW IRN BLD.

## Where the data came from

All game data is a snapshot of **deepwoken.co** (October 2026). The fandom wiki blocks automated fetches. deepwoken.co's API worked from the Claude desktop app's built-in browser, run as JavaScript on deepwoken.co; the cloud shell can't reach it.

- `/api/proxy/get?type=all`: talents (with descriptions), mantras, weapons, outfits, enchants
- `/api/proxy/db/equipment`, `/api/proxy/db/enchantments`, `/api/proxy/db/oaths`
- `/api/proxy/builds?sort=top&limit=50&page=N&tags=PvE%3A%20Boss` (tag filters: `PvE: Boss`, `PvP: Chime`, `PvP: Gank`, `PvE: Mob`, oath names, attunements…), `/api/proxy/builds/tags`, `/api/proxy/builds/<id>`
- deepwoken.co's builder JavaScript bundle was read to copy its Shrine of Order, Shrine of Mastery, damage and EHP formulas.

## Game rules the tool models

- **Budget:** 330 points. Power = `clamp(floor((points − 15) / 15), 0, 20)`. Each attunement after the first gets its first point free.
- **Talent cap:** 52 + (12 − normal mantras) × 2.
- **Shrine of Order** (deepwoken.co's algorithm): average every stat with at least 1 point; a non-attunement stat can't drop more than 25 (it gets pinned and the excess is shared among the rest); floor the results, hand out leftovers +1 to unpinned stats, refund the remainder. Talents you already own stay.
- **Shrine of Mastery:** remove up to 3 points in total, split between before and after the Order shrine. The points are refunded, and talents already taken stay.
- **Weapon (M1) damage:** base × (1 + 0.75 × Σ(stat × scaling) / 1000) × (1 + bonus) × (1 − (1 − pen) × 0.30 armor).
  - **Damage bonus:** talent bonuses add up; past +25% each extra % counts half, capped at +50%. Unique bonuses such as After Cut bypass this.
  - **Penetration:** weapon pen + STR/10 % + talents, capped at 50% (100% with Million Ton Piercer or Ether Overdrive). Cheap Shot multiplies it by 1.1.
- **Mantra damage:** level = clamp(1 + floor(attunement / 20), 1, 5). Damage = level damage × (1 + Σ scaling/10 × stat/100) × (1 + bonus) × 0.7.
- **Health:** 220 + Power × 4 + min(FTD, 50) × 0.5 + max(FTD − 50, 0) × 0.25, plus gear.
- **EHP:** health ÷ (1 − armor% × (1 − attacker pen)), with physical pen 35 and mantra pen 20. Stars add pips (1★ R, 2★ R R, 3★ R R L; Head/Arms/Legs up to 3★ and +1 HP per star). The pip values table is `PIPV` in the template.
- **Not modelled:** race stat bonuses, gear set bonuses, talent HP bonuses.

## How the optimizer works

- **Search:** it picks pre-shrine stats `P` by local search over requirement thresholds, starting from several points, including the stats currently on screen so re-optimizing never does worse. A talent is taken before the shrine if `P` already meets it, otherwise after.
- **Score:** free points + 2·(1 − prio)·damage% + 2·prio·talentValue/10.
  - **damage%** blends M1 and mantra damage using the "Damage from" slider.
  - **talentValue** sums the popularity of unpicked talents the stats unlock, plus 15 per synergy weight unit.
- **When you press Optimize**, in order:
  1. Drop talents your stat limits rule out.
  2. Enforce the talent cap (`trimToCap`).
  3. Search.
  4. If still over budget, drop the talents that free the most points for the least value (`trimToBudget`). Required talents are never dropped.
  5. Optionally spend leftovers on weapon and attunements.
- **Stat limits ("Keep these stats low"):** a limited stat gets no pre-shrine points (the shrine would average them up), its targets are clamped, and talents or oaths that need more are flagged. Combined requirements such as Soulbreaker's WLL+CHA 50 count too.
- **Manual mode** skips all of this; the user types every pre-shrine and final value.
- **Equipment optimizer:** it reaches the minimum health (default 500) first, then maximizes health × (1/(1 − physical resistance))^a, where a comes from the Health ↔ Physical armor slider. It never uses elemental pips and never picks Transfusion Ring.
- **Presets** are averages of deepwoken.co's top builds; Bossraid uses 92 heavy builds tagged PvE: Boss, Bossraid Mage 37 caster builds, Chime 199 builds tagged PvP: Chime. The preset questions lower floors 5 at a time until a new build fits 330 points.
- **AI build maker** is a keyword reader that runs in the browser (`aiParse`), not a language model. The "What you want" box uses `applyWish`.

## Saved state and share links

- **Browser storage:** `meta-builder-v1` holds the build and settings, `meta-builder-look` the theme.
- **Share code:** `dw1` + base64url of a JSON object with keys `v w t a s m n i q o p g r e x sn av cp`:
  - `w` weapon type, `t` weapon target, `a` attunements, `s` talents, `m` mantras, `n` pre/post overrides
  - `i` after-shrine floors, `q` pre-shrine floors, `o` oath, `p` weapon, `g` gear, `r` required, `e` enchant
  - `x` pins, `sn` saved pre/post snapshots, `av` avoided talents, `cp` stat limits
- `decodeBuild` validates every field. Keep old keys working when adding new ones so existing links don't break.

## Decisions and preferences so far

- **Name and layout:** the tool is "Meta Builder". The default theme is Abyss (dark teal and brass). Tabs follow the build order: Build → Required & avoid → Optimize → Summary → Armor.
- **Accessibility:** colorblind support is a set of themes (red‑green, blue‑yellow, high contrast), not a separate toggle. Help mode lives in Starting presets and in the preset questions.
- **Level dropdowns:** they start with "No stats" (0), then 1, 5, 10 … 100.
- **Talents:** they're grouped by the stat they need most. Synergies are grouped under the talent they pair with, and hovering any talent shows its description.
- **Equipment:** never use Transfusion Ring; aim for at least 500 HP; physical armor only.
- **Licensing:** MIT license, with a README note that this is an unofficial fan tool.
- **Commits:** commits made with Claude end with the `Co-Authored-By` / `Claude-Session` trailer.

## Ideas not done yet

- Race and aspect stat bonuses, gear set bonuses, and talent health bonuses.
- 17 outfits that grant talents are missing from the outfit list (Flame Worshipper Armor, Steel Plate, the Familiar Assassin's, Demon's and Occultist's sets, and others).
- On phones, hover cards don't appear; the Required tab's Browse talents list is the way to read descriptions there.
- Refreshing data means pulling from deepwoken.co again with the endpoints above and regenerating `src/data/*.txt` in the same formats.
