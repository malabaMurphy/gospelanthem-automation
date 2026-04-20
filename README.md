# gospelanthem-automation

Automated daily Bible-verse posting for `@gospelanthem` on Instagram.

**Three posts every day, fully automatic:**

| Slot | Time (Tanzania) | Type | Format |
| --- | --- | --- | --- |
| Morning | 8:00 AM | Feed post | 1080×1080 square |
| Midday | 12:00 PM | Story | 1080×1920 vertical |
| Evening | 6:00 PM | Feed post | 1080×1080 square |

Each slot picks a different verse so all three feel fresh.

---

## Quick start

1. Read [`SETUP.md`](./SETUP.md) — one-time Meta API setup.
2. Push this repo to GitHub.
3. Add two secrets: `INSTAGRAM_USER_ID` and `IG_ACCESS_TOKEN`.
4. Trigger the workflow manually for each slot to verify, then it runs daily.

---

## Project structure

```
gospelanthem-automation/
├── .github/workflows/
│   └── daily_post.yml         # Three cron triggers (8am, 12pm, 6pm Tanzania)
├── fonts/                     # Bundled Lora + Poppins
├── posted/                    # Auto-populated archive of every poster
├── src/
│   ├── verses.json            # 234 curated KJV verses
│   ├── generate_poster.py     # Serene Cream renderer (feed + story formats)
│   ├── caption_builder.py     # Composes IG caption + hashtags
│   ├── publish_instagram.py   # Meta Graph API client (posts + stories)
│   └── main.py                # Slot-aware orchestrator
├── requirements.txt
├── SETUP.md                   # ← Start here
└── README.md
```

---

## Local testing

Generate any slot for any date without touching Instagram:

```bash
pip install -r requirements.txt

# Test today's three slots
python src/main.py --slot morning --dry-run
python src/main.py --slot midday  --dry-run
python src/main.py --slot evening --dry-run

# Test a specific date
python src/main.py --slot morning --dry-run --date 2026-12-25
```

Posters are saved to `posted/YYYY-MM-DD-<slot>.png`.

---

## How verses are picked

Each slot uses `(day_of_year - 1 + year_shift + slot_offset) % len(verses)`:

- Morning slot: offset 0
- Midday slot: offset 78
- Evening slot: offset 156

This guarantees that on any given day, the three slots get three *different* verses across the bank. Different years shift everything by 7 so the same calendar date gets fresh verses next year.

---

## Customization cheat sheet

| Want to change… | Edit… |
| --- | --- |
| Post times | The three `cron` lines in `.github/workflows/daily_post.yml` |
| Style colors / fonts | Constants at the top of `src/generate_poster.py` |
| Caption wording / hashtags | `src/caption_builder.py` |
| Add more verses | Append to `src/verses.json` |
| Add a 4th slot | Add to `SLOTS` dict in `src/main.py` and a 4th cron in the workflow |

---

## License & content notes

- KJV Bible text is **public domain** — free for any commercial use.
- Lora and Poppins fonts are SIL Open Font License — free to embed and redistribute.
- Code is yours.
