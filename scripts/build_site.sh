#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf _site
mkdir -p _site/assets/projects/snapshots _site/projects _site/en/projects _site/demos

# Publish only explicit, privacy-reviewed site inputs.
cp index.html 404.html CNAME robots.txt sitemap.xml site.webmanifest _site/
cp -R contact _site/
cp en/index.html _site/en/
cp -R en/contact _site/en/
for project in buoy chess event-checkin ai-media-pipeline; do
  cp -R "projects/$project" "_site/projects/$project"
  cp -R "en/projects/$project" "_site/en/projects/$project"
done
cp -R demos/event-checkin _site/demos/
cp assets/styles.css assets/p1.css assets/portfolio-extra.css assets/main.js assets/favicon.svg assets/og-image.svg assets/buoy-ui.svg assets/avatar-fallback.svg _site/assets/

# Social and app icons.
rsvg-convert -w 1200 -h 630 assets/og-image.svg -o _site/assets/og-image.png
rsvg-convert -w 180 -h 180 assets/favicon.svg -o _site/assets/apple-touch-icon.png
rsvg-convert -w 192 -h 192 assets/favicon.svg -o _site/assets/icon-192.png
rsvg-convert -w 512 -h 512 assets/favicon.svg -o _site/assets/icon-512.png

# Frozen captures for public projects already reviewed and tracked in this repo.
for project in buoy chess; do
  test -s "assets/projects/snapshots/${project}.webp"
  cp "assets/projects/snapshots/${project}.webp" "_site/assets/projects/snapshots/${project}.webp"
  cp "assets/projects/snapshots/${project}.webp" "_site/assets/projects/${project}.webp"
  dwebp "assets/projects/snapshots/${project}.webp" -o "_site/assets/projects/${project}.png" >/dev/null
 done

# Capture the privacy-safe interactive EventOps demo with synthetic data only.
google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --run-all-compositor-stages-before-draw --virtual-time-budget=3500 \
  --window-size=1440,810 --screenshot=/tmp/event-checkin.png \
  "file://${ROOT}/_site/demos/event-checkin/index.html" >/dev/null 2>&1
cwebp -quiet -q 84 /tmp/event-checkin.png -o _site/assets/projects/snapshots/event-checkin.webp
cp _site/assets/projects/snapshots/event-checkin.webp _site/assets/projects/event-checkin.webp
cp /tmp/event-checkin.png _site/assets/projects/event-checkin.png

# Deterministic architecture visual for the AI media operations case study.
rsvg-convert -w 1200 -h 675 assets/projects/ai-media-pipeline.svg -o _site/assets/projects/ai-media-pipeline.png
cwebp -quiet -q 86 _site/assets/projects/ai-media-pipeline.png -o _site/assets/projects/snapshots/ai-media-pipeline.webp
cp _site/assets/projects/snapshots/ai-media-pipeline.webp _site/assets/projects/ai-media-pipeline.webp

# Preserve the established layout while hardening metadata, links and runtime behavior.
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
test ! -e _site/projects/ncku-return-os
test ! -e _site/en/projects/ncku-return-os
python3 scripts/check_p2.py
python3 scripts/check_p3.py

echo "Built privacy-reviewed site at $ROOT/_site"
