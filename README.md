# gospelanthem-automation

Automated daily Bible-verse posting for `@gospelanthem` on Instagram.

Every day at your chosen time, GitHub Actions:
1. Picks the day's KJV verse from a curated bank of 234 verses
2. Generates a "Serene Cream" 1080×1080 poster
3. Commits it to the `posted/` archive
4. Publishes it to Instagram via the Meta Graph API

No server, no PC needs to be on, no manual work after the one-time setup.

---

## Quick start

1. Read [`SETUP.md`](./SETUP.md) — walks you through the one-time Meta API setup (~30-60 minutes, you do this once and never again).
2. Push this repo to GitHub.
3. Add two secrets: `INSTAGRAM_USER_ID` and `IG_ACCESS_TOKEN`.
4. Trigger the workflow manually once to verify, then it runs daily.

---

## Project structure

```
gospelanthem-automation/
├── .github/workflows/
│   └── daily_post.yml         # The daily cron job
├── fonts/                     # Bundled Lora + Poppins (so it works anywhere)
├── posted/                    # Auto-populated archive of every poster ever made
├── src/
│   ├── verses.json            # 234 curated KJV verses
│   ├── generate_poster.py     # Serene Cream poster renderer
│   ├── caption_builder.py     # Composes the IG caption + hashtags
│   ├── publish_instagram.py   # Meta Graph API client
│   └── main.py                # Orchestrator (pick → render → publish)
├── requirements.txt           # Just Pillow
├── SETUP.md                   # ← Start here
└── README.md
```

---

## Local testing

You can preview today's poster (and the caption) without touching Instagram:

```bash
pip install -r requirements.txt
python src/main.py --dry-run
```

The poster is saved to `posted/YYYY-MM-DD.png`.

To preview a specific date:

```bash
python src/main.py --dry-run --date 2026-12-25
```

---

## How the verse is picked

`pick_verse_for_today` uses `(day_of_year - 1 + year_shift) % len(verses)`.
- Different days within the year → different verses.
- Different years → the same calendar date will get a different verse (rotates by 7).
- Adding new verses to `verses.json` automatically expands the rotation.

---

## Customization cheat sheet

| Want to change…              | Edit…                                             |
| ---------------------------- | ------------------------------------------------- |
| Post time                    | `cron` line in `.github/workflows/daily_post.yml` |
| Style colors / fonts         | Constants at the top of `src/generate_poster.py`  |
| Caption wording / hashtags   | `src/caption_builder.py`                          |
| Add more verses              | Append to `src/verses.json`                       |
| Use a different translation  | Replace verses in `src/verses.json`               |

---

## License & content notes

- KJV is **public domain** — free to use commercially with no attribution required.
- The fonts (Lora, Poppins) are licensed under the SIL Open Font License — free to use, embed, and redistribute.
- The code is yours to use however you like.
