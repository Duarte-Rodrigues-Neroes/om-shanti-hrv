"""Last gate before the report becomes public.

Refuses a ``docs/index.html`` that still carries real band identifiers or
session dates. Exits non-zero so CI blocks the deploy.

**Scope matters more than the patterns.** The page inlines a minified Plotly
bundle and base64 font blobs, which contain arbitrary byte sequences: a naive
scan of the whole file matches dates like ``2016-10-13`` inside the library and
blocks a perfectly clean report. So the check runs against exactly two things -
the authored prose, and the structured JSON data island - and never the
vendored assets.

Usage:
    python tools/check_publishable.py [docs/index.html]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BAND_ID = re.compile(r"\bHM\d{2,}\b")
ISO_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
ISLAND = re.compile(
    r'<script id="bundle" type="application/json">(.*?)</script>', re.S
)


def check(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    problems: list[str] = []

    match = ISLAND.search(html)
    if not match:
        return ["nao encontrei o bloco de dados JSON no relatorio"]
    bundle = json.loads(match.group(1))

    mode = bundle.get("publish_mode")
    if mode == "full":
        problems.append(
            "gerado em --publish-mode full: contem series RR individuais"
        )

    # The authored prose: everything before the first vendored <script>.
    prose = html.split("<script>", 1)[0]
    for label, text in (("texto da pagina", prose), ("dados embebidos", match.group(1))):
        ids = sorted(set(BAND_ID.findall(text)))
        if ids:
            problems.append(f"{label}: identificadores de banda reais {ids}")

    if mode == "anonymous":
        # generated_at is the report's own timestamp and may stay; anything else
        # is a session date and must not.
        generated = str(bundle.get("generated_at", ""))[:10]
        dates = sorted(set(ISO_DATE.findall(match.group(1))) - {generated})
        if dates:
            problems.append(f"dados embebidos: datas de sessao {dates}")
        prose_dates = sorted(set(ISO_DATE.findall(prose)) - {generated})
        if prose_dates:
            problems.append(f"texto da pagina: datas de sessao {prose_dates}")

    beats = sum(
        len(r.get("tacogram", {}).get("rr_ms", []))
        + len(r.get("tacogram", {}).get("rr_raw_ms", []))
        + len(r.get("excerpt", {}).get("rr_ms", []))
        for r in bundle.get("recordings", [])
    )
    if mode in ("aggregate", "anonymous") and beats:
        problems.append(f"{beats} pontos RR batimento-a-batimento embebidos")

    return problems


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/index.html")
    if not path.exists():
        print(f"ERRO: {path} nao existe")
        return 1

    problems = check(path)
    if problems:
        print("DEPLOY BLOQUEADO:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"{path} verificado: sem identificadores reais, datas ou RR individual.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
