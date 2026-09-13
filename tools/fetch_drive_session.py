"""Mirror the shared Drive session folder into ``data/sessao/``.

The folder is link-shared, so every file is reachable unauthenticated through
``drive.usercontent.google.com/download``. That avoids the OAuth client's
``drive.file`` scope limitation entirely and costs one HTTP GET per file.

File ids were enumerated from the Drive folder tree. They are listed explicitly
rather than discovered, because listing a folder *does* require auth.

Usage:
    python tools/fetch_drive_session.py [--skip-ecg]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

DEST_ROOT = Path("data/sessao")
DOWNLOAD_URL = "https://drive.usercontent.google.com/download"

# (band, date, measurement, filename, drive_file_id)
FILES: list[tuple[str, str, str, str, str]] = [
    # --- HM13, 2026-09-11 (short run, then the long one) ---
    ("HM13", "2026-09-11", "livre_1h", "rr_intervals.csv", "1aGfQd5iTJ4W_-o89Tmm9Lu2U3tM0aheI"),
    ("HM13", "2026-09-11", "livre_1h", "metrics.json", "1F2i5sLCW8UDtNwR3O83w0pKgKetwX8y9"),
    ("HM13", "2026-09-11", "livre_1h", "ecg_raw.csv", "1cCVOjGbBN2Sm0w-TOWjt0Rar3Hix1QyE"),
    ("HM13", "2026-09-11", "livre_1h_2", "rr_intervals.csv", "1hftqBnCwIATz84wWEFPaHkUO4YkL90NI"),
    ("HM13", "2026-09-11", "livre_1h_2", "metrics.json", "1sY_EnMqy1-yY-4kfZBlaVEy4lyvSw6QF"),
    ("HM13", "2026-09-11", "livre_1h_2", "ecg_raw.csv", "1JkK46pGHbyxp2VsmzEwpxe-tvCFHC4Z8"),
    # --- HM15 ---
    ("HM15", "2026-09-11", "livre_1h", "rr_intervals.csv", "16XBS1PsitZrUJfdHAe-PTtdljmgcMpNF"),
    ("HM15", "2026-09-11", "livre_1h", "metrics.json", "1fp7Bwaxs8Aj9wA1dB7V2O8INa8ZDlqgb"),
    ("HM15", "2026-09-11", "livre_1h", "ecg_raw.csv", "1S6G-nmDKxSdcAqwTczAd-I2FwIS3Lc2K"),
    ("HM15", "2026-09-13", "livre_1h", "rr_intervals.csv", "1sIy4Bo5FpTVZI9UJfCXvN5zuCjjwPmUV"),
    ("HM15", "2026-09-13", "livre_1h", "metrics.json", "1bInWdeJ97Yz4BUbA-hUfaloUgdolKjrb"),
    # --- HM16 ---
    ("HM16", "2026-09-13", "livre_1h", "rr_intervals.csv", "1gj7wHPUqTen03h_IjUFShRhwOGrvDaOW"),
    ("HM16", "2026-09-13", "livre_1h", "metrics.json", "1bWJCuzke4ROtgwLDYR1kQwDkgEj7rQDh"),
    ("HM16", "2026-09-13", "livre_1h", "ecg_raw.csv", "16pnkkA29mgE4ve7PDcIUyoQaEc555Zlb"),
    # --- HM02 (heavy RR dropout) ---
    ("HM02", "2026-09-12", "livre_1h", "rr_intervals.csv", "1yX6dJ1JDeb5fPTtTuagKzmzzCCXkq5s1"),
    ("HM02", "2026-09-12", "livre_1h", "metrics.json", "1dTLA52iOMkR2g2DXG8LhpEt3YXbe_48O"),
    ("HM02", "2026-09-12", "livre_1h", "ecg_raw.csv", "1kk34edMV2GVpejf6xyp8vKa3alMlqvia"),
    # --- HM11 (heavy RR dropout) ---
    ("HM11", "2026-09-12", "livre_1h", "rr_intervals.csv", "1JebvjhPbXHtmgCZqA1Fgy8tRWQ5LTCPY"),
    ("HM11", "2026-09-12", "livre_1h", "metrics.json", "1EZb8jodxzFM6JjYjN_eVzkeNFO9__6tw"),
    ("HM11", "2026-09-12", "livre_1h", "ecg_raw.csv", "1gl0YIw_Lpv1XlfXF5Jn9Qq60QS71jIDk"),
    # --- rest_5min_manha: the only genuinely un-chanted recordings in the set ---
    ("HM01", "2026-09-11", "rest_5min_manha", "rr_intervals.csv", "1xaBkp3nDrqOdlO2q9K6rc-2tTvjDNUJB"),
    ("HM01", "2026-09-11", "rest_5min_manha", "metrics.json", "1Bvn2n0NANKEfOT6oBEyEUIicXbIkPlJE"),
    ("HM01", "2026-09-11", "rest_5min_manha", "ecg_raw.csv", "12WThZmj3XHyvdciIKBECpGa2fbS0TplT"),
    ("HM02", "2026-09-11", "rest_5min_manha", "rr_intervals.csv", "1Vlf2MbzeDCeMNDUIuCsucJj140X9hzHt"),
    ("HM02", "2026-09-11", "rest_5min_manha", "metrics.json", "1zFP7NmjOmNs6PVku0cpknHzrVlaJ-iTr"),
    ("HM02", "2026-09-11", "rest_5min_manha", "ecg_raw.csv", "1XmZIu75zoX7Mz2eL7QxWLzHagM33PVEt"),
    ("HM02", "2026-09-11", "rest_5min_manha_2", "rr_intervals.csv", "1pUGsY4Wrh0KJY30TFgo3FPw6SifE9hEO"),
    ("HM02", "2026-09-11", "rest_5min_manha_2", "metrics.json", "1-38klJaR1-1DyMd226gQeiNVAND2T1DF"),
    ("HM02", "2026-09-11", "rest_5min_manha_2", "ecg_raw.csv", "1xudYnq5OF-VaJb1WzD2kz2y67ACevOj-"),
    ("HM07", "2026-09-11", "rest_5min_manha", "rr_intervals.csv", "1NhOpz4wN7NvwDWOFiI4F8DCJIsSrPOMW"),
    ("HM07", "2026-09-11", "rest_5min_manha", "metrics.json", "1n67wZ3jHtNdnoGWx2jAcx6QcMBGC9cbN"),
    ("HM07", "2026-09-11", "rest_5min_manha", "ecg_raw.csv", "1HhnjSO5kOrZu2uLBTtEQWcDJamwmpf4B"),
    ("HM09", "2026-09-11", "rest_5min_manha", "rr_intervals.csv", "1lqAwLr_ZposB5H70KjnHREzo7V334wUt"),
    ("HM09", "2026-09-11", "rest_5min_manha", "metrics.json", "1h_KosNI9caaeIRBu3-mV1tAXGi2yoBGx"),
    ("HM09", "2026-09-11", "rest_5min_manha", "ecg_raw.csv", "1_XfE9nuFapbO4hRcF7g2OHJa-Ya0dU5C"),
    ("HM15", "2026-09-13", "rest_5min_manha", "rr_intervals.csv", "1QFkAkby2-ywkWo8K4jhWnp1I2MvhtXRy"),
    ("HM15", "2026-09-13", "rest_5min_manha", "metrics.json", "1JMFytns8P_0CkalO4Dl7ZK930-OGHZuI"),
    ("HM15", "2026-09-13", "rest_5min_manha", "ecg_raw.csv", "1GQMw5zytVW_SzToba7X24rDclkwrw5Nk"),
]


def fetch(file_id: str, dest: Path, session: requests.Session) -> int:
    """Download one link-shared Drive file, handling the large-file warning."""
    response = session.get(
        DOWNLOAD_URL, params={"id": file_id, "export": "download"}, timeout=120
    )
    response.raise_for_status()

    # Files over ~100 MB return an HTML interstitial; ours are far smaller, but
    # fail loudly rather than writing a web page to a .csv.
    head = response.content[:200].lstrip()
    if head.startswith(b"<!DOCTYPE") or head.startswith(b"<html"):
        raise RuntimeError(f"{dest.name}: got HTML, not file content (id={file_id})")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    return len(response.content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-ecg", action="store_true", help="RR and metadata only (much faster)"
    )
    args = parser.parse_args()

    session = requests.Session()
    failures: list[str] = []
    total = 0

    for band, date, measurement, filename, file_id in FILES:
        if args.skip_ecg and filename == "ecg_raw.csv":
            continue
        dest = DEST_ROOT / band / date / measurement / filename
        label = f"{band}/{date}/{measurement}/{filename}"
        try:
            written = fetch(file_id, dest, session)
        except Exception as exc:  # one bad file must not stop the mirror
            print(f"  FALHOU  {label}: {exc}")
            failures.append(label)
            continue
        total += written
        print(f"  ok      {label}  ({written:,} bytes)")

    print(f"\n{total:,} bytes em {DEST_ROOT}")
    if failures:
        print(f"{len(failures)} ficheiro(s) falharam:")
        for item in failures:
            print(f"  - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
