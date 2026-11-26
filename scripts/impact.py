"""Generate the "numbers" strip (dark + light SVG).

    python3 scripts/impact.py      -> assets/impact-dark.svg, assets/impact-light.svg

Four real results from work, big mono numbers that rise in one after another.
Keep these in sync with content.yaml in the cv-hub repo. Stdlib only.
"""

from pathlib import Path

W, H = 1000, 132
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {"bg": "#0A0A0A", "strong": "#FFFFFF", "text": "#A1A1A1", "muted": "#8F8F8F", "line": "#262626"},
    "light": {"bg": "#FFFFFF", "strong": "#1F2328", "text": "#59636E", "muted": "#59636E", "line": "#D1D9E0"},
}
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# (number, line 1, line 2)
STATS = [
    ("84%", "faster network workflow", "350 → 55 min · temporal"),
    ("10k+", "alerts a day correlated", "embeddings + llm grouping"),
    ("95%", "lower api latency", "10s → 200ms · 3.5m-row mysql"),
    ("12h", "agent runs, durable", "mcp tools · temporal workers"),
]


def svg(theme: str) -> str:
    t = THEMES[theme]
    cw = (W - 48) / len(STATS)
    cells = []
    for i, (num, l1, l2) in enumerate(STATS):
        x = 24 + cw * i + 22
        sep = "" if i == 0 else f'<line x1="{24 + cw * i:.0f}" y1="30" x2="{24 + cw * i:.0f}" y2="102" stroke="{t["line"]}"/>'
        cells.append(f"""  {sep}
  <g class="r" style="animation-delay:{0.15 + i * 0.18:.2f}s">
    <text x="{x:.0f}" y="66" font-family="{MONO}" font-size="36" font-weight="600" letter-spacing="-1" fill="{t['strong']}">{num}</text>
    <text x="{x:.0f}" y="90" font-family="{SANS}" font-size="14" fill="{t['text']}">{l1}</text>
    <text x="{x:.0f}" y="108" font-family="{MONO}" font-size="11.5" fill="{t['muted']}">{l2}</text>
  </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="84% faster network workflow, 10k+ alerts a day correlated, 95% lower API latency, 12-hour durable agent runs">
  <style>
    .r {{ opacity: 0; animation: rise .9s cubic-bezier(.2,.7,.2,1) forwards; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: reduce) {{ .r {{ animation: none; opacity: 1; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
{''.join(cells)}
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"impact-{theme}.svg").write_text(svg(theme))
        print(f"wrote assets/impact-{theme}.svg")


if __name__ == "__main__":
    main()
