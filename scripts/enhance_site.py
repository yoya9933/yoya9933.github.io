from __future__ import annotations

from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
PROJECT_DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))

PROJECT_BY_REL: dict[str, tuple[dict, str]] = {}
for project in PROJECT_DATA["projects"]:
    PROJECT_BY_REL[f"projects/{project['slug']}/index.html"] = (project, "zh")
    PROJECT_BY_REL[f"en/projects/{project['slug']}/index.html"] = (project, "en")


def attr(text: str, name: str) -> str | None:
    match = re.search(rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"', text, re.I)
    return match.group(1) if match else None


def property_attr(text: str, name: str) -> str | None:
    match = re.search(rf'<meta\s+property="{re.escape(name)}"\s+content="([^"]*)"', text, re.I)
    return match.group(1) if match else None


def canonical(text: str) -> str | None:
    match = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', text, re.I)
    return match.group(1) if match else None


def title(text: str) -> str:
    match = re.search(r'<title>(.*?)</title>', text, re.I | re.S)
    return re.sub(r'\s+', ' ', match.group(1)).strip() if match else "Yoya Portfolio"


def description(text: str) -> str:
    return attr(text, "description") or "Engineering, data and AI portfolio by Yoya."


def add_before_head_end(text: str, fragment: str) -> str:
    return text.replace("</head>", fragment + "</head>", 1)


def ensure_meta(text: str, key: str, value: str, *, prop: bool = False) -> str:
    kind = "property" if prop else "name"
    pattern = rf'<meta\s+{kind}="{re.escape(key)}"\s+content="[^"]*"[^>]*>'
    tag = f'<meta {kind}="{key}" content="{escape(value, quote=True)}">'
    if re.search(pattern, text, re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return add_before_head_end(text, tag)


def ensure_x_default(text: str, href: str) -> str:
    if 'hreflang="x-default"' in text:
        return text
    return add_before_head_end(text, f'<link rel="alternate" hreflang="x-default" href="{escape(href, quote=True)}">')


def harden_blank_links(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r'\brel=', tag, re.I):
            rel_match = re.search(r'rel="([^"]*)"', tag, re.I)
            current = rel_match.group(1).split() if rel_match else []
            for token in ("noopener", "noreferrer"):
                if token not in current:
                    current.append(token)
            return re.sub(r'rel="[^"]*"', f'rel="{" ".join(current)}"', tag, count=1, flags=re.I)
        return tag[:-1] + ' rel="noopener noreferrer">'
    return re.sub(r'<a\b[^>]*target="_blank"[^>]*>', repl, text, flags=re.I)


def ensure_accessibility(text: str) -> str:
    lang = "en" if re.search(r'<html[^>]+lang="en', text, re.I) else "zh"
    label = "Skip to main content" if lang == "en" else "跳到主要內容"
    if 'class="skip-link"' not in text:
        text = re.sub(r'(<body\b[^>]*>)', rf'\1<a class="skip-link" href="#main">{label}</a>', text, count=1, flags=re.I)
    if '<main' in text and not re.search(r'<main\b[^>]*\bid="main"', text, re.I):
        text = re.sub(r'<main(\b[^>]*)>', r'<main id="main"\1>', text, count=1, flags=re.I)
    return text


def ensure_image_dimensions(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'width=' not in tag:
            tag = tag[:-1] + ' width="1200">'
        if 'height=' not in tag:
            tag = tag[:-1] + ' height="720">'
        if 'decoding=' not in tag:
            tag = tag[:-1] + ' decoding="async">'
        return tag
    return re.sub(r'<img\b[^>]+src="[^"]*assets/projects/[^"]+"[^>]*>', repl, text, flags=re.I)


def project_schema(rel: str, text: str, url: str) -> str | None:
    entry = PROJECT_BY_REL.get(rel)
    if not entry:
        return None
    project, locale = entry
    lang = "en" if locale == "en" else "zh-Hant-TW"
    home = "https://yoya9933.page/en/" if locale == "en" else "https://yoya9933.page/"
    work: dict = {
        "@type": "CreativeWork",
        "name": project["title"][locale],
        "url": url,
        "description": description(text),
        "inLanguage": lang,
        "author": {"@type": "Person", "name": "Yoya", "url": "https://yoya9933.page/"},
    }
    if project.get("repo"):
        work["codeRepository"] = project["repo"]
    if project.get("live"):
        work["sameAs"] = [project["live"]]

    data = {
        "@context": "https://schema.org",
        "@graph": [
            work,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Portfolio", "item": home},
                    {"@type": "ListItem", "position": 2, "name": project["title"][locale], "item": url},
                ],
            },
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + '</script>'


def process(path: Path) -> None:
    rel = path.relative_to(SITE).as_posix()
    text = path.read_text(encoding="utf-8")
    if rel == "404.html":
        path.write_text(ensure_accessibility(harden_blank_links(text)), encoding="utf-8")
        return

    if rel == "index.html" and "portfolio-extra.css" not in text:
        text = add_before_head_end(text, '<link rel="stylesheet" href="assets/portfolio-extra.css">')
    elif rel == "en/index.html" and "portfolio-extra.css" not in text:
        text = add_before_head_end(text, '<link rel="stylesheet" href="../assets/portfolio-extra.css">')

    url = canonical(text)
    if url:
        is_en = rel.startswith("en/") or rel == "en/index.html"
        locale = "en_US" if is_en else "zh_TW"
        og_title = property_attr(text, "og:title") or title(text)
        og_desc = property_attr(text, "og:description") or description(text)
        og_image = property_attr(text, "og:image") or "https://yoya9933.page/assets/og-image.png"
        text = ensure_meta(text, "og:url", url, prop=True)
        text = ensure_meta(text, "og:locale", locale, prop=True)
        text = ensure_meta(text, "twitter:card", "summary_large_image")
        text = ensure_meta(text, "twitter:title", og_title)
        text = ensure_meta(text, "twitter:description", og_desc)
        text = ensure_meta(text, "twitter:image", og_image)
        x_default = url.replace("/en/", "/") if "/en/" in url else url
        text = ensure_x_default(text, x_default)
        schema = project_schema(rel, text, url)
        if schema and '"@type":"CreativeWork"' not in text:
            text = add_before_head_end(text, schema)

    text = ensure_accessibility(text)
    text = harden_blank_links(text)
    text = ensure_image_dimensions(text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for html in sorted(SITE.rglob("*.html")):
        process(html)
    print(f"Enhanced published SEO using {len(PROJECT_BY_REL) // 2} project records")


if __name__ == "__main__":
    main()
