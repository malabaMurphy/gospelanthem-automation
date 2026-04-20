"""
Main orchestrator for daily Instagram posting.

Flow:
  1. Pick today's verse (deterministic — based on day-of-year so no duplicates within the year)
  2. Generate the Serene Cream poster
  3. Save it to posted/YYYY-MM-DD.png so it's committed to the repo
  4. Build the caption
  5. Publish to Instagram Graph API using the raw GitHub URL of the just-committed image

This script is designed to be invoked by GitHub Actions but also runnable locally
for testing (with --dry-run to skip actual publishing).
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


def pick_verse_for_today(verses: list, today: date) -> dict:
    """
    Deterministic verse selection based on day-of-year + year offset.
    Day-of-year (1-366) maps into the verses list with modulo, plus a
    year-based shift so consecutive years aren't identical.
    """
    doy = today.timetuple().tm_yday        # 1..366
    year_shift = (today.year - 2025) * 7   # rotate by 7 each year
    idx = (doy - 1 + year_shift) % len(verses)
    return verses[idx]


def build_image_url(repo_slug: str, branch: str, relative_path: str) -> str:
    """Build a raw.githubusercontent.com URL for the just-committed image."""
    # Example: https://raw.githubusercontent.com/user/repo/main/posted/2026-04-20.png
    return f"https://raw.githubusercontent.com/{repo_slug}/{branch}/{relative_path}"


def main():
    parser = argparse.ArgumentParser(description="Daily Instagram poster")
    parser.add_argument(
        "--mode",
        choices=["generate", "publish", "all"],
        default="all",
        help=(
            "generate: only build the poster (used by step 1 of CI). "
            "publish: only publish (assumes image already committed and reachable). "
            "all: do both, useful locally with --dry-run."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the poster but do not call the Instagram API.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="ISO date override (YYYY-MM-DD), useful for testing.",
    )
    args = parser.parse_args()

    # Resolve target date
    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        target_date = date.today()

    # Load verses
    with open(VERSES_PATH, "r", encoding="utf-8") as f:
        verses = json.load(f)

    verse = pick_verse_for_today(verses, target_date)
    print(f"[main] Date: {target_date.isoformat()}")
    print(f"[main] Verse: \"{verse['text']}\" — {verse['ref']}")
    print(f"[main] Theme: {verse.get('theme', 'n/a')}")

    # Path that the workflow will commit
    image_filename = f"{target_date.isoformat()}.png"
    image_relpath = f"posted/{image_filename}"
    image_path = ROOT / image_relpath

    if args.mode in ("generate", "all"):
        POSTED_DIR.mkdir(exist_ok=True)
        generate_poster(verse["text"], verse["ref"], str(image_path))
        print(f"[main] Poster saved: {image_path}")

    if args.mode in ("publish", "all"):
        if args.dry_run:
            print("[main] DRY RUN — skipping Instagram publish.")
            print("[main] Caption preview:")
            print("-" * 50)
            print(build_caption(verse["text"], verse["ref"], verse.get("theme", "")))
            print("-" * 50)
            return

        # Required env vars (set in GitHub Actions secrets)
        ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
        access_token = os.environ.get("IG_ACCESS_TOKEN")
        repo_slug = os.environ.get("GITHUB_REPOSITORY")  # auto-set by Actions
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
        caption = build_caption(verse["text"], verse["ref"], verse.get("theme", ""))

        media_id = publish_image(ig_user_id, image_url, caption, access_token)
        print(f"[main] Done. Posted media id: {media_id}")


if __name__ == "__main__":
    main()
