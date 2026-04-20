"""
Caption builder for Instagram posts.
Builds a nicely-formatted caption from a verse + reference.
"""

# A curated set of relevant, well-performing Christian hashtags.
# Order matters less than quality. Instagram allows up to 30; we use ~22.
HASHTAGS = [
    "#bibleverse",
    "#dailybibleverse",
    "#dailydevotional",
    "#christianquotes",
    "#biblequotes",
    "#scripture",
    "#scriptureoftheday",
    "#wordofgod",
    "#faith",
    "#jesus",
    "#jesuschrist",
    "#christian",
    "#christianity",
    "#gospel",
    "#godisgood",
    "#prayer",
    "#blessed",
    "#hope",
    "#kjv",
    "#kingjamesbible",
    "#gospelanthem",
    "#dailyword",
]


def build_caption(verse_text: str, reference: str, theme: str = "") -> str:
    """
    Compose the Instagram caption.

    Returns a string with:
      - The verse in quotes
      - The reference
      - A short reflection prompt
      - Hashtags
    """
    quote = f'\u201c{verse_text}\u201d'
    parts = [
        quote,
        "",
        f"— {reference} (KJV)",
        "",
        "Let this word strengthen your heart today. \U0001F64F\u2728",
        "",
        "Follow @gospelanthem for daily scripture.",
        "",
        ".",
        ".",
        ".",
        " ".join(HASHTAGS),
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    print(build_caption(
        "Be still, and know that I am God.",
        "Psalm 46:10",
        "peace",
    ))
