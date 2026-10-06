"""Fetch the public contribution calendar and render contrib-heatmap.svg.

Stdlib only, no token: GitHub serves the calendar as public HTML.
Usage: python3 scripts/heatmap.py [username]
"""
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "youridegraef"
OUT = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG, FG, MUTED = "#0d1117", "#c9d1d9", "#8b949e"
CELL, PITCH = 12, 15
LEFT, TOP, W = 36, 44, 860
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def parse(html):
    """Return [(date, level, count)] sorted by date."""
    counts = {}
    for cell_id, text in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', html):
        m = re.match(r"\s*([\d,]+) contribution", text)
        counts[cell_id] = int(m.group(1).replace(",", "")) if m else 0
    days = []
    for tag in re.findall(r"<td[^>]*data-date[^>]*>", html):
        attr = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        days.append((date.fromisoformat(attr["data-date"]), int(attr["data-level"]), counts.get(attr["id"], 0)))
    return sorted(days)


def streaks(days):
    """Return (current, longest) streak in days. A missing today does not break the current streak."""
    longest = run = 0
    for _, _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    for i, (_, _, n) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i:
            break
    return current, longest


def render(days):
    first = days[0][0]
    # GitHub weeks start on Sunday
    offset = (first.weekday() + 1) % 7
    weeks = (offset + len(days) + 6) // 7
    height = TOP + 7 * PITCH + 62
    left = (W - (LEFT + weeks * PITCH - (PITCH - CELL))) // 2 + LEFT

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">',
        "<style>.d{opacity:0;animation:i .45s ease-out forwards}"
        "@keyframes i{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        "@media (prefers-reduced-motion:reduce){.d{animation:none;opacity:1}}</style>",
        f'<rect width="{W}" height="{height}" rx="10" fill="{BG}"/>',
    ]
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{left - 8}" y="{TOP + row * PITCH + 10}" fill="{MUTED}" text-anchor="end">{label}</text>')

    last_month = None
    for i, (d, level, n) in enumerate(days):
        col, row = divmod(i + offset, 7)
        x, y = left + col * PITCH, TOP + row * PITCH
        if d.month != last_month and d.day <= 7 and col < weeks - 1:
            out.append(f'<text x="{x}" y="{TOP - 10}" fill="{MUTED}">{MONTHS[d.month - 1]}</text>')
            last_month = d.month
        out.append(
            f'<rect class="d" style="animation-delay:{(col + row) * 18}ms" x="{x}" y="{y}" '
            f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}"><title>{d}: {n}</title></rect>'
        )

    total = sum(n for _, _, n in days)
    current, longest = streaks(days)
    best = max(days, key=lambda t: t[2])
    foot = TOP + 7 * PITCH + 30
    out.append(
        f'<text x="{left}" y="{foot}" fill="{FG}" font-size="12">{total:,} contributions in the last year'
        f'<tspan fill="{MUTED}">  ·  streak {current}d  ·  longest {longest}d  ·  best day {best[2]}</tspan></text>'
    )
    lx = left + weeks * PITCH - (PITCH - CELL) - 5 * PITCH - 40
    out.append(f'<text x="{lx - 6}" y="{foot}" fill="{MUTED}" text-anchor="end">Less</text>')
    for k, color in enumerate(PALETTE):
        out.append(f'<rect x="{lx + k * PITCH}" y="{foot - 10}" width="{CELL}" height="{CELL}" rx="3" fill="{color}"/>')
    out.append(f'<text x="{lx + 5 * PITCH + 4}" y="{foot}" fill="{MUTED}">More</text>')
    out.append("</svg>")
    return "\n".join(out)


def check():
    html = (
        '<td data-date="2026-01-02" id="contribution-day-component-0-1" data-level="2">'
        '<td data-date="2026-01-01" id="contribution-day-component-0-0" data-level="0">'
        '<td data-date="2026-01-03" id="contribution-day-component-0-2" data-level="0">'
        '<tool-tip for="contribution-day-component-0-1" class="x">1,204 contributions on January 2nd.</tool-tip>'
        '<tool-tip for="contribution-day-component-0-0" class="x">No contributions on January 1st.</tool-tip>'
    )
    days = parse(html)
    assert [n for _, _, n in days] == [0, 1204, 0], days
    assert streaks(days) == (1, 1), streaks(days)
    assert render(days).count('class="d"') == 3


if __name__ == "__main__":
    check()
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"})
    days = parse(urllib.request.urlopen(req, timeout=30).read().decode())
    if len(days) < 300:
        sys.exit(f"only {len(days)} days parsed, GitHub markup probably changed; keeping old SVG")
    OUT.write_text(render(days))
    print(f"wrote {OUT.name}: {len(days)} days, {sum(n for _, _, n in days)} contributions")
