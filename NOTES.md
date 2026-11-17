# Meta Builder: project notes

Everything needed to pick this project back up. Last updated November 17, 2026 (v0.35).
The spreadsheet `docs/Meta Builder formulas.xlsx` has every formula (with a live Calculator) and every talent, mantra, weapon and item.

## Starting a new chat

The handoff page (a private Claude artifact) has this same information for a chat that isn't attached to the repo: https://claude.ai/artifact/YBSQSo98nCQC84rkSZVZE3 (regenerate with `python3 tools/handoff.py` and publish `dist/handoff.html` to it every 10 versions — v0.30, v0.40… — or when the owner asks). In a new chat, attach the repo `itsmrchickenss/meta-builder` (or paste the handoff link) and say what to change. Claude reads `CLAUDE.md` and this file first.

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

Pre-release numbering is **v0.x** (v0.35 released November 17, 2026). The owner sets **v1.0 at release**. Each release is a new version (+0.01) with an entry at the top of `src/data/versions.txt` (`## vX | YYYY-MM-DD`, then `- change` lines in plain words for players). **Releases happen only when the owner says so** (October 26, 2026: fewer updates, higher quality): work goes on the `next` branch under a `## vX | unreleased` entry, and is merged into `main` (which updates the website, the artifact and the desktop downloads) only on the owner's word. The build puts the newest version on the badge next to the title; clicking it opens the Version history popup. The handoff page is refreshed automatically every 10 versions (v0.30, v0.40, v0.50…) and otherwise only when the owner asks. (Earlier commits used v1.12–v1.23 before the owner renamed it; v0.23 followed v1.23.)

## Desktop app and web server (v0.32+)

- `app/` holds a Node.js web server (`server.js`, no dependencies; `npm start`, `npm test`, `/healthz`, `/version`, Dockerfile) and an Electron desktop app (`electron/main.js`). Both show the built page. The owner chose JavaScript so the same code can be hosted on a server later.
- The desktop app serves `www/` on a private `app://meta-builder/` address so localStorage persists; outside links open in the normal browser; share links point to the GitHub Pages site (`shareBase()` treats non-http pages that way). A hosted server's share links use its own address.
- `.github/workflows/app.yml`: on every push to `main` touching `src/`, `app/` or the workflow, it builds the page, runs `core-test.js` and `app/test-server.js`, builds the Mac universal `.dmg` (ad-hoc signed, not notarized) and Windows `Setup.exe` + `Portable.exe` (unsigned), and publishes a GitHub Release tagged with the version from `versions.txt`. Electron can't be downloaded in Claude's cloud workspace (GitHub release downloads are blocked there), so desktop builds only happen in Actions.
- **Auto-update (v0.33):** `app/electron/updater.js` (plain Node, tested by `app/test-updater.js`). Page layer: on launch (after 8 s) and every 6 hours, if "Update Automatically" is on (Help menu; saved in the app's `settings.json`), the app downloads `https://itsmrchickenss.github.io/meta-builder/index.html`, checks it (≥200 KB, Meta Builder title, complete `</html>`, version badge, game data), and if its version is newer saves it to `<userData>/www/index.html` (temp file + rename). The newer of the bundled and downloaded page is served; installing a newer app deletes the older download. Then it asks "Reload now / Later". App layer: each page carries `<script type="text/plain" id="dwshell">N</script>` (from `shellVersion` in `app/package.json`); if N is above the running app's, the page isn't installed and the person is pointed to the Releases download. Bump `shellVersion` only when `app/electron/` changes in a way pages need. A real installer auto-update isn't used: on Mac it requires a paid Apple Developer ID certificate. Since the website is `main`, apps only update when the owner releases.
- `app/www/`, `app/node_modules/` and `app/release/` are git-ignored; the server falls back to the repo's `index.html` on a fresh clone.

## Owner's rules and preferences (keep these)

**Shrine and stats**
- The Shrine of Order can only be used at **Power 8+** (135 points before it).
- **Pre-shrine is the peak:** never raise an attribute before the shrine and then raise it again after. Either about 1 before and the rest after, or high before and the shrine brings it down. Fortitude is **never the same** before and after (no "50 → 50"). Weapon and attunement stats may be re-raised (top builds do Ironsing 60 → 80).
- Never change Fortitude just because "favor health" is chosen for equipment.

**Presets**
- Presets are **starting stats only**: defining stat floors and weapon type. No core talents, no auto-picked talents (loading a preset, AI build or import never runs the slider's talent fill: `optimizeAll({noSpend})` → `sliderRebalance(res,noFill)`). **Oaths only where the preset is built around one** (owner, November 17, 2026): Jetstriker Agility (Jetstriker), Elder / Enmity (Bladeharper), Bossraid Mage (Saintsworn, so it has 15 in the other four elements), Silentheart, Diluvian (Dawnwalker); every other preset is `oath:'None'` and says "oath up to you". Each preset's stats must meet its oath; `tests/core-test.js` checks it. The AI build maker treats a starting point with no oath as "best fit". **Diluvian** is the one preset with talents: Dawnwalker, Brick Wall locked, FTD 100 + WLL 100 before the shrine (75 after), and every talent those two stats unlock on their own (`statOnlyTalents`, computed from the data); weapon and attunements are left to the person. Bossraid = FTD + WLL; Bossraid Mage = FTD + WLL + INT + 100 in an attunement of choice. Willpower Tank was removed (Diluvian covers it). **Hero's Blade** (owner, November 17, 2026): a build with no weapon stats always gets the Hero's Blade of its strongest element (`autoHeroBlade`, called from `renderInputs`, `run`, `optCore`) unless the person picked a weapon, cleared it (`S.noAutoW`) or imported a build without one; `S.weaponAuto` marks our pick (share keys `wa`, `nw`). Ironsing/Bloodrend-only mages get none (there is no Hero's Blade for them). **Weapons** (owner, November 17, 2026): every preset with a weapon starts at 80 in a weapon of the person's choice (Light / Medium / Heavy buttons at the top of the wizard, `data-wzw` / `wizSetW`); Elder / Enmity keeps Medium 90 (Shattered Katana); Bossraid Mage and Mage stay weapon-free. **Variations on every preset** (owner, November 17, 2026: "choices like Attunementless for every preset, variations of the build's shell, still letting people make their own version"): every preset but Clean Slate has `variants`; the first is the preset itself (`tests/core-test.js` checks it, so "Use preset as is" matches). A variant sets `pre`/`post` and may set `wtype`, `oath`, `ftd` (Fortitude-after options that fit; the wizard's Fortitude menu is the union, `wizFtdOpts`), `atts`, `wtarget`, `dsplit`. `wizVariant` fills the wizard from it (attunement rows, weapon level, weapon buttons and damage focus only when some variant of that preset sets them); everything stays editable. Chime's variants come from the featured Chime builds. `tests/core-test.js` runs every variant x Fortitude option x weapon type (one type when the variant has no weapon); `tests/browser/preset_variants.py` checks the form at 1280/390 and that each variant loads within budget. **Attunementless**: `variants` (splits AGL 100 + STR 40 → Jetstriker, STR 100 + AGL 65 → Starkindred, STR 100 + AGL 100 → oath by weapon type via `oathByW`) and `ftdOpts` 50 / 90 (90 only where it fits: not for 100/100); WLL 40 after; built from the owner's three examples in `featured.txt`. `tests/core-test.js` checks every split x Fortitude x weapon type, including that the oath fits.

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

**Buildmaking guide (owner's source, October 26, 2026):** Infekted, "Build Making Made Easy! - Deepwoken Buildmaking Guide" (https://www.youtube.com/watch?v=o9fxuIc64NM), plus the fandom wiki Attunements and Talents pages (the wiki blocks automated reads, so the owner pasted both pages on October 26, 2026). What it means here:
- **Key talents per stat** (`KEY_T`): STR Champion's Regalia, Going Nowhere, Bulldozer (25), Unwavering Resolve, Showstopper (40), Berserk (80), Collapsed Lung, Piercing Blow (100); FTD Exoskeleton (40), To The Finish (50), Reinforced Armor (90); AGL Risky Moves, Spine Cutter, Conditioned Runner (25), Ghost (40), Cheap Shot (65), Dustlunge, Pursuit (90), None Left Behind (100); INT Lightspeed Reflexes (20), Everchanging Aegis, Perfect Flash (25), Eureka (30), Overflowing Dam (40), Master Craftsman (45), Foolish Outburst, Water off a Duck's Back (50), Critical Engine, Ether Overdrive (90), Absolute Pitch (100); WLL Breathing Exercise (5), Old Habits Die Hard (20), Magical Resolve, Azure Flames (40), Emergency Reserves, Heretic's Sutra, Piercing Will (80), Shared Misery (85); CHA Charismatic Cast (25), Golden Tongue (40), Manipulator (60), Unnecessary Theatrics, Command: Live (75), Cult of Personality (90). You almost always take these when the stats reach them: +60 in `talentVal`, +70 in auto-pick, +1.2 in recommendations, and the AI build maker takes the ones its stats reach after optimizing. (Observation and Safety Dance are left out: they exclude Risky Moves, which Ghost needs.)
- **Archetypes in the AI build maker** (`AI_ARCH_ATT` and the play-style block in `aiParse`): armor shredding / high penetration = high Strength (90 before the shrine, Million Ton Piercer) + Ironsing + heavy weapon; gank = high Agility (65, Cheap Shot) + Ghost; stealth = Agility 40 for Ghost (take Ghost and the Butterfly talents before the shrine); block breaking = Strength 40; support = Charisma 55 (whole Charm Caster tree); alchemy = Intelligence 45. Attunement themes: burn/explosions = Flamecharm, freeze/slows = Frostdraw, stuns/lockdown/zoning = Thundercall, pressure = Galebreathe, ether drain/blind/anti-mage = Shadowcast, armor manipulation/shredding = Ironsing, lifesteal/bleed/blood poison = Bloodrend, fighting several people = Ironsing + Bloodrend. Words like these add the attunement after any named outright.
- **Talents that weaken below a stat** (wiki Talents page): they stay after the shrine but get weaker. `SCALE_MOD` changes the damage: Million Ton Piercer PEN × min(1, STR/90), Ether Overdrive PEN × min(1, INT/90), Cheap Shot PEN multiplier −0.11% per AGL below 65 (min 7.22%), Overflowing Dam −0.125% damage per INT below 40 (min 6.875%). `WEAK_T` lists the rest for the "Weaker after the shrine" warning (To The Finish 50 FTD, Reinforced Armor 90 FTD, Collapsed Lung 100 STR, Down to your Level 60 FTD, Twelve Steps Ahead 80 INT, Broken Ankles 70 STR, Unwavering Resolve 40 STR, Foolish Outburst 50 INT, Cornered Fool 85 CHA, Donation Drive 60 CHA, Alloyblood 100 IRN, Audacity 75 CHA + 25 STR, Defensive Reprisal / Dancing Guard / Knuckle Guard at their requirements). Mantra-level and Unbounded talents are removed below their requirement, but they don't use talent slots.
- Other wiki facts: mantra levels 1 / 20 / 40 / 60 / 80 = levels 1–5 (matches `mLevel`). Choosing no attunement at character creation gives 10 extra investment points (not modelled; the 330 budget comes from deepwoken.co).
- **Fortitude:** people rarely go over 50. Only plan 90 (Reinforced Armor) when the person asks for Reinforced Armor; a typed number still wins.
- **Shrine facts from the guide** (already modelled): Power 8+; it takes at most 25 from an attribute or weapon stat, but **attunements have no floor** (wiki: they can lose an unlimited amount, e.g. 100 down to about 20; `shrine()` skips them when pinning); 1 point in a stat lets the shrine raise it; one use only; mantra levels drop if the attunement drops below 20/40/60/80; weapons you no longer meet are unequipped; you must be Oathless when you use it (oaths come after the shrine); race points don't count toward its averaging.

**Talents**
- Prioritize talents tied to your **weapon type and attunements** (`kitOf`).
- Talent cap = 52 + (12 − normal mantras) × 2. Adding past it shows "Max talent limit reached!" with an opt-in box to allow going over.
- Show which talents are taken **before the shrine** (PRE badge) and count pre-shrine stats as reachable in suggestions.

**Equipment**
- Default targets: **500 HP and 50% physical armor**, then the Health ↔ Armor slider. **Never elemental armor** pips. Never Transfusion Ring.

**Optimizer**
- Optimize must always end within the budget (drop talents, then lower floors, then rebuild picks, then as a last resort picked mantras and a picked weapon), and the damage ↔ talent options slider must visibly change the result. Only when a build ends with exactly 0 points to spare can Fortitude stay the same before and after (moving it could make the shrine unreachable).

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
| `tests/browser/*.py` | Playwright checks: layout, preset_variants, ai_paths, ai_questions, stress_optimize (random over-budget builds), presets_import, ai_maker, traits, screenshot_parse, talents_tab, adjustments, talent_cap, bug_report. |
| `tests/fixtures/dwco-build.json` | A real deepwoken.co build (with traits) for import tests. |
| `tools/formulas/` | `dump.js` (exports data from index.html) + `build.py` (writes the workbook). |
| `docs/Meta Builder formulas.xlsx` | The formulas workbook. |

Data line formats: talent `name|category|rarity(+0 = not counted)|stats|o=alts|a=combined|t=talents|m=mantras|x=exclusive|w=weapon|q`; mantra `name|attunement|category+stars+type|req…` (type N = normal, costs 2 talent slots); equipment `name|slot|hp|physFlat|eleFlat|phys%|ele%|hp%|pips|req|set|flag|talents`; outfit `name|phys%|ele%|durability|req|`.

## Game rules and formulas (full detail in the workbook's Formulas sheet)

- **Budget** 330. Power = clamp(floor((points − 15)/15), 0, 20). Attunements after the first get their first point free. Points used = pre − shrine refund + added after − free attunement points − Mastery refunds.
- **Shrine of Order** (deepwoken.co algorithm, `shrine()`): average the invested stats; attributes and weapon stats can't end more than 25 below pre (pinned, excess shared); attunements have no floor and can drop to the average; floor; hand out leftovers; refund the rest. Needs Power 8.
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
- **Talent value** (`talentVal`): 90 × kit + 60 × key talent + (1 + popularity + 15 × synergy)(0.4 + 1.2 × slider) + 100 × (damage + PEN)(0.2 + 3.6 × (1 − slider)).
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
- **Build file (.txt)** (`buildFileJson` / `buildFileText`, "Download build file (.txt)" link in Share & export and the Share dialog; v0.34): owner-specified format, one line of JSON `{"preShrine":{"Strength":…,"Heavy Wep.":…,"Bloodrend":…},"postShrine":{…},"talents":[…]}` with the 16 stats in deepwoken.co order. Talents = the attunement milestone talents (Flamecharmer, Adept/Expert/Master …) and "… Unbounded" (75) the final stats reach, then "Oath: X" and that oath's own talent when it has exactly one (Blindseer: All-Seeing Eye), then every picked talent and prerequisite. Plain names (no [HVY] tags). The importer reads flat stat objects like these and takes the oath from an "Oath: X" talent when there is no `stats.meta.Oath`. `tests/browser/build_file.py` round-trips the owner's example (`tests/fixtures/build-file.txt`).
- Our Deepwoken-text export adds `== WEAPON ==`, `== OUTFIT ==`, `== PRE-SHRINE ==`, `== TRAITS ==` sections, read back on import.

## Where the data came from

deepwoken.co snapshot (October 2026), read in the Claude desktop app's built-in browser as JavaScript on a deepwoken.co page (same-origin fetches work there): `/api/proxy/get?type=all`, `/api/proxy/db/equipment|enchantments|oaths`, `/api/proxy/builds?sort=top&limit=50&page=N[&tags=…]`, `/api/proxy/builds/<id>`. Its builder bundle supplied the shrine, damage and EHP formulas. The fandom wiki blocks automated fetches except through WebFetch.

## Presets

Clean Slate · Bossraid (FTD 75 + WLL 50 pre, weapon 80 of choice) · Bossraid Mage (Saintsworn: FTD 75 + WLL 50 + INT 40 pre, attunement 100 + 15 in the other four elements) · Elder / Enmity (Bladeharper Ironsing: CHA 40 pre, INT 90 + STR 25 post, Ironsing 80, Shadowcast 20, Shattered Katana, Prophet's Cloak) · Diluvian (Dawnwalker, Brick Wall, FTD/WLL 100 → 75, all FTD/WLL talents) · Silentheart (STR 50 + AGL 50 pre, 25 each after, weapon 80, no attunements) · Attunementless (three splits, Fortitude 50 / 90, weapon 80) · Chime · High Charisma · High Strength · Jetstriker Agility (Jetstriker) · High Intelligence · Reinforced Armor · Mage · No Willpower.

## Hallowtide 2026 (October 31, 2026): added in v0.34

Numbers from deepwoken.co on November 16, 2026 (same endpoints as above). Weapons are compared by name against `#W`/`wdmg.txt`, outfits against `#O`/`#OT`.
- **Iron Veins** rename (was Alloyblood): `RENAMED_T` maps old names in saved builds, share links and imports. Add future game renames there.
- **Composite Path: Alloyblood** (category `Alloyblood`, BLD + IRN): Composite Path, Plasma Signal, Stored Plasma, Retained Hemoglobin, Ultrafiltration, Plasma Refresh, Hypoferritinemia (also needs Torture Mastery + Needleblade, so `aiParse` leaves it out of "alloyblood path"). Excludes Gilded Path: Scrapsinger. Mantras Infused Slash, Spinning Serum, Rising Plasma (no damage numbers on deepwoken.co yet, so not in `mdmg.txt`).
- **Exotherm Path: Sanguine Blaze** (category `Exotherm`, BLD + FLM): Exotherm Path, Critical Mass, Pressure Bleed, Burnout, Exothermic Finish. Excludes Azure Flames, Eruption Path, Wraith Path. Mantras Cauterize, Combustion Tide, Flashfusion (the wiki's "Flashpoint" is Flashfusion).
- `AI_PATHS` knows both; a third element is a bare-words match ("sanguine blaze", "black blood", "pink flames"/"pink fire").
- **Weapons:** Corvidirge Severants, Silas's Cenotaph, Cursed Flames, Alloyblood Daggers / Spear / Axe (needs the path talent + the mantra that summons it), Infected; Ironcry was in `wdmg.txt` but missing from `#W`.
- **Outfits:** Familiar Vagrant's / Sage's / Prince's Armor, Familiar Arachnid's Cloak. Crimsonsteel, Ceruleansteel and Etrean Steel Plate are on deepwoken.co with no stats, so not added.
- **Equipment:** Familiar Prosthetic Arm, Thorned Blazer, Harvestman's Halo / Cloak, Wreath of the Ardenstar, Raudra's Finger, Raudra's Pendant Earrings, and the cosmetics (Hunter's Chapeau, Crooked Witch Hat, Wispfire Beacon, Pilferer's Trophy, Eyes of the Moppet, Stitched Effigy, Mask of Phantoms, Coffin / Pumpkin Earrings). Mushroom costumes and Party Hat have no stats and aren't listed.
- **Balance changes:** Krulian Knife 13.5 dmg, Iron Requiem 18, Withered Phantomcleave 18 / 5% PEN / AGL 2 scaling, Imperial Staff 10% PEN, Duskguard Axe 24, Ysley's Pyre Keeper 30% PEN, First Light FLM 2 scaling; Merchant Robes 10/5, Pathfinder Thaumaturge 15/10, Pathfinder Sorcerer no INT req + Mantra Permanence, Skeptic Pioneer Ready or Not.
- Not added: Ether Surge (Vow of Iron-only enchant). Test: `tests/browser/hallowtide26.py`.
- deepwoken.co also lists about 100 older equippable items that aren't in `gear.txt` (Sorcerer's set, Hallowed Monastery, Corrupted items, many rings and earrings). Not part of this update; add them if the owner asks.

## Featured builds (owner's picks, November 17, 2026)

`src/data/featured.txt`: 15 builds the owner rates above the scraped top builds: 9 Chime of Conflict builds (weight 10 each, "weight these the highest"), 3 gank builds (weight 5) and the owner's 3 attunementless examples (weight 5; the Attunementless preset is built from them). Read from deepwoken.co (`/api/proxy/builds/<id>` on a deepwoken.co page) and dwt.sh (`api.dwt.sh/builds/<id>` on a dwt.sh page) in the built-in browser. `FEATURED` blends them into POP (as extra builds on top of the 802), CONDD (they count where their pre-shrine or final stats allow a talent) and REF (each repeated `weight` times). Add more by appending lines in the same format; the Chime preset's stats follow these builds. Not in our data: the Justicar Whistle talent and the Pumpkin Pitch mantra.

## Full build check (November 17, 2026)

`python3 tests/browser/full_check.py [seed] [scale]` runs about 180 builds (random presets x attunements x paths x stat changes, AI build maker descriptions, the 63 REF builds, every preset), Optimize and Auto-pick at several stages, the Summary and Armor tabs, and share link / Deepwoken text / build file round trips, checked by an independent checker (`window.__check`). Problems print as they're found. Run it in 5 parallel chunks, about 15 minutes in all: `full_check.py SEED 1 0 30`, `30 60`, `60 90`, `90 120` (random builds) and `-1 0` (presets, AI builds, popular builds, imports, buttons). Imported builds' own numbers (over budget, over the talent cap) are warnings, not problems. Fixed from its first report: Mind/Body weapon crash (`statName`), equipment optimizer restarts, `dropConflicts` / `conflictOf` (prerequisite path conflicts, Silentheart attunement mantras), shrine-skipped manual imports (`computeManual`: same stats before and after = no shrine), `easeFloors` with no build at all, `rebuildToBudget(seedP)`, `fixReup` + `better()` (a plan that fits without a re-raise always wins; `REUP_W`), Auto-pick taking back its picks, share codes carry `lp` (pre-shrine plan) used as the first seed.

## Ideas not done yet

- Race and aspect stat bonuses, gear set bonuses, talent health bonuses, ether modelling.
- Hover cards don't show on phones (Browse talents shows descriptions).
- Refreshing data: pull again from deepwoken.co with the endpoints above (from a deepwoken.co page) and regenerate `src/data/*.txt` in the same formats.

## Version history

The full list lives in `src/data/versions.txt` (shown in the app when you click the version). It is the only copy; don't repeat it here.
