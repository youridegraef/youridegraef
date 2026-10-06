"""Write info-card.svg, a neofetch-style panel. Edit ROWS and rerun:
    python3 scripts/make_info_card.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

TITLE = "youri@github"
ROWS = [
    ("Role", "Full-stack developer"),
    ("Now", "Co-founder @ Feldon"),
    ("Also", "De Graef Digital"),
    ("Study", "HBO-ICT @ Fontys"),
    ("Based", "Eindhoven, NL"),
    None,
    ("Backend", ".NET · Postgres · Node · Hono"),
    ("Frontend", "Nuxt · Next.js · Astro · Tailwind"),
    ("Infra", "Cloudflare · Supabase · Railway"),
    ("Focus", "APIs, databases, infrastructure"),
    None,
    ("Built", "Optimzd · ads dashboard for agencies"),
    ("", "Ombit · rental backoffice"),
    ("", "Verslokaal Leivere · website"),
]

# Sized to match the portrait's height at README widths (490 next to 370).
W, H, PAD, LH = 560, 412, 24, 21
BG, FG, MUTED, KEY, ACCENT = "#0d1117", "#c9d1d9", "#8b949e", "#58a6ff", "#39d353"

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="14" fill="{FG}">',
    "<style>.l{opacity:0;animation:i .4s ease-out forwards}"
    "@keyframes i{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
    "@media (prefers-reduced-motion:reduce){.l{animation:none;opacity:1}}</style>",
    f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
]
for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
    out.append(f'<circle cx="{PAD + 6 + i * 20}" cy="22" r="6" fill="{color}"/>')

y = 62
user, host = TITLE.split("@")
lines = [
    f'<text x="{PAD}" y="{y}" font-weight="bold"><tspan fill="{ACCENT}">{user}</tspan>'
    f'<tspan fill="{MUTED}">@</tspan><tspan fill="{ACCENT}">{host}</tspan></text>',
    f'<text x="{PAD}" y="{y + LH}" fill="{MUTED}">{"-" * len(TITLE)}</text>',
]
y += 2 * LH
for row in ROWS:
    if row:
        key, value = row
        value = value.replace("&", "&amp;")
        lines.append(
            f'<text x="{PAD}" y="{y}"><tspan fill="{KEY}" font-weight="bold">{key}</tspan>'
            f'<tspan x="{PAD + 90}">{value}</tspan></text>'
        )
    y += LH if row else LH // 2
for i, line in enumerate(lines):
    out.append(f'<g class="l" style="animation-delay:{0.3 + i * 0.12:.2f}s">{line}</g>')

swatches = ["#161b22", "#f85149", ACCENT, "#d29922", KEY, "#bc8cff", "#39c5cf", FG]
for i, color in enumerate(swatches):
    out.append(f'<rect x="{PAD + i * 24}" y="{H - PAD - 16}" width="24" height="16" fill="{color}"/>')
out.append("</svg>")
OUT.write_text("\n".join(out))
print(f"wrote {OUT.name}")
