from pathlib import Path
import re

site = Path(__file__).resolve().parents[1] / "_site"
errors: list[str] = []

required = [
    "index.html",
    "en/index.html",
    "contact/index.html",
    "en/contact/index.html",
    "projects/buoy/index.html",
    "projects/chess/index.html",
    "projects/event-checkin/index.html",
    "projects/ai-media-pipeline/index.html",
    "en/projects/buoy/index.html",
    "en/projects/chess/index.html",
    "en/projects/event-checkin/index.html",
    "en/projects/ai-media-pipeline/index.html",
]

for rel in required:
    path = site / rel
    if not path.exists():
        errors.append(f"missing P2 output: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    for token in ('hreflang="x-default"', 'property="og:url"', 'property="og:locale"', 'name="twitter:title"', 'name="twitter:description"', 'name="twitter:image"'):
        if token not in text:
            errors.append(f"{rel}: missing {token}")
    if 'class="skip-link"' not in text or not re.search(r'<main\b[^>]*id="main"', text, re.I):
        errors.append(f"{rel}: missing skip-link/main target")
    for tag in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', text, re.I):
        if 'noopener' not in tag or 'noreferrer' not in tag:
            errors.append(f"{rel}: unsafe target=_blank link")
    for tag in re.findall(r'<img\b[^>]+assets/projects/[^>]+>', text, re.I):
        if 'width="1200"' not in tag or 'height="720"' not in tag:
            errors.append(f"{rel}: project image missing intrinsic dimensions")

project_pages = [
    "projects/buoy/index.html", "projects/chess/index.html", "projects/event-checkin/index.html", "projects/ai-media-pipeline/index.html",
    "en/projects/buoy/index.html", "en/projects/chess/index.html", "en/projects/event-checkin/index.html", "en/projects/ai-media-pipeline/index.html",
]
for rel in project_pages:
    text = (site / rel).read_text(encoding="utf-8")
    if '"@type":"CreativeWork"' not in text or '"@type":"BreadcrumbList"' not in text:
        errors.append(f"{rel}: missing project structured data")

sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
for url in (
    "https://yoya9933.page/en/contact/",
    "https://yoya9933.page/projects/event-checkin/",
    "https://yoya9933.page/en/projects/event-checkin/",
    "https://yoya9933.page/projects/ai-media-pipeline/",
    "https://yoya9933.page/en/projects/ai-media-pipeline/",
    "https://yoya9933.page/demos/event-checkin/",
):
    if url not in sitemap:
        errors.append(f"sitemap missing {url}")
if "ncku-return-os" in sitemap:
    errors.append("sitemap still contains retired credit-map project")

if errors:
    print("P2 checks failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("P2 SEO/accessibility checks passed")
