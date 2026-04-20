"""
Poster Generator — Serene Cream style with two-part layout.

Top half: Bold modern HOOK (Poppins, sans-serif) — scroll-stopper
Bottom half: KJV verse (Lora italic) + reference

Supports two formats:
  - feed:  1080x1080 square Instagram post
  - story: 1080x1920 vertical Instagram story
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

LORA_REG = str(FONTS / "Lora-Variable.ttf")
LORA_IT = str(FONTS / "Lora-Italic-Variable.ttf")
POP_LIGHT = str(FONTS / "Poppins-Light.ttf")
POP_MED = str(FONTS / "Poppins-Medium.ttf")
POP_BOLD = str(FONTS / "Poppins-Bold.ttf") if (FONTS / "Poppins-Bold.ttf").exists() else POP_MED
POP_REG = str(FONTS / "Poppins-Regular.ttf")

HANDLE = "@gospelanthem"

# Serene Cream palette
BG = (245, 240, 230)
INK = (40, 35, 30)
ACCENT = (160, 130, 90)
SUBTLE = (120, 110, 95)
VERSE_GREY = (90, 80, 70)  # softer than INK so the hook dominates

FORMATS = {
    "feed": {
        "size": (1080, 1080),
        "label_y": 110,
        # Hook section
        "hook_top": 175,
        "hook_bottom": 590,
        "hook_max_width": 880,
        "hook_max_size": 60,
        "hook_min_size": 36,
        "hook_max_lines": 6,
        # Divider
        "divider_y": 620,
        # Verse section
        "verse_top": 660,
        "verse_bottom": 880,
        "verse_max_width": 820,
        "verse_max_size": 36,
        "verse_min_size": 22,
        "verse_max_lines": 4,
        "ref_offset": 30,
        "ref_size": 24,
        # Bottom
        "handle_y_from_bottom": 100,
        "handle_size": 20,
        "border_margin": 50,
    },
    "story": {
        "size": (1080, 1920),
        "label_y": 220,
        # Hook section
        "hook_top": 320,
        "hook_bottom": 1100,
        "hook_max_width": 880,
        "hook_max_size": 78,
        "hook_min_size": 44,
        "hook_max_lines": 8,
        # Divider
        "divider_y": 1160,
        # Verse section
        "verse_top": 1220,
        "verse_bottom": 1620,
        "verse_max_width": 880,
        "verse_max_size": 42,
        "verse_min_size": 26,
        "verse_max_lines": 5,
        "ref_offset": 40,
        "ref_size": 28,
        # Bottom
        "handle_y_from_bottom": 160,
        "handle_size": 24,
        "border_margin": 60,
    },
}


def _wrap_text(text, font, draw, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = (current + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _line_height(font, draw, sample="Hg"):
    bbox = draw.textbbox((0, 0), sample, font=font)
    return bbox[3] - bbox[1]


def _fit_text(text, font_path, draw, max_width, max_lines, max_size, min_size):
    """Find largest font size where text fits within max_lines."""
    for size in range(max_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size)
        lines = _wrap_text(text, font, draw, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = ImageFont.truetype(font_path, min_size)
    return font, _wrap_text(text, font, draw, max_width)


def _draw_centered_lines(draw, lines, font, y_start, color, width, line_spacing=1.25):
    line_h = _line_height(font, draw)
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (width - w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += int(line_h * line_spacing)
    return y


def generate_poster(verse_text: str, reference: str, output_path: str,
                    format: str = "feed", hook: str = None) -> str:
    """
    Generate a Serene Cream poster with hook + verse two-part layout.

    Args:
        verse_text: KJV verse text
        reference: e.g. "Psalm 46:10"
        output_path: Where to save .png
        format: "feed" (1080x1080) or "story" (1080x1920)
        hook: Modern reflection / scroll-stopper. If None, falls back to verse-only.
    """
    if format not in FORMATS:
        raise ValueError(f"format must be one of {list(FORMATS.keys())}")

    cfg = FORMATS[format]
    width, height = cfg["size"]

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # --- Decorative outer border ---
    m = cfg["border_margin"]
    draw.rectangle([m, m, width - m, height - m], outline=ACCENT, width=2)

    # --- Top label "DAILY WORD" ---
    label_font = ImageFont.truetype(POP_MED, 22 if format == "feed" else 26)
    label = "DAILY WORD"
    label_spaced = " ".join(list(label))
    bbox = draw.textbbox((0, 0), label_spaced, font=label_font)
    label_w = bbox[2] - bbox[0]
    draw.text(((width - label_w) // 2, cfg["label_y"]), label_spaced,
              font=label_font, fill=ACCENT)

    # Small decorative line under label
    cx = width // 2
    line_y = cfg["label_y"] + (35 if format == "feed" else 45)
    draw.line([(cx - 50, line_y), (cx + 50, line_y)], fill=ACCENT, width=2)

    # --- HOOK (bold sans, large, dominant) ---
    if hook:
        hook_font, hook_lines = _fit_text(
            hook, POP_BOLD, draw,
            cfg["hook_max_width"],
            cfg["hook_max_lines"],
            cfg["hook_max_size"],
            cfg["hook_min_size"],
        )
        hook_line_h = _line_height(hook_font, draw)
        hook_spacing = 1.2
        hook_total_h = int(hook_line_h * hook_spacing) * (len(hook_lines) - 1) + hook_line_h
        hook_avail_h = cfg["hook_bottom"] - cfg["hook_top"]
        hook_start_y = cfg["hook_top"] + (hook_avail_h - hook_total_h) // 2
        _draw_centered_lines(draw, hook_lines, hook_font, hook_start_y, INK, width, hook_spacing)

        # Divider line between hook and verse
        div_y = cfg["divider_y"]
        draw.line([(cx - 30, div_y), (cx + 30, div_y)], fill=ACCENT, width=1)

    # --- VERSE (Lora italic, smaller, supporting) ---
    quote_text = f'\u201c{verse_text}\u201d'
    verse_font, verse_lines = _fit_text(
        quote_text, LORA_IT, draw,
        cfg["verse_max_width"],
        cfg["verse_max_lines"],
        cfg["verse_max_size"],
        cfg["verse_min_size"],
    )
    verse_line_h = _line_height(verse_font, draw)
    verse_spacing = 1.3
    verse_total_h = int(verse_line_h * verse_spacing) * (len(verse_lines) - 1) + verse_line_h
    verse_avail_h = cfg["verse_bottom"] - cfg["verse_top"]
    verse_start_y = cfg["verse_top"] + (verse_avail_h - verse_total_h) // 2
    _draw_centered_lines(draw, verse_lines, verse_font, verse_start_y, VERSE_GREY, width, verse_spacing)

    # --- Reference ---
    ref_font = ImageFont.truetype(POP_MED, cfg["ref_size"])
    bbox = draw.textbbox((0, 0), reference, font=ref_font)
    ref_w = bbox[2] - bbox[0]
    ref_y = verse_start_y + verse_total_h + cfg["ref_offset"]
    draw.text(((width - ref_w) // 2, ref_y), reference,
              font=ref_font, fill=ACCENT)

    # --- Bottom handle ---
    handle_font = ImageFont.truetype(POP_LIGHT, cfg["handle_size"])
    bbox = draw.textbbox((0, 0), HANDLE, font=handle_font)
    handle_w = bbox[2] - bbox[0]
    draw.text(((width - handle_w) // 2, height - cfg["handle_y_from_bottom"]),
              HANDLE, font=handle_font, fill=SUBTLE)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG", quality=95, optimize=True)
    return output_path


# CLI
if __name__ == "__main__":
    out_dir = ROOT / "test_output"
    out_dir.mkdir(exist_ok=True)

    test_cases = [
        (
            "God isn't asking you to figure it out. He's asking you to be still and trust that He already has.",
            "Be still, and know that I am God.",
            "Psalm 46:10",
        ),
        (
            "He's not making it up as He goes. He has a plan for you \u2014 and it ends well.",
            "For I know the thoughts that I think toward you, saith the Lord, thoughts of peace, and not of evil, to give you an expected end.",
            "Jeremiah 29:11",
        ),
        (
            "Love outlasts everything. Strategy fails. Love doesn't.",
            "Charity never faileth.",
            "1 Corinthians 13:8",
        ),
    ]

    for i, (hook, verse, ref) in enumerate(test_cases):
        for fmt in ["feed", "story"]:
            path = out_dir / f"test_{i+1}_{fmt}.png"
            generate_poster(verse, ref, str(path), format=fmt, hook=hook)
            print(f"Generated: {path}")
