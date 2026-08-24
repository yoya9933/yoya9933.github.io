#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf _site
mkdir -p _site/assets/projects/snapshots

# Publish only explicit site inputs. Source files, repo metadata and stale build
# directories never enter the Pages artifact.
cp index.html 404.html CNAME robots.txt sitemap.xml site.webmanifest _site/
cp -R en projects contact _site/
cp assets/styles.css assets/p1.css assets/main.js assets/favicon.svg assets/og-image.svg assets/buoy-ui.svg assets/avatar-fallback.svg _site/assets/

# Deterministic local image pipeline: every published input is tracked in this repo.
rsvg-convert -w 1200 -h 630 assets/og-image.svg -o _site/assets/og-image.png
rsvg-convert -w 180 -h 180 assets/favicon.svg -o _site/assets/apple-touch-icon.png
rsvg-convert -w 192 -h 192 assets/favicon.svg -o _site/assets/icon-192.png
rsvg-convert -w 512 -h 512 assets/favicon.svg -o _site/assets/icon-512.png

# Publish frozen real product captures under a cache-busting path. Keep the old
# filenames as compatibility aliases for case-study pages and older links.
for project in buoy chess ncku-return-os; do
  test -s "assets/projects/snapshots/${project}.webp"
  cp "assets/projects/snapshots/${project}.webp" "_site/assets/projects/snapshots/${project}.webp"
  cp "assets/projects/snapshots/${project}.webp" "_site/assets/projects/${project}.webp"
done

# Preserve the P2/P3 build hardening while using the previous visual layout.
python3 scripts/normalize_publish_copy.py
python3 scripts/enhance_site.py
python3 scripts/fix_locale_links.py
python3 scripts/enhance_runtime.py

# CV has one source of truth: tracked HTML -> generated PDF artifact.
qrencode -o /tmp/portfolio-qr.png -s 8 'https://yoya9933.page/'
python3 scripts/prepare_cv_html.py
google-chrome --headless=new --no-sandbox --disable-gpu \
  --print-to-pdf=/tmp/Yoya_CV.pdf --no-pdf-header-footer \
  file:///tmp/Yoya_CV_print.html >/dev/null 2>&1
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
  -dNOPAUSE -dQUIET -dBATCH -dDetectDuplicateImages=true -dCompressFonts=true \
  -sOutputFile=_site/assets/Yoya_CV.pdf /tmp/Yoya_CV.pdf

test ! -e _site/dist
test ! -e _site/assets/Yoya_CV_source.html
python3 scripts/check_p2.py
python3 scripts/check_p3.py

echo "Built allowlisted site at $ROOT/_site"
