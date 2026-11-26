"""Generate the animated profile header (dark + light) as SVG.

    python3 scripts/header.py      -> assets/header-dark.svg, assets/header-light.svg

Same look as samandareo.uz: a quiet twinkling starfield, the name, the role,
a `~ $ whoami` line that types and deletes a few phrases,
the odd shooting star, and the Ulugh Beg constellation
(drawn as his Fakhri sextant) on the right. Stdlib only.
"""

import random
from pathlib import Path

W, H = 1000, 260
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {"bg": "#0A0A0A", "star": "#EDEDED", "name": "#FFFFFF", "role": "#A1A1A1",
             "muted": "#8F8F8F", "line": "#EDEDED"},
    "light": {"bg": "#FFFFFF", "star": "#1F2328", "name": "#1F2328", "role": "#59636E",
              "muted": "#59636E", "line": "#1F2328"},
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# Ulugh Beg constellation: the Fakhri sextant (same points as the website), placed at the right.
UB_OFFSET = (735, 30)
UB_POINTS = [(40, 20), (67.8, 177.6), (120, 158.6), (162.6, 122.8), (190.4, 74.7)]
UB_PATH = "M40 20 L67.8 177.6 L120 158.6 L162.6 122.8 L190.4 74.7 Z M40 20 L120 158.6 M40 20 L162.6 122.8"

# `$ whoami` types these one after another, deletes them, and loops.
PHRASES = ["llm systems", "ai agents on temporal", "rag pipelines", "backends that scale"]
CH = 9.0                     # monospace advance at 15px (each phrase is pinned with textLength)
TYPE, HOLD, DEL, GAP = 0.075, 1.9, 0.03, 0.35   # seconds per char / hold / per char / pause
PX = 56 + 9 * CH             # phrase x, after "building "

# Shooting stars: (x1, y1, x2, y2, delay, period), kept out of the text block.
SHOOTERS = [(960, 6, 640, 66, 2.5, 11), (560, 4, 330, 52, 7.5, 13)]


def typing_css():
    """CSS keyframes for the typing line: one clip animation per phrase plus the caret."""
    seq, t = [], 0.0
    for i, ph in enumerate(PHRASES):
        n = len(ph)
        for k in range(n + 1):
            seq.append((t, i, k)); t += TYPE
        t += HOLD
        for k in range(n - 1, -1, -1):
            seq.append((t, i, k)); t += DEL
        t += GAP
    total = t
    rules = []
    for i, ph in enumerate(PHRASES):
        n = len(ph)
        frames = [f"0% {{ clip-path: inset(0 {n * CH:.0f}px 0 0); }}"]
        for ts, j, k in seq:
            if j == i:
                frames.append(f"{ts / total * 100:.3f}% {{ clip-path: inset(0 {(n - k) * CH:.0f}px 0 0); }}")
        rules.append(f"@keyframes ty{i} {{ {' '.join(frames)} }}")
        rules.append(f".ph{i} {{ animation: ty{i} {total:.2f}s step-end infinite; }}")
    caret = " ".join(f"{ts / total * 100:.3f}% {{ transform: translateX({k * CH:.0f}px); }}" for ts, _, k in seq)
    rules.append(f"@keyframes cx {{ {caret} }}")
    rules.append(f".cm {{ animation: cx {total:.2f}s step-end infinite; }}")
    return "\n    ".join(rules)


def stars(seed: int):
    rnd = random.Random(seed)
    out = []
    while len(out) < 90:
        x, y = rnd.uniform(8, W - 8), rnd.uniform(8, H - 8)
        # keep the text area and the constellation calm
        if 40 < x < 560 and 70 < y < 232:
            continue
        if 760 < x < 940 and 40 < y < 220:
            continue
        z = rnd.uniform(0.2, 1.0)
        out.append((x, y, rnd.uniform(0.3, 1.2) * z + 0.25, z, rnd.uniform(0, 6), rnd.uniform(3, 7)))
    return out


def svg(theme: str) -> str:
    t = THEMES[theme]
    ox, oy = UB_OFFSET
    star_nodes = "\n".join(
        f'    <circle class="s" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
        f'style="--o:{0.2 + 0.6 * z:.2f};animation-delay:{d:.2f}s;animation-duration:{dur:.2f}s"/>'
        for x, y, r, z, d, dur in stars(seed=2026)
    )
    shooters = "\n".join(
        f'    <line class="shoot" x1="{x1}" y1="{y1}" x2="{x1 + (x2 - x1) * 0.28:.0f}" y2="{y1 + (y2 - y1) * 0.28:.0f}" '
        f'stroke="url(#sg{theme})" stroke-width="1.4" stroke-linecap="round" '
        f'style="--dx:{(x2 - x1) * 0.72:.0f}px;--dy:{(y2 - y1) * 0.72:.0f}px;animation-delay:{d}s;animation-duration:{per}s"/>'
        for x1, y1, x2, y2, d, per in SHOOTERS
    )
    phrases = "".join(
        f'<text class="ph{i}" x="{PX:.0f}" y="214" font-family="{MONO}" font-size="15" fill="{t["name"]}" '
        f'textLength="{len(ph) * CH:.0f}" lengthAdjust="spacingAndGlyphs">{ph}</text>'
        for i, ph in enumerate(PHRASES)
    )
    ub_stars = "\n".join(
        f'    <circle class="ubs" cx="{x}" cy="{y}" r="{r}" style="animation-delay:{d}s"/>'
        for (x, y), r, d in zip(UB_POINTS, [2.6, 1.9, 2.2, 1.8, 2.4], [0, 0.6, 1.4, 0.9, 2.0])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Samandar Abdugafforov — AI &amp; Backend Engineer">
  <style>
    .s {{ fill: {t['star']}; opacity: var(--o); animation: tw ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: var(--o); }} 50% {{ opacity: calc(var(--o) * 0.25); }} }}
    .ubl {{ fill: none; stroke: {t['line']}; stroke-opacity: .3; stroke-width: 1; stroke-dasharray: 420; animation: draw 2.6s .6s ease-out both; }}
    @keyframes draw {{ from {{ stroke-dashoffset: 420; }} to {{ stroke-dashoffset: 0; }} }}
    .ubs {{ fill: {t['name']}; animation: tw2 3.2s ease-in-out infinite; }}
    @keyframes tw2 {{ 0%, 100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
    .caret {{ animation: blink 1s step-end infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    .rise {{ animation: rise .9s cubic-bezier(.2,.7,.2,1) both; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    .shoot {{ opacity: 0; animation: shoot linear infinite; }}
    @keyframes shoot {{ 0% {{ opacity: 0; transform: translate(0, 0); }} 1% {{ opacity: 1; }}
      7% {{ opacity: 0; transform: translate(var(--dx), var(--dy)); }} 100% {{ opacity: 0; transform: translate(var(--dx), var(--dy)); }} }}
    {typing_css()}
    @media (prefers-reduced-motion: reduce) {{
      .s, .ubl, .ubs, .caret, .rise, .shoot, .cm {{ animation: none; }}
      [class^="ph"] {{ animation: none; clip-path: inset(0 100% 0 0); }} .ph0 {{ clip-path: none; }}
      .cm {{ transform: translateX({len(PHRASES[0]) * CH:.0f}px); }}
    }}
  </style>
  <defs><linearGradient id="sg{theme}" x1="1" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t['star']}" stop-opacity="0"/><stop offset="1" stop-color="{t['star']}" stop-opacity=".9"/>
  </linearGradient></defs>
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
  <g>
{star_nodes}
  </g>
{shooters}
  <g class="rise">
    <text x="56" y="112" font-family="{SANS}" font-size="40" font-weight="600" letter-spacing="-0.8" fill="{t['name']}">Samandar Abdugafforov</text>
    <text x="56" y="146" font-family="{SANS}" font-size="18" fill="{t['role']}">AI &amp; Backend Engineer · Tashkent, Uzbekistan</text>
    <text x="56" y="190" font-family="{MONO}" font-size="15" fill="{t['muted']}">~ $ <tspan fill="{t['name']}">whoami</tspan></text>
    <text x="56" y="214" font-family="{MONO}" font-size="15" fill="{t['muted']}">building</text>
    {phrases}
    <g class="cm"><rect class="caret" x="{PX + 1:.0f}" y="201" width="8" height="17" fill="{t['name']}" opacity=".85"/></g>
  </g>
  <g transform="translate({ox} {oy})">
    <path class="ubl" d="{UB_PATH}"/>
{ub_stars}
    <text x="0" y="210" font-family="{MONO}" font-size="11" fill="{t['muted']}">ulugh beg · samarkand, 1420</text>
  </g>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"header-{theme}.svg").write_text(svg(theme))
        print(f"wrote assets/header-{theme}.svg")


if __name__ == "__main__":
    main()
