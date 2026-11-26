"""Draw the GitHub contribution calendar as a star map (dark + light SVG).

    GITHUB_TOKEN=... python3 scripts/commit_stars.py [out_dir]   (default: dist/)

Runs daily in .github/workflows/commit-stars.yml. Each day is a star: brighter and
bigger on busier days (relative to the year's max), faint dots on quiet days, and thin
constellation lines between consecutive heavy days. Same idea as "Commits, as stars"
on samandareo.uz. Stdlib only. Exits non-zero (writing nothing) if the API call fails,
so a bad run never replaces a good image.
"""

import hashlib
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

LOGIN = os.environ.get("GH_LOGIN", "samandareo")
W, PAD_X, TOP, ROWS_H = 1000, 24, 20, 150
H = TOP + ROWS_H + 46

THEMES = {
    "dark": {"bg": "#0A0A0A", "star": "#EDEDED", "text": "#8F8F8F", "strong": "#EDEDED"},
    "light": {"bg": "#FFFFFF", "star": "#1F2328", "text": "#59636E", "strong": "#1F2328"},
}
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { totalContributions weeks { contributionDays { date contributionCount weekday } } } } } }"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "commit-stars"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors'][0].get('message')}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def unit(s: str) -> float:
    """Stable pseudo-random number in [0, 1) from a string (so stars don't jump between runs)."""
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def svg(cal, theme):
    t = THEMES[theme]
    weeks = cal["weeks"]
    cols = len(weeks)
    cw, ch = (W - 2 * PAD_X) / cols, ROWS_H / 7
    days = []
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            r = d["weekday"]
            x = PAD_X + cw * (c + 0.5) + (unit(d["date"] + "x") - 0.5) * cw * 0.4
            y = TOP + ch * (r + 0.5) + (unit(d["date"] + "y") - 0.5) * ch * 0.4
            days.append({**d, "c": c, "x": x, "y": y})
    mx = max((d["contributionCount"] for d in days), default=0) or 1
    heavy = max(2, 0.6 * mx)

    lines = []
    for a, b in zip(days, days[1:]):
        if a["contributionCount"] >= heavy and b["contributionCount"] >= heavy:
            lines.append(f'<line x1="{a["x"]:.1f}" y1="{a["y"]:.1f}" x2="{b["x"]:.1f}" y2="{b["y"]:.1f}" '
                         f'style="animation-delay:{0.9 + b["c"] * 0.03:.2f}s"/>')

    nodes = []
    for d in days:
        n = d["contributionCount"]
        delay = 0.9 + d["c"] * 0.03
        if n == 0:
            nodes.append(f'<circle class="q" cx="{d["x"]:.1f}" cy="{d["y"]:.1f}" r="0.9" style="animation-delay:{delay:.2f}s"/>')
            continue
        lvl = min(n, mx) / mx
        o = 0.35 + 0.6 * lvl
        tw = 3 + unit(d["date"] + "t") * 4
        nodes.append(
            f'<circle class="a" cx="{d["x"]:.1f}" cy="{d["y"]:.1f}" r="{1.0 + lvl * 2.2:.2f}" '
            f'style="--o:{o:.2f};animation-delay:{delay:.2f}s,{delay + 0.6 + unit(d["date"]) * 3:.2f}s;'
            f'animation-duration:.6s,{tw:.2f}s"><title>{n} contributions · {d["date"]}</title></circle>'
        )

    total = cal["totalContributions"]
    today = date.today().isoformat()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} GitHub contributions in the last year, drawn as a star map">
  <style>
    .a {{ fill: {t['star']}; opacity: 0; animation-name: in, tw; animation-fill-mode: forwards, none; animation-iteration-count: 1, infinite; animation-timing-function: ease-out, ease-in-out; }}
    .q {{ fill: {t['star']}; opacity: 0; animation: inq .6s ease-out forwards; }}
    line {{ stroke: {t['star']}; stroke-width: .7; opacity: 0; animation: inl .8s ease-out forwards; }}
    @keyframes in {{ to {{ opacity: var(--o); }} }}
    @keyframes inq {{ to {{ opacity: .12; }} }}
    @keyframes inl {{ to {{ opacity: .2; }} }}
    @keyframes tw {{ 0%, 100% {{ opacity: var(--o); }} 50% {{ opacity: calc(var(--o) * .45); }} }}
    @media (prefers-reduced-motion: reduce) {{
      .a {{ animation: none; opacity: var(--o); }} .q {{ animation: none; opacity: .12; }} line {{ animation: none; opacity: .2; }}
    }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
  <g>{''.join(lines)}</g>
  <g>{''.join(nodes)}</g>
  <text x="{PAD_X}" y="{H - 18}" font-family="{MONO}" font-size="13" fill="{t['text']}"><tspan fill="{t['strong']}">{total:,}</tspan> contributions in the last year</text>
  <text x="{W - PAD_X}" y="{H - 18}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t['text']}">updated {today}</text>
</svg>
"""


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    cal = fetch()
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (out / f"commit-stars-{theme}.svg").write_text(svg(cal, theme))
    print(f"{cal['totalContributions']} contributions → {out}/commit-stars-{{dark,light}}.svg")


if __name__ == "__main__":
    main()
