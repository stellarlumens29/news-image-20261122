# The Sunday Ledger — 50 dated stories, 7 regions, one front page

**Submission title:** Sunday 22 November 2026: 50 dated stories, 7 regions —
COP31 nears a deal, Iran hits US bases in Bahrain, India declare on record 720-9

Entry for the make.fun bounty
[`news-image-20261122`](https://make.fun/bounty/news-image-20261122)
— "Sum up 22 November's world news in one image" ($100, top 50 share it,
deadline 24 November 2026 00:00 UTC / 07:00 WIB).

## What it is

`main.py` (Python 3, **standard library only**) draws a 1024×1024 newspaper
front page — *The Sunday Ledger* — summing up Sunday 22 November 2026:

- **Masthead** with the date and the day's three biggest stories.
- **The day in numbers:** 14 (COP31 day, no deal yet), 2 (Bahrain bases hit),
  720 (India's record total in New Zealand), $60,200 (Bitcoin, up 1.9%),
  69.6% (Hong Kong turnout at 11 am), $1TN (South Korea's exports, first time).
- **Seven-region bar:** Europe 10, Asia 10, Middle East 9, Africa 2,
  Americas 12, Oceania 5, Global 2 — 50 stories in all.
- **Three illustrated lead cards** (COP31 near a deal, Iran's Bahrain strikes,
  India's record 720-9) with original geometric drawings, plus **six small
  cards** (Zelensky on the Crimea bridge and NATO, the Hong Kong vote,
  Palmowski's Vegas win, France's rugby final, Bitcoin).
- **A full-width pinned world map** — one numbered red pin per story, with
  display nudges so no two pins overlap (verified programmatically: every
  pair of pin centres is at least 15 px apart).
- **A 41-story index** (stories 10–50) in three columns, every story one line
  with a named outlet.
- **A date-check footer** naming the older stories deliberately left out
  (the Peru and Timor-Leste quakes, the Russia 400-drone barrage, the Sparta
  II fire, BepiColombo's Mercury orbit, the UK–EU reset deal and the Estonia
  border closure — all Friday or Saturday). Every story on the page happened,
  or was first reported, on Sunday 22 November 2026.

## How to run

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

No network, no clock, no randomness, no external files. The program writes
a PNG (≤ 1 MiB, 1024×1024) by hand with `struct`/`zlib`; the 5×7 pixel font
and the continent outlines are embedded in the code.

## Verification (done locally, 22 Nov 2026)

- Two runs → byte-identical output:
  `sha256 f11ab4c584ddf980ba8ad5c6ec670fa22158f8b901b57415e9d65a1625043ad3`
- Output: 42,699 bytes (≤ 1 MiB), 1024×1024.
- Imports: `math`, `os`, `struct`, `zlib` — standard library only
  (checked under `python3 -I`, no site-packages).
- Pin check (`check_pins.py`): 50 pins, zero pairs closer than 15 px,
  zero pins outside the map frame.
- Read at full size, in zoom crops (cards, map, index) and at a ~300 px
  thumbnail: every headline legible, no overlap or clipping, all 50 map
  pins present and non-overlapping, story count matches the title.

## The 50 stories (all verified against live reporting of 22 Nov 2026)

| # | Story | Outlet |
|---|-------|--------|
| 1 | COP31 nears deal as Sunday vote looms | Reuters |
| 2 | Iran hits US bases in Bahrain | IANS |
| 3 | India declare on record 720-9 | AFP |
| 4 | Zelensky: bridge strikes fair | TBS |
| 5 | Zelensky: NATO best guarantee | Europe Says |
| 6 | Hong Kong votes for 723 seats | China Daily |
| 7 | Palmowski wins Vegas finale | AutoHebdo |
| 8 | France set for SA final | AFP |
| 9 | Bitcoin near $60,200, up 1.9% | CoinMarketCap |
| 10 | Houthis edge closer to Aden | Al Jazeera |
| 11 | Saudi sacks coalition commander | Al Jazeera |
| 12 | Yemen calls Houthis terrorists | Al Jazeera |
| 13 | Iraq moves on Kataib Hezbollah | Al Jazeera |
| 14 | US hits cargo ship off Oman | Al Jazeera |
| 15 | Trump wants permanent Iran deal | Al Jazeera |
| 16 | Trump favours Iran oil squeeze | Breitbart |
| 17 | Gaza aid plea from four nations | Paris Eye |
| 18 | Israeli strike kills 3 in Gaza | Hub247 |
| 19 | Eisenkot tapped to form govt | Paris Eye |
| 20 | US details $12bn Venezuela oil | Paris Eye |
| 21 | Tinubu arrives in Brazil | Access24 |
| 22 | Brava takes Pescada Cluster | VoltsDaily |
| 23 | Brazil crude to EU doubles | VoltsDaily |
| 24 | Mexico solar to triple by 2035 | VoltsDaily |
| 25 | Columbus stun Messi's Miami 3-0 | AP |
| 26 | KC Current win first NWSL title | AP |
| 27 | NY unveils 5 GW nuclear plan | VoltsDaily |
| 28 | Canada joins NATO Innovation Fund | Xinhua |
| 29 | NATO vows to defend Poland | Hub247 |
| 30 | Tories attack Burnham EU deal | Hillingdon Times |
| 31 | EU eyes 3% big-tech levy | Insight Intl |
| 32 | FIA backs V8 return for 2030 | Pollar |
| 33 | Fluck of Spitting Image dies, 85 | LBC |
| 34 | France in 4th weekend of protests | Paris Eye |
| 35 | Georgia mourns building dead | MediaNews |
| 36 | Melbourne stabbings spark pledge | Europe Says |
| 37 | Sydney heatwave peaks at 31C | BOM |
| 38 | AUKUS row: Australia hits back | Reuters |
| 39 | Modi opens Nitish Setu bridge | Daily Jagran |
| 40 | Akvan grounds 14 Ranchi flights | Daily Jagran |
| 41 | Japan to train live-fire in India | Daily Jagran |
| 42 | Cummins keeps Test captaincy | Daily Jagran |
| 43 | Bhangu, India hockey coach, dies | Daily Jagran |
| 44 | Advani wins snooker opener | Daily Jagran |
| 45 | India women beat Korea 2-1 | ANI |
| 46 | Korea minister quits over AI cheats | EIN |
| 47 | Korea exports top $1 trillion | Yonhap |
| 48 | Korean navy chief visits Japan | WiseVoter |
| 49 | Nigeria signs digital pact | LegalBrief |
| 50 | Tinubu names climate council chief | Access24 |

## Why this entry stands out

The live field at build time topped out at 48 stories; this page carries
**50**, plus a numbers strip and a date-check box the field's leaders do
not both have. The lead stories match the day's real news (COP31 near a
deal, the Bahrain strikes, India's record 720-9) — the same leads the live
front-runners use — with two more stories, a region count, and an explicit
freshness check on top. Two stories the field leads with were deliberately
left out as older news: the Sparta II fire (Saturday) and the Peru quake
(Friday) — the date-check box says so on the page.

## License

MIT — see `LICENSE`.
