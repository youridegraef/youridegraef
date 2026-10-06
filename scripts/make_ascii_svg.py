"""Turn a background-free portrait (PNG with alpha) into a self-typing ASCII SVG.

Needs Pillow. Run locally when the photo changes:
    python3 scripts/make_ascii_svg.py path/to/cutout.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "portrait-ascii.svg"

RAMP = ".`:-=+*cs#%@"  # dark (sparse) -> bright (dense), drawn light on dark
COLS, ROWS = 100, 53
CW, LH, PAD = 6, 11, 12  # glyph width, line height, padding
CROP = (0.13, 0, 0.87, 0.585)  # left, top, right, bottom as fractions: head and shoulders
BG, FG = "#0d1117", "#c9d1d9"

src = Image.open(sys.argv[1]).convert("RGBA")
l, t, r, b = CROP
src = src.crop((int(src.width * l), int(src.height * t), int(src.width * r), int(src.height * b)))
alpha = src.getchannel("A").resize((COLS, ROWS), Image.LANCZOS)
# equalize over the subject only, so a flatly lit face still gets highlights and shadows
gray = ImageOps.equalize(ImageOps.grayscale(src), mask=src.getchannel("A")).resize((COLS, ROWS), Image.LANCZOS)

rows = []
for y in range(ROWS):
    line = ""
    for x in range(COLS):
        if alpha.getpixel((x, y)) < 128:
            line += " "  # background stays empty
        else:
            line += RAMP[gray.getpixel((x, y)) * len(RAMP) // 256]
    rows.append(line.rstrip())

w, h = COLS * CW + 2 * PAD, ROWS * LH + 2 * PAD
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10" fill="{FG}">',
    f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>',
]
for i, line in enumerate(rows):
    if not line:
        continue
    y, begin, width = PAD + i * LH, f"{i * 0.05:.2f}s", len(line) * CW
    # no-break spaces: plain ones collapse when the SVG is loaded through <img>
    esc = line.replace(" ", "\u00a0").replace("&", "&amp;").replace("<", "&lt;")
    out += [
        f'<clipPath id="r{i}"><rect x="{PAD}" y="{y}" width="0" height="{LH}">'
        f'<animate attributeName="width" from="0" to="{width}" begin="{begin}" dur="0.5s" fill="freeze"/></rect></clipPath>',
        f'<text x="{PAD}" y="{y + LH - 2}" textLength="{width}" clip-path="url(#r{i})">{esc}</text>',
        # block cursor riding the wipe edge
        f'<rect y="{y}" width="{CW}" height="{LH}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD + width}" begin="{begin}" dur="0.5s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.98;1" begin="{begin}" dur="0.5s" fill="freeze"/></rect>',
    ]
out.append("</svg>")
OUT.write_text("\n".join(out))
print(f"wrote {OUT.name}")
