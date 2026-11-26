"""Generate the stack as a small solar system (dark + light SVG).

    python3 scripts/orbit.py      -> assets/orbit-dark.svg, assets/orbit-light.svg

Python is the sun; four tilted rings (ai, backend, data & infra, frontend & tools) carry the
technologies around it. Planets dim at the back of a ring and brighten at the front, so it reads
as depth. Same idea as /stack on samandareo.uz. SMIL animation (works in GitHub image views).
Only list technologies confirmed in content.yaml. Stdlib only.
"""

from pathlib import Path

W, H = 1000, 470
CX, CY = 500, 236
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": {"bg": "#0A0A0A", "strong": "#FFFFFF", "planet": "#EDEDED", "text": "#A1A1A1",
             "muted": "#8F8F8F", "ring": "#EDEDED", "glow": "#FFFFFF"},
    "light": {"bg": "#FFFFFF", "strong": "#1F2328", "planet": "#1F2328", "text": "#59636E",
              "muted": "#59636E", "ring": "#1F2328", "glow": "#1F2328"},
}
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# (name, rx, ry, seconds per lap, technologies)
RINGS = [
    ("ai", 130, 48, 46, ["openai", "anthropic", "litellm", "mcp", "rag", "agents sdk", "transformers"]),
    ("backend", 220, 82, 70, ["fastapi", "temporal", "kafka", "node.js", "grpc", "rabbitmq", "nats", "socket.io"]),
    ("data & infra", 310, 118, 98, ["postgres", "pgvector", "mongodb", "clickhouse", "redis", "elasticsearch",
                                    "docker", "aws", "cloudflare"]),
    ("frontend & tools", 395, 156, 132, ["typescript", "react", "next.js", "react native", "flutter", "tailwind",
                                         "figma", "github actions", "claude code", "cursor"]),
]


def ellipse(rx, ry):
    return f"M{CX - rx} {CY} a{rx} {ry} 0 1 1 {2 * rx} 0 a{rx} {ry} 0 1 1 {-2 * rx} 0"


def svg(theme: str) -> str:
    t = THEMES[theme]
    rings, planets = [], []
    for ri, (label, rx, ry, dur, techs) in enumerate(RINGS):
        d = ellipse(rx, ry)
        rings.append(f'<path d="{d}" fill="none" stroke="{t["ring"]}" stroke-opacity=".13" '
                     f'stroke-dasharray="{"2 5" if ri % 2 else "none"}"/>')
        n = len(techs)
        for i, tech in enumerate(techs):
            begin = f"-{dur * i / n:.2f}s"
            # path starts at the left and sweeps over the top (back) first, then the bottom (front)
            planets.append(f"""  <g opacity=".7">
    <animateMotion dur="{dur}s" begin="{begin}" repeatCount="indefinite" path="{d}" calcMode="linear"/>
    <animate attributeName="opacity" dur="{dur}s" begin="{begin}" repeatCount="indefinite"
      values=".62;.28;.62;1;.62" keyTimes="0;.25;.5;.75;1"/>
    <circle r="{2.6 if ri < 2 else 2.2}" fill="{t['planet']}"/>
    <text x="7" y="4" font-family="{MONO}" font-size="12" fill="{t['planet']}">{tech}</text>
  </g>""")
    legend = "".join(
        f'<text x="24" y="{H - 66 + 16 * i}" font-family="{MONO}" font-size="11" fill="{t["muted"]}">'
        f'<tspan fill="{t["text"]}">{i + 1}</tspan> {label.replace('&', '&amp;')}</text>'
        for i, (label, *_rest) in enumerate(RINGS)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Tech stack drawn as a solar system: Python at the centre, with AI, backend, data and infra, and frontend rings">
  <defs><radialGradient id="sun{theme}">
    <stop offset="0" stop-color="{t['glow']}" stop-opacity=".35"/><stop offset="1" stop-color="{t['glow']}" stop-opacity="0"/>
  </radialGradient></defs>
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
  <text x="24" y="34" font-family="{MONO}" font-size="12" fill="{t['muted']}">~ $ stack --orbit</text>
  {''.join(rings)}
  <circle cx="{CX}" cy="{CY}" r="46" fill="url(#sun{theme})">
    <animate attributeName="r" values="40;50;40" dur="6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{CX}" cy="{CY}" r="7" fill="{t['strong']}"/>
  <text x="{CX}" y="{CY + 26}" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="600" fill="{t['strong']}">python</text>
{chr(10).join(planets)}
  {legend}
  <text x="{W - 24}" y="{H - 18}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t['muted']}">full map · samandareo.uz/stack</text>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"orbit-{theme}.svg").write_text(svg(theme))
        print(f"wrote assets/orbit-{theme}.svg")


if __name__ == "__main__":
    main()
