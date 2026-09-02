from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT / "_site" / "robots.txt"
EXPECTED_SITEMAP = "Sitemap: https://yoya9933.page/sitemap.xml"


def main() -> int:
    if not ROBOTS.is_file():
        print("robots.txt is missing from the deployment artifact", file=sys.stderr)
        return 1

    lines = [line.strip() for line in ROBOTS.read_text(encoding="utf-8").splitlines()]
    active = [line for line in lines if line and not line.startswith("#")]
    required = {"User-agent: *", "Allow: /", EXPECTED_SITEMAP}
    missing = sorted(required.difference(active))
    if missing:
        print("robots.txt validation failed:")
        for item in missing:
            print(f"- missing: {item}")
        return 1
    if any(line.lower() == "disallow: /" for line in active):
        print("robots.txt unexpectedly blocks the whole site", file=sys.stderr)
        return 1

    print("robots.txt checks passed with public sitemap declaration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
