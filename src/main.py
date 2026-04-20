"""
Main orchestrator for daily Instagram posting.

Supports 3 daily slots:
  - morning  (8 AM Tanzania) -> feed post (square)
  - midday   (12 PM Tanzania) -> story (vertical)
  - evening  (6 PM Tanzania) -> feed post (square)

Each slot picks a *different* verse for the same day so posts feel fresh.

Flow:
  1. Pick the verse for today + this slot (deterministic)
  2. Generate the right poster (feed or story format)
  3. Save it under posted/YYYY-MM-DD-<slot>.png
  4. Publish to Instagram Graph API
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Make src importable when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_poster import generate_poster
from caption_builder import build_caption
from publish_instagram import publish_image


ROOT = Path(__file__).resolve().parent.parent
VERSES_PATH = ROOT / "src" / "verses.json"
POSTED_DIR = ROOT / "posted"


# Slot definitions
SLOTS = {
    "morning": {
        "format": "feed",
        "media_type": None,        # regular feed post
        "verse_offset": 0,         # uses today's primary verse
    },
    "midday": {
        "format": "story",
        "media_type": "STORIES",
        "verse_offset": 78,        # offset into the verses list (~1/3)
    },
    "evening": {
        "format": "feed",
        "media_type": None,
        "verse_offset": 156,       # offset into the verses list (~2/3)
    },
}


def pick_verse(verses: list, today: date, slot_offset: int) -> dict:
    """
    Pick a verse for a given date + slot.
    Uses day-of-year + year shift + slot offset, all modulo verse count.
    Different slots on the same day get different verses.
    """
    doy = today.timetuple().tm_yday
    year_shift = (today.year - 2025) * 7
    idx = (doy - 1 + year_shift + slot_offset) % len(verses)
    return verses[idx]


def build_image_url(repo_slug: str, branch: str, relative_path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo_slug}/{branch}/{relative_path}"


def main():
    parser = argparse.ArgumentParser(description="Daily Instagram poster")
    parser.add_argument(
        "--slot",
        choices=list(SLOTS.keys()),
        required=True,
        help="Which daily slot to publish (morning, midday, or evening)",
    )
    parser.add_argument(
        "--mode",
        choices=["generate", "publish", "all"],
        default="all",
        help="generate-only, publish-only, or both (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the poster but skip the Instagram API call.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="ISO date override (YYYY-MM-DD), useful for testing.",
    )
    args = parser.parse_args()

    slot = args.slot
    slot_cfg = SLOTS[slot]

    # Resolve target date
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    # Load verses
    with open(VERSES_PATH, "r", encoding="utf-8") as f:
        verses = json.load(f)

    verse = pick_verse(verses, target_date, slot_cfg["verse_offset"])
    print(f"[main] Date: {target_date.isoformat()}")
    print(f"[main] Slot: {slot} ({slot_cfg['format']})")
    print(f"[main] Verse: \"{verse['text']}\" — {verse['ref']}")
    print(f"[main] Theme: {verse.get('theme', 'n/a')}")

    # Output filename includes slot so each post has its own file
    image_filename = f"{target_date.isoformat()}-{slot}.png"
    image_relpath = f"posted/{image_filename}"
    image_path = ROOT / image_relpath

    if args.mode in ("generate", "all"):
        POSTED_DIR.mkdir(exist_ok=True)
        generate_poster(
            verse["text"],
            verse["ref"],
            str(image_path),
            format=slot_cfg["format"],
            hook=verse.get("hook"),
        )
        print(f"[main] Poster saved: {image_path}")

    if args.mode in ("publish", "all"):
        if args.dry_run:
            print("[main] DRY RUN — skipping Instagram publish.")
            print("[main] Caption preview:")
            print("-" * 50)
            if slot_cfg["media_type"] == "STORIES":
                print("(Stories don't have captions on Instagram)")
            else:
                print(build_caption(
                    verse["text"], verse["ref"],
                    theme=verse.get("theme", ""),
                    hook=verse.get("hook"),
                ))
            print("-" * 50)
            return

        ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
        access_token = os.environ.get("IG_ACCESS_TOKEN")
        repo_slug = os.environ.get("GITHUB_REPOSITORY")
        branch = os.environ.get("GITHUB_REF_NAME", "main")

        missing = [
            name for name, val in [
                ("INSTAGRAM_USER_ID", ig_user_id),
                ("IG_ACCESS_TOKEN", access_token),
                ("GITHUB_REPOSITORY", repo_slug),
            ] if not val
        ]
        if missing:
            raise SystemExit(f"Missing required env vars: {missing}")

        image_url = build_image_url(repo_slug, branch, image_relpath)
        caption = build_caption(
            verse["text"], verse["ref"],
            theme=verse.get("theme", ""),
            hook=verse.get("hook"),
        )

        media_id = publish_image(
            ig_user_id, image_url, caption, access_token,
            media_type=slot_cfg["media_type"],
        )
        print(f"[main] Done. Posted media id: {media_id}")


if __name__ == "__main__":
    main()
