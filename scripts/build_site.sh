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

# Project slugs come from one manifest. Adding/removing a portfolio project no longer
# requires editing this deployment script.
mapfile -t PROJECT_SLUGS < <(python3 - <<'PY'
import json
from pathlib import Path
for project in json.loads(Path('data/projects.json').read_text(encoding='utf-8'))['projects']:
    print(project['slug'])
PY
)
for project in "${PROJECT_SLUGS[@]}"; do
  cp -R "projects/$project" "_site/projects/$project"
  cp -R "en/projects/$project" "_site/en/projects/$project"
done

cp -R demos/event-checkin _site/demos/
cp assets/styles.css assets/portfolio-extra.css assets/main.js assets/favicon.svg assets/og-image.svg assets/buoy-ui.svg assets/avatar-fallback.svg _site/assets/
# p1.css is the deployed component bundle; the second source module contains stable
# portfolio-specific layout rules instead of one-off fix files.
cat assets/p1.css assets/portfolio-layout.css > _site/assets/p1.css

# Social and app icons.
rsvg-convert -w 1200 -h 630 assets/og-image.svg -o _site/assets/og-image.png
rsvg-convert -w 180 -h 180 assets/favicon.svg -o _site/assets/apple-touch-icon.png
rsvg-convert -w 192 -h 192 assets/favicon.svg -o _site/assets/icon-192.png
rsvg-convert -w 512 -h 512 assets/favicon.svg -o _site/assets/icon-512.png

# data/projects.json owns each project's public media build plan.
python3 scripts/build_project_media.py

# The project manifest drives homepage sections, project links/visuals, structured data
# and standardized evidence-based Case Study framing.
python3 scripts/render_projects.py
python3 scripts/render_case_studies.py
python3 scripts/check_case_studies.py

# Generic site hardening stays separate from project data.
python3 scripts/enhance_site.py
python3 scripts/fix_locale_links.py
python3 scripts/enhance_runtime.py

# CHANGELOG.md is the source for the public version history page.
python3 scripts/render_changelog.py

# VERSION is the single source of truth for human-readable and machine-readable site version data.
python3 scripts/render_version.py

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
