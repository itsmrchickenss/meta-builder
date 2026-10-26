# Meta Builder: project notes

Everything needed to pick this project back up. Last updated October 26, 2026 (v0.29).
The spreadsheet `docs/Meta Builder formulas.xlsx` has every formula (with a live Calculator) and every talent, mantra, weapon and item.

## Starting a new chat

The handoff page (a private Claude artifact) has this same information for a chat that isn't attached to the repo: https://claude.ai/artifact/YBSQSo98nCQC84rkSZVZE3 (regenerate with `python3 tools/handoff.py` and publish `dist/handoff.html` to it only when the owner asks). In a new chat, attach the repo `itsmrchickenss/meta-builder` (or paste the handoff link) and say what to change. Claude reads `CLAUDE.md` and this file first.

## Links

- **Website (public):** https://itsmrchickenss.github.io/meta-builder/ (GitHub Pages, deploys from `main`, root folder, 1–2 minutes after a push)
- **Repo (public, MIT):** https://github.com/itsmrchickenss/meta-builder
- **Claude artifact (private to the owner):** https://claude.ai/artifact/BoupUctZcdQwYCUpkDoyFn. Publish `dist/meta-builder.html` to it with capabilities `{downloads: true, sample: {images: true}}` (sample = Claude reads screenshots).
- **Older copy:** private repo `itsmrchickenss/Projects`, `deepwoken-shrine-planner/`. Only update it if the owner asks.
- Share links always point at the website: `https://itsmrchickenss.github.io/meta-builder/#dw1…`
- Bug reports / suggestions are emailed to the owner by Web3Forms (key `BUG_KEY` in the template, registered to the GitHub Pages URL).

## How to change the site

1. Edit `src/template.html` (all HTML, CSS and JS) or `src/data/*.txt`. Never edit `index.html`.
2. `python3 src/build.py` → writes `index.html` (website) and `dist/meta-builder.html` (artifact).
3. `node tests/core-test.js` → every preset, with and without 6 mantras, must say `ok` (fits budget and talent cap).
4. Browser checks (Playwright + Chromium are preinstalled): `python3 tests/browser/layout.py` (no sideways scroll at 1280/390, no console errors) plus the others in `tests/browser/` that touch what changed.
5. Add the new version at the top of `src/data/versions.txt` (it sets the badge and the in-app Version history), commit with the `Co-Authored-By` / `Claude-Session` trailers, push, publish the artifact.
6. If formulas or data changed: `node tools/formulas/dump.js && python3 tools/formulas/build.py`, then recalc the workbook (xlsx skill `recalc.py`), commit `docs/Meta Builder formulas.xlsx`.

## Version

Pre-release numbering is **v0.x** (v0.29 now). The owner sets **v1.0 at release**. Every update the owner makes is a new version: +0.01, a new entry at the top of `src/data/versions.txt` (`## vX | YYYY-MM-DD`, then `- change` lines in plain words for players), pushed to this repo (owner's request, October 26, 2026). The build puts the newest version on the badge next to the title; clicking it opens the Version history popup. The handoff page is not refreshed per version, only when the owner asks. (Earlier commits used v1.12–v1.23 before the owner renamed it; v0.23 followed v1.23.)

## Owner's rules and preferences (keep these)

**Shrine and stats**
- The Shrine of Order can only be used at **Power 8+** (135 points before it).
- **Pre-shrine is the peak:** never raise an attribute before the shrine and then raise it again after. Either about 1 before and the rest after, or high before and the shrine brings it down. Fortitude is **never the same** before and after (no "50 → 50"). Weapon and attunement stats may be re-raised (top builds do Ironsing 60 → 80).
- Never change Fortitude just because "favor health" is chosen for equipment.

**Presets**
- Presets are **starting stats only**: defining stat floors, oath, weapon type. No core talents, no auto-picked talents. Bossraid = FTD + WLL; Bossraid Mage = FTD + WLL + INT + 100 in an attunement of choice.

**AI build maker**
- Keep the oath the person names; otherwise use the starting point's default.
- A mage gets **no attunement unless asked**.
- Attunements: one → 80 (mage 100); two → 80/40, or 80/80 when the points allow (mage or "dual" → 80/80); three+ → one main at 80 (mage 100), the rest 40.
- A talent path that needs other attunements (steam = Flamecharm + Frostdraw): those secondary attunements go **only as high as the requested talents need** (e.g. "lightning steam path" → Thundercall 80, Flamecharm 30, Frostdraw 30). The main attunement is the first one named that the path doesn't need. Numbers the person types always win ("flame 50").
- Silentheart makes attunement points useless: never auto-pick it for attunement or mage builds; warn when a weapon (Hero's Blade) still needs attunement.
- A new build must not inherit anything from the previous one (required talents, equipment, enchant, caps).
- Saintsworn requirements, talent paths (steam = Vaporborne…), gank = mobile, semi-tanky are understood.
- **Follow-up questions** (`aiQuestions` / `renderAiQs` / `aiAnswersText`): after "Make my build", the dialog asks only what the description left open. Attunement focus when 2+ attunements have no typed numbers: main attunement select + options (2: "80 / 80", "80 / 40", "80 / just what the path needs" when a path needs the other, "Other" with number boxes; 3+: "80 / 40 / 40", "80 / 80 / 40", "all 80", "just what the path needs", "Other"; mage main = 100). Also weapon type (if none named), oath (if none named; "best fit" default) and how tanky (glass cannon / balanced / semi tanky / tanky). Answers are appended to the description as words ("thundercall 80, flamecharm 30…") and `aiParse` runs again. Skip uses the defaults; Back returns to the text.
- After an AI build, the Adjustments box takes plain-language changes and re-optimizes.

**Talents**
- Prioritize talents tied to your **weapon type and attunements** (`kitOf`).
- Talent cap = 52 + (12 − normal mantras) × 2. Adding past it shows "Max talent limit reached!" with an opt-in box to allow going over.
- Show which talents are taken **before the shrine** (PRE badge) and count pre-shrine stats as reachable in suggestions.

**Equipment**
- Default targets: **500 HP and 50% physical armor**, then the Health ↔ Armor slider. **Never elemental armor** pips. Never Transfusion Ring.

**Optimizer**
- Optimize must always end within the budget (drop talents, then lower floors, then rebuild picks), and the damage ↔ talent options slider must visibly change the result.

**Layout and wording**
- Tabs: ⇩ Import · 1 Stats · 2 Talents & mantras · 3 Summary · 4 Armor · ! Report bug/suggestions.
- Stats tab: Import is its own tab; stats table shows Before shrine → Shrine leaves → After shrine (Final, editable). Weapon, Attunements, Traits, Oath on the right.
- Talents tab: picker and Required on the left; Browse talents and Avoided talents at the top of the right column.
- Plain wording ("X points left", not "free"). The AI builder says "(the more specific you are the better!)".
- Keep the sticky top bar compact (it once covered the Talents filters).

**Data and import**
- deepwoken.co blocks other sites from reading its builds (403 for direct loads and other origins). A pasted link can't import. **Don't spoof requests or use proxies to get around it.** The supported path is the bookmark/console snippet (`DWCO_SNIP`): it runs on the deepwoken.co build page, fetches `/api/proxy/builds/<id>` there and opens the website with `#dwco=<json>`, which imports on load.
- Game data is credited to deepwoken.co.

## Files

| Path | What it is |
|---|---|
| `src/template.html` | The whole app. Sections marked `// ================= name =================`. Everything above `// ================= UI =================` is DOM-free game logic (what `tests/core-test.js` and `tools/formulas/dump.js` load). |
| `src/head.html` | `<head>` for the website. |
| `src/build.py` | Fills `@@PLACEHOLDERS@@` from `src/data/*.txt`. |
| `src/data/part1.txt`, `part2.txt` | `#T` talents, `#M` mantras, `#W` weapons, `#O` oath mantra slots. |
| `src/data/builds.txt` | Reference builds (REF) for recommendations. |
| `src/data/pop.txt` | Talent popularity % across 802 top builds. |
| `src/data/cond.txt` | Take rate given stats: `name:k/m`, k of the m top-500 builds whose stats allow it take it. |
| `src/data/wdmg.txt`, `mdmg.txt` | Weapon damage/PEN/scaling; mantra damage per level and scaling. |
| `src/data/syn.txt` | Synergy pairs (`A|B|kind`: c = curated weight 3, m = description mention weight 2, or a lift number). |
| `src/data/gear.txt` | `#E` equipment, `#O` outfits (incl. non-master outfits with talents), `#OT`, `#TD`. |
| `src/data/tdesc.txt` | Talent descriptions. |
| `tests/core-test.js` | Node check: every preset optimizes within budget and cap, with and without mantras. |
| `tests/browser/*.py` | Playwright checks: layout, ai_paths, ai_questions, stress_optimize (random over-budget builds), presets_import, ai_maker, traits, screenshot_parse, talents_tab, adjustments, talent_cap, bug_report. |
| `tests/fixtures/dwco-build.json` | A real deepwoken.co build (with traits) for import tests. |
| `tools/formulas/` | `dump.js` (exports data from index.html) + `build.py` (writes the workbook). |
| `docs/Meta Builder formulas.xlsx` | The formulas workbook. |

Data line formats: talent `name|category|rarity(+0 = not counted)|stats|o=alts|a=combined|t=talents|m=mantras|x=exclusive|w=weapon|q`; mantra `name|attunement|category+stars+type|req…` (type N = normal, costs 2 talent slots); equipment `name|slot|hp|physFlat|eleFlat|phys%|ele%|hp%|pips|req|set|flag|talents`; outfit `name|phys%|ele%|durability|req|`.

## Game rules and formulas (full detail in the workbook's Formulas sheet)

- **Budget** 330. Power = clamp(floor((points − 15)/15), 0, 20). Attunements after the first get their first point free. Points used = pre − shrine refund + added after − free attunement points − Mastery refunds.
- **Shrine of Order** (deepwoken.co algorithm, `shrine()`): average the invested stats; attributes can't end more than 25 below pre (pinned, excess shared); floor; hand out leftovers; refund the rest. Needs Power 8.
- **Shrine of Mastery:** up to 3 points refunded before or after the Order shrine.
- **Requirements:** alternatives from stats, one-of groups, combined sums; prerequisites merged (`chainAlts`); cost = sum of shortfalls; taken pre-shrine if every alternative is plain minimums and pre stats meet it. Silentheart: weapon reqs −25.
- **Weapon hit:** scaled = base × (1 + 0.75 × Σ(coef × stat) × (1 + 0.065 × Proficiency)/1000); bonus = talents (+2.5% Soulbreaker), full to 25%, half past, max 50%, unique outside; PEN = weapon + STR/10 % + talents + enchant + 2.5% × Proficiency, cap 50% (100% if uncapped); hit = scaled × (1 + bonus) × enchant × (1 − (1 − PEN) × 0.3).
- **Mantra hit:** level = clamp(1 + floor(att/20), 1, 5); hit = lv × (1 + Σ coef/10 × stat/100 × (1 + 0.065 × Songchant)) × (1 + bonus) × (1 − (1 − min(0.5, 0.025 × Songchant)) × 0.3).
- **Health:** 220 + 4 × 20 + 0.5 × min(FTD, 50) + 0.25 × max(FTD − 50, 0) + 10 × Vitality + gear. Resistance = min(0.95, armor% × (1 − pen)), pen 35 physical / 20 elemental. EHP = hp/(1 − res).
- **Traits:** separate 12-point pool, max 6 each. Vitality +10 HP; Erudition +30 ether, +5 tempo, +5% tempo gain (shown only); Proficiency ×(1+6.5%) weapon scaling, +2.5% weapon PEN; Songchant same for mantras (oath/monster mantras +2% dmg, shown only). Source: deepwoken.fandom.com/wiki/Traits.
- **Not modelled:** race bonuses, gear set bonuses, talent HP bonuses, ether use.

## How the optimizer works

- **Score:** (330 − used) + 2(1 − slider) × damage% + 2 × slider × talent options/10; penalties 20/pt over a stat limit or breaking the pre-shrine rule.
- **Optimize** (`optimizeAll`): drop limit-blocked talents → trim to cap (`trimToCap`) → search (`compute`) → `trimToBudget` → if required + floors alone are over, `easeFloors` (never values set in Adjustments, `S.keep`) → `rebuildToBudget` → `sliderRebalance` (damage end raises weapon/attunements toward 100 paid by low-value non-damage talents; talent end lowers them and fills with popular/synergy talents; 35–65 does nothing) → optional leftover spend (retries with fewer points).
- **Talent value** (`talentVal`): 90 × kit + (1 + popularity + 15 × synergy)(0.4 + 1.2 × slider) + 100 × (damage + PEN)(0.2 + 3.6 × (1 − slider)).
- **Auto-pick** fills open slots with talents that already fit, best value per slot (prerequisites count as slots).
- **Recommendations:** synergies first (10 + weight), then take rate given stats, +0.8 × kit.
- **Equipment optimizer:** meet min HP and min physical armor, then hp × (1/(1−res))^a.
- **AI build maker** (`aiParse`) is a keyword reader that runs in the browser, not a language model. Wishes: `applyWish`; Adjustments: `applyAdjust`.

## Features (where to find them)

- **Import tab:** paste box (Meta Builder link, Deepwoken in-game text, deepwoken.co JSON), deepwoken.co bookmark, Build from a screenshot (Claude reads it in the artifact; Tesseract.js 5.1.1 from jsdelivr on the website) → Likely talents → Talents you see in the video (become required) → Load.
- **Stats tab:** presets + AI build maker + My presets (localStorage), stats table (pins, editable finals = floor + limit), Adjustments (after AI builds), optimizer settings and sliders, weapon, attunements, traits, oath, "What you want".
- **Talents & mantras tab:** picker (filters, by stat/category, search over names and descriptions, PRE badges, kit labels, max-talent warning), required, browse, avoided, your talents (pre/post), mantras, true combos.
- **Summary:** damage, weapon & enchant, compare weapons, mantra damage, levelling steps, recommended talents (Take), share & export.
- **Armor:** equipment search, slots and pips, health/EHP, optimize equipment.
- **Report bug/suggestions:** emailed to the owner via Web3Forms; the artifact can't send outside (points to the website).
- **Help mode:** tips with Take / Spend / Optimize buttons.

## Saved state and share links

- localStorage `meta-builder-v1` (build + settings), `meta-builder-look` (theme), `meta-builder-presets`, `meta-builder-combos`.
- Share code: `dw1` + base64url JSON, keys `v w t a s m n i q o p g r e x sn av cp tr` (tr = traits). `decodeBuild` validates every field; keep old keys working.
- deepwoken.co JSON: `stats.meta.{Oath,Outfit}`, `stats.traits`, `attributes|preShrine|postShrine.{base,weapon,attunement}`, `talents` (some with `[HVY]`-style tags), `mantras`, `weapons`.
- Our Deepwoken-text export adds `== WEAPON ==`, `== OUTFIT ==`, `== PRE-SHRINE ==`, `== TRAITS ==` sections, read back on import.

## Where the data came from

deepwoken.co snapshot (October 2026), read in the Claude desktop app's built-in browser as JavaScript on a deepwoken.co page (same-origin fetches work there): `/api/proxy/get?type=all`, `/api/proxy/db/equipment|enchantments|oaths`, `/api/proxy/builds?sort=top&limit=50&page=N[&tags=…]`, `/api/proxy/builds/<id>`. Its builder bundle supplied the shrine, damage and EHP formulas. The fandom wiki blocks automated fetches except through WebFetch.

## Presets (stats only)

Clean Slate · Bossraid (FTD 75 + WLL 50 pre) · Bossraid Mage (FTD 75 + WLL 50 + INT 40, attunement 100) · Elder / Enmity (Bladeharper Ironsing: CHA 40 pre, INT 90 + STR 25 post, Ironsing 80, Shadowcast 20, Shattered Katana, Prophet's Cloak; real builds hit INT 100 but shrine below Power 8) · Brick Wall Dawnwalker (FTD/WLL 100 → 75, Frostdraw 80 + Flamecharm 40, steam talents locked, Gran Sudaruska) · Chime · High Charisma · High Strength · Jetstriker Agility · Willpower Tank · High Intelligence · Reinforced Armor · Mage · No Willpower.

## Ideas not done yet

- Race and aspect stat bonuses, gear set bonuses, talent health bonuses, ether modelling.
- Hover cards don't show on phones (Browse talents shows descriptions).
- Refreshing data: pull again from deepwoken.co with the endpoints above (from a deepwoken.co page) and regenerate `src/data/*.txt` in the same formats.

## Version history

The full list lives in `src/data/versions.txt` (shown in the app when you click the version). It is the only copy; don't repeat it here.
