# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/dendrad0987-maker/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/dendrad0987-maker/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

The World in One Day — Thursday 19 November 2026. A newspaper-style front page
drawn entirely in code: a navy masthead naming the day, and six story panels
in a 2×3 grid, each with a coloured kicker, a two-line headline, one factual
subline, and a small flat vector icon. All text is rendered with a 5×7 bitmap
font defined in the program itself. Pure Python 3.13 standard library, no
network, deterministic — two runs produce byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024 PNG, under 1 MiB).

## The six stories

All six were verified against multiple news sources for Thursday 19 November 2026:

1. **Summit — Trump, Xi, Putin meet in Shenzhen.** The three leaders hold their
   first three-way summit on the APEC sidelines in Shenzhen, then issue a joint
   declaration on nuclear risks and stable energy flows. (Reuters / AP)
2. **The Hague — ICJ rules against Myanmar.** The International Court of Justice
   rules against Myanmar in the Rohingya genocide case brought by The Gambia
   in 2019, over the 2017 crackdown. (AP / Reuters)
3. **Ukraine — Kerch Bridge hit third time in week.** Ukraine strikes the
   Crimean (Kerch) Bridge again, the third attack in seven days. (Reuters)
4. **Gaza — Israeli tanks push into central Gaza.** The advance goes beyond the
   ceasefire line; Hamas calls it a violation. (Reuters / AP)
5. **Weather — Cyclone Akvan nears India coast.** The storm is expected to make
   landfall on the Andhra Pradesh–Odisha coast on Friday 20 November as a
   severe cyclonic storm, winds 90–100 km/h gusting to 110 km/h. (IMD / Reuters)
6. **Climate — COP31 talks enter final stage.** Fossil-fuel language
   ("transition away" vs phaseout) is still unresolved as talks enter their
   final stage. (Reuters / AP)

No figures beyond those reported are shown; no hype, no speculation as fact.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
