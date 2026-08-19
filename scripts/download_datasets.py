"""Download publicly accessible dataset archives without committing dataset files.

Sources requiring authentication or manual terms acceptance are reported with
instructions instead of being silently substituted.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import PROJECT_ROOT


SOURCES = {
    "nazario": (
        "http://monkey.org/~jose/phishing/phishing-2024",
        PROJECT_ROOT / "data" / "raw" / "nazario" / "phishing-2024",
    ),
    "phiusiil": (
        "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip",
        PROJECT_ROOT / "data" / "raw" / "phiusiil" / "phiusiil.zip",
    ),
}


def download(name: str) -> Path:
    if name not in SOURCES:
        raise ValueError(f"Unsupported automatic source: {name}")
    url, destination = SOURCES[name]
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {name} from {url}")
    with urllib.request.urlopen(url, timeout=60) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    print(f"Saved {destination}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=["nazario", "phiusiil"])
    args = parser.parse_args()
    download(args.source)


if __name__ == "__main__":
    main()