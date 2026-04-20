"""
Poster Generator — Serene Cream style
Generates a 1080x1080 Instagram-ready poster for any verse + reference.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

# Resolve paths relative to this file so it works in any environment
ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

LORA_REG = str(FONTS / "Lora-Variable.ttf")
LORA_IT = str(FONTS / "Lora-Italic-Variable.ttf")
POP_LIGHT = str(FONTS / "Poppins-Light.ttf")
POP_MED = str(FONTS / "Poppins-Medium.ttf")
POP_REG = str(FONTS / "Poppins-Regular.ttf")

SIZE = 1080
HANDLE = "@gospelanthem"

# Serene Cream palette
BG = (245, 240, 230)        # warm cream
INK = (40, 35, 30)          # warm near-black
ACCENT = (160, 130, 90)     # muted gold
SUBTLE = (120, 110, 95)     # soft handle color


def _wrap_text(text, font, draw, max_width):
    """Wrap text into lines that fit within max_width pixels."""
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


def _fit_verse(text, draw, max_width, max_lines):
    """Auto-shrink the verse font size until the text fits within max_lines."""
    # Start large, shrink until it fits
    for size in range(72, 32, -2):
        font = ImageFont.truetype(LORA_IT, size)
        lines = _wrap_text(text, font, draw, max_width)
        if len(lines) <= max_lines:
            return font, lines, size
    # Fallback to smallest tried
    font = ImageFont.truetype(LORA_IT, 34)
    return font, _wrap_text(text, font, draw, max_width), 34


def _draw_centered_lines(draw, lines, font, y_start, color, line_spacing=1.3):
    line_h = _line_height(font, draw)
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (SIZE - w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += int(line_h * line_spacing)
    return y


def generate_poster(verse_text: str, reference: str, output_path: str) -> str:
    """
    Generate a Serene Cream poster.

    Args:
        verse_text: The Bible verse text (without quotes — they get added)
        reference: e.g. "Psalm 46:10"
        output_path: Where to save the .png

    Returns:
        The output_path on success.
    """
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    # --- Decorative outer border frame ---
    margin = 60
    draw.rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        outline=ACCENT,
        width=2,
    )

    # --- Top label: DAILY WORD ---
    label_font = ImageFont.truetype(POP_MED, 22)
    label = "DAILY WORD"
    # Letter-spacing fake by adding spaces
    label_spaced = " ".join(list(label))
    bbox = draw.textbbox((0, 0), label_spaced, font=label_font)
    label_w = bbox[2] - bbox[0]
    draw.text(((SIZE - label_w) // 2, 270), label_spaced,
              font=label_font, fill=ACCENT)

    # Decorative line under label
    cx = SIZE // 2
    draw.line([(cx - 60, 320), (cx + 60, 320)], fill=ACCENT, width=2)

    # --- Verse text (auto-fit) ---
    quote_text = f'\u201c{verse_text}\u201d'
    max_text_width = SIZE - 200
    max_lines = 6
    verse_font, lines, verse_size = _fit_verse(
        quote_text, draw, max_text_width, max_lines
    )
    line_h = _line_height(verse_font, draw)
    line_spacing = 1.3
    total_h = int(line_h * line_spacing) * (len(lines) - 1) + line_h

    # Center vertically in the available space (between label and reference area)
    available_top = 380
    available_bottom = 800
    available_h = available_bottom - available_top
    start_y = available_top + (available_h - total_h) // 2

    _draw_centered_lines(draw, lines, verse_font, start_y, INK, line_spacing)

    # --- Reference ---
    ref_font = ImageFont.truetype(POP_MED, 32)
    bbox = draw.textbbox((0, 0), reference, font=ref_font)
    ref_w = bbox[2] - bbox[0]
    ref_y = start_y + total_h + 50
    draw.text(((SIZE - ref_w) // 2, ref_y), reference,
              font=ref_font, fill=ACCENT)

    # --- Bottom handle ---
    handle_font = ImageFont.truetype(POP_LIGHT, 22)
    bbox = draw.textbbox((0, 0), HANDLE, font=handle_font)
    handle_w = bbox[2] - bbox[0]
    draw.text(((SIZE - handle_w) // 2, SIZE - 110), HANDLE,
              font=handle_font, fill=SUBTLE)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG", quality=95, optimize=True)
    return output_path


# ---- CLI for local testing ----
if __name__ == "__main__":
    import sys, json

    test_verses = [
        ("Be still, and know that I am God.", "Psalm 46:10"),
        (
            "For I know the thoughts that I think toward you, saith the Lord, "
            "thoughts of peace, and not of evil, to give you an expected end.",
            "Jeremiah 29:11",
        ),
        ("Charity never faileth.", "1 Corinthians 13:8"),
    ]

    out_dir = ROOT / "test_output"
    out_dir.mkdir(exist_ok=True)
    for i, (text, ref) in enumerate(test_verses):
        path = out_dir / f"test_{i+1}.png"
        generate_poster(text, ref, str(path))
        print(f"Generated: {path}")
