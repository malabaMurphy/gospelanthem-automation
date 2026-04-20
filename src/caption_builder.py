"""
Caption builder for Instagram posts.
Composes a scroll-stopping caption: hook on top, verse below, hashtags at the end.
"""

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


def build_caption(verse_text: str, reference: str, theme: str = "",
                  hook: str = None) -> str:
    """
    Compose the Instagram caption.

    Order:
      1. Hook (if present) — modern, scroll-stopping
      2. KJV verse (in quotes)
      3. Reference
      4. Brief CTA
      5. Hashtags (separated by dots so they don't dominate)
    """
    quote = f'\u201c{verse_text}\u201d'
    parts = []

    if hook:
        parts.append(hook)
        parts.append("")
        parts.append("\u2014")
        parts.append("")

    parts.extend([
        quote,
        "",
        f"\u2014 {reference} (KJV)",
        "",
        "Tap \u2764\ufe0f if this met you today.",
        "",
        "Follow @gospelanthem for daily scripture.",
        "",
        ".",
        ".",
        ".",
        " ".join(HASHTAGS),
    ])
    return "\n".join(parts)


if __name__ == "__main__":
    print(build_caption(
        verse_text="Be still, and know that I am God.",
        reference="Psalm 46:10",
        theme="peace",
        hook="God isn't asking you to figure it out. He's asking you to be still and trust that He already has.",
    ))
