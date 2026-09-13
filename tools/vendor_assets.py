"""Fetch the third-party assets the report embeds. Run once; needs network.

Everything the report needs is inlined into a single HTML file so it opens by
double-click with no network, no CDN and no fetch() that a browser would block
on a ``file://`` origin. This script is the only step that touches the network,
and its output is committed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import requests

VENDOR = Path("polarmed/report/assets")

# Partial Plotly build: scatter and heatmap only, roughly a third the size of
# the full bundle and all this report draws.
PLOTLY_URL = "https://cdn.plot.ly/plotly-basic-2.35.2.min.js"

# Brand faces, latin subset only. The CSS endpoint returns @font-face rules
# whose src URLs we follow to the actual woff2 files.
FONT_CSS = (
    "https://fonts.googleapis.com/css2"
    "?family=Sora:wght@300;400;500;600"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Newsreader:ital,wght@1,400"
    "&display=swap"
)
# A modern UA gets woff2; without it Google serves ttf.
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}


def main() -> int:
    VENDOR.mkdir(parents=True, exist_ok=True)

    print("plotly...")
    response = requests.get(PLOTLY_URL, timeout=180)
    response.raise_for_status()
    (VENDOR / "plotly.min.js").write_bytes(response.content)
    print(f"  plotly.min.js  {len(response.content):,} bytes")

    print("fontes...")
    css = requests.get(FONT_CSS, headers=UA, timeout=60)
    css.raise_for_status()
    text = css.text

    # Keep only the latin blocks: the full set includes cyrillic and greek,
    # which would more than double the embedded weight for nothing.
    blocks = re.findall(r"/\*\s*([\w\-\[\]]+)\s*\*/\s*(@font-face\s*\{[^}]+\})", text)
    kept = [b for name, b in blocks if name in ("latin", "latin-ext")]
    if not kept:
        kept = re.findall(r"@font-face\s*\{[^}]+\}", text)

    out: list[str] = []
    for block in kept:
        match = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if not match:
            continue
        url = match.group(1)
        font = requests.get(url, headers=UA, timeout=60)
        font.raise_for_status()
        import base64

        encoded = base64.b64encode(font.content).decode("ascii")
        out.append(
            block.replace(
                match.group(0), f"url(data:font/woff2;base64,{encoded}) format('woff2')"
            )
        )
        family = re.search(r"font-family:\s*'([^']+)'", block)
        print(f"  {family.group(1) if family else '?':16s} {len(font.content):,} bytes")

    css_path = VENDOR / "fonts.css"
    css_path.write_text("\n".join(out), encoding="utf-8")
    print(f"  fonts.css      {css_path.stat().st_size:,} bytes ({len(out)} faces)")

    print("logo...")
    logo = Path("reference/assets/neroes-lockup-dark.png")
    if logo.exists():
        import base64

        encoded = base64.b64encode(logo.read_bytes()).decode("ascii")
        (VENDOR / "logo.txt").write_text(
            f"data:image/png;base64,{encoded}", encoding="utf-8"
        )
        print(f"  logo.txt       {len(encoded):,} chars")
    else:
        print("  AVISO: reference/assets/neroes-lockup-dark.png nao encontrado")

    return 0


if __name__ == "__main__":
    sys.exit(main())
