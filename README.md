# Meta Builder

A Deepwoken build planner built around the ability to optimize your builds effectively and help you create.

**Use it:** https://itsmrchickenss.github.io/meta-builder/

**Desktop app (Mac and Windows):** download the latest from [Releases](https://github.com/itsmrchickenss/meta-builder/releases/latest). To host it on your own server, see [app/README.md](app/README.md).

- Optimizer that picks pre-shrine stats and the pre/post order for every talent, or Manual mode where you set every stat
- Shrine of Order, Shrine of Mastery, and save/load pre- and post-shrine stats
- AI build maker: describe the build in plain words ("insanity build with flamecharm, tanky") and it fills in the starting questions
- Guided starting presets (including Bossraid, Bossraid Mage and Chime, averaged from deepwoken.co's top builds with those tags), required talents, talent synergies, auto-pick, help mode
- Hover any talent to see what it does; the talent cap is enforced when optimizing
- "What you want" box and stat limits: tell the optimizer things like "no willpower, keep intelligence under 20, no Ghost" before it builds
- Avoid list for talents you never want, and an Oath requirements menu showing what every oath needs and whether it fits
- Weapon, enchant and mantra damage, weapon comparison
- Armor and equipment with a health vs physical armor optimizer (500 HP minimum by default) and gear talents
- Share links: every build can be copied as a link that opens it here

Data comes from deepwoken.co (October 2026). Race stat bonuses aren't counted.

## Working on it

Source is in `src/` (`template.html` plus data files). Build with `python3 src/build.py`, test with `node tests/core-test.js`. See [NOTES.md](NOTES.md) for how everything works.

## Disclaimer

Meta Builder is an unofficial fan tool. It is not affiliated with or endorsed by the developers of Deepwoken or by deepwoken.co. Deepwoken and its game content (talents, mantras, weapons, items and their names and descriptions) belong to their respective owners. The MIT license below covers only the code written for this project.

## License

[MIT](LICENSE)
