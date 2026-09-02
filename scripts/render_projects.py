from __future__ import annotations

from html import escape
from pathlib import Path
import json
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA_PATH = ROOT / "data/projects.json"


def load_data() -> dict:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    projects = data.get("projects", [])
    slugs = [p["slug"] for p in projects]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("duplicate project slug in data/projects.json")

    selected = sorted((p for p in projects if p.get("section") == "selected"), key=lambda p: p["order"])
    orders = [p["order"] for p in selected]
    if orders != list(range(1, len(selected) + 1)):
        raise RuntimeError(f"selected project order must be contiguous from 1; got {orders}")

    for key in ("selected_title", "selected_heading", "additional_title", "additional_heading"):
        if not all(data.get(key, {}).get(locale) for locale in ("zh", "en")):
            raise RuntimeError(f"missing bilingual homepage copy: {key}")

    for project in projects:
        for locale in ("zh", "en"):
            case_url = project["case"][locale]
            case_file = SITE / case_url.lstrip("/") / "index.html"
            if not case_file.exists():
                raise RuntimeError(f"missing case study for {project['slug']} ({locale}): {case_file}")
    return data


def link_attrs(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"}:
        return ' target="_blank" rel="noopener noreferrer"'
    return ""


def absolute_case(site_url: str, project: dict, locale: str) -> str:
    return site_url.rstrip("/") + project["case"][locale]


def render_links(project: dict, locale: str, *, on_case_page: bool = False) -> str:
    links: list[str] = []
    if not on_case_page:
        case_label = "看 Case Study" if locale == "zh" else "Case Study"
        links.append(
            f'<a class="project-primary" href="{escape(project["case"][locale], quote=True)}">{case_label}</a>'
        )

    external_specs: list[tuple[str, str]] = []
    if project.get("live"):
        external_specs.append((project["live"], project.get("live_label", {}).get(locale, "Live Demo ↗")))
    if project.get("repo"):
        external_specs.append((project["repo"], "GitHub ↗"))

    for index, (url, label) in enumerate(external_specs):
        cls = ""
        if on_case_page and index == 0:
            cls = ' class="button primary"'
        elif on_case_page:
            cls = ' class="button secondary"'
        links.append(f'<a{cls} href="{escape(url, quote=True)}"{link_attrs(url)}>{escape(label)}</a>')
    return "".join(links)


def render_selected_card(project: dict, locale: str) -> str:
    prefix = "../" if locale == "en" else ""
    classes = "project-card featured" if project.get("featured") else "project-card"
    badge = project.get("badge")
    badge_html = f'<span class="project-badge">{escape(badge)}</span>' if badge else ""
    tags = "".join(f"<li>{escape(tag)}</li>" for tag in project["tags"][locale])
    return (
        f'<article class="{classes}" data-project="{escape(project["slug"], quote=True)}">'
        f'<div class="project-media"><img src="{prefix}assets/projects/{escape(project["image"], quote=True)}" '
        f'alt="{escape(project["image_alt"][locale], quote=True)}" loading="lazy" decoding="async"></div>'
        f'<div class="project-topline"><span class="project-number">{project["order"]:02d}</span>{badge_html}</div>'
        f'<h3>{escape(project["title"][locale])}</h3>'
        f'<p>{escape(project["card_description"][locale])}</p>'
        f'<ul class="tags">{tags}</ul>'
        f'<div class="project-links">{render_links(project, locale)}</div>'
        "</article>"
    )


def render_additional_card(project: dict, locale: str) -> str:
    prefix = "../" if locale == "en" else ""
    tags = "".join(f"<li>{escape(tag)}</li>" for tag in project["tags"][locale])
    note = project.get("note", {}).get(locale)
    note_html = f'<p class="case-meta-note">{escape(note)}</p>' if note else ""
    return (
        f'<article class="secondary-project" data-project="{escape(project["slug"], quote=True)}">'
        f'<div class="secondary-project-media"><img src="{prefix}assets/projects/{escape(project["image"], quote=True)}" '
        f'alt="{escape(project["image_alt"][locale], quote=True)}" loading="lazy" decoding="async"></div>'
        '<div class="secondary-project-copy">'
        f'<p class="eyebrow">{escape(project.get("eyebrow", ""))}</p>'
        f'<h3>{escape(project["title"][locale])}</h3>'
        f'<p>{escape(project["card_description"][locale])}</p>'
        f'<ul class="tags">{tags}</ul>'
        f'<div class="project-links">{render_links(project, locale)}</div>'
        f'{note_html}</div></article>'
    )


def render_selected_section(data: dict, locale: str, selected: list[dict]) -> str:
    cards = "".join(render_selected_card(project, locale) for project in selected)
    return (
        '<section class="section shell" id="projects">'
        '<div class="section-heading"><p class="section-index">01 / SELECTED WORK</p><div>'
        f'<h2>{escape(data["selected_title"][locale])}</h2>'
        f'<p>{escape(data["selected_heading"][locale])}</p>'
        '</div></div>'
        f'<div class="projects-grid">{cards}</div>'
        '</section>'
    )


def render_additional_section(data: dict, locale: str, project: dict) -> str:
    return (
        '<section class="section shell" id="additional-work">'
        '<div class="section-heading"><p class="section-index">02 / ADDITIONAL SYSTEM</p><div>'
        f'<h2>{escape(data["additional_title"][locale])}</h2>'
        f'<p>{escape(data["additional_heading"][locale])}</p>'
        '</div></div>'
        f'{render_additional_card(project, locale)}'
        '</section>'
    )


def replace_section(text: str, section_id: str, rendered: str) -> str:
    pattern = rf'<section\s+class="section shell"\s+id="{re.escape(section_id)}">.*?</section>'
    if not re.search(pattern, text, flags=re.S):
        raise RuntimeError(f"homepage section not found: {section_id}")
    return re.sub(pattern, rendered, text, count=1, flags=re.S)


def home_schema(data: dict, locale: str, selected: list[dict]) -> str:
    site_url = data["site_url"].rstrip("/")
    home = site_url + ("/en/" if locale == "en" else "/")
    language = "en" if locale == "en" else "zh-Hant-TW"
    graph = [
        {
            "@type": "Person",
            "@id": site_url + "/#person",
            "name": "Yoya",
            "url": site_url + "/",
            "sameAs": ["https://github.com/yoya9933"],
            "knowsAbout": [
                "Engineering Data",
                "Data Analysis",
                "Artificial Intelligence",
                "Full-stack Web Development",
                "Operations Automation",
            ],
        },
        {
            "@type": "WebSite",
            "@id": home + "#website",
            "url": home,
            "name": "Yoya | Engineering × Data × AI Portfolio" if locale == "en" else "Yoya｜Engineering × Data × AI Portfolio",
            "inLanguage": language,
            "author": {"@id": site_url + "/#person"},
        },
        {
            "@type": "ItemList",
            "name": "Selected Projects",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": project["order"],
                    "url": absolute_case(site_url, project, locale),
                    "name": project["title"][locale],
                }
                for project in selected
            ],
        },
    ]
    return '<script type="application/ld+json">' + json.dumps(
        {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")
    ) + '</script>'


def replace_home_schema(text: str, schema: str) -> str:
    pattern = r'<script type="application/ld\+json">.*?</script>'
    if re.search(pattern, text, flags=re.S):
        return re.sub(pattern, schema, text, count=1, flags=re.S)
    return text.replace("</head>", schema + "</head>", 1)


def render_home(path: Path, data: dict, locale: str) -> None:
    selected = sorted((p for p in data["projects"] if p.get("section") == "selected"), key=lambda p: p["order"])
    additional = sorted((p for p in data["projects"] if p.get("section") == "additional"), key=lambda p: p["order"])
    if len(additional) != 1:
        raise RuntimeError("homepage expects exactly one additional project")

    text = path.read_text(encoding="utf-8")
    text = replace_section(text, "projects", render_selected_section(data, locale, selected))
    text = replace_section(text, "additional-work", render_additional_section(data, locale, additional[0]))
    text = replace_home_schema(text, home_schema(data, locale, selected))
    path.write_text(text, encoding="utf-8")


def update_case_visual(text: str, project: dict, locale: str, site_url: str) -> str:
    visual = project.get("case_visual")
    if not visual:
        return text

    og_asset = visual.get("og_asset")
    if og_asset:
        og_url = f'{site_url.rstrip("/")}/assets/projects/{og_asset}'
        text = re.sub(
            r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
            lambda match: match.group(1) + escape(og_url, quote=True) + match.group(2),
            text,
            count=1,
            flags=re.I,
        )

    asset = visual["asset"]
    prefix = "../../../" if locale == "en" else "../../"
    replacement_src = f'{prefix}assets/projects/{asset}'
    figure_pattern = r'(<figure\s+class="case-shot"[^>]*>.*?<img\b)([^>]*)(>)(.*?</figure>)'
    match = re.search(figure_pattern, text, flags=re.I | re.S)
    if not match:
        return text

    attrs = match.group(2)
    attrs = re.sub(r'\s+src="[^"]*"', f' src="{escape(replacement_src, quote=True)}"', attrs, count=1)
    alt = visual.get("alt", {}).get(locale, project["image_alt"][locale])
    if re.search(r'\s+alt="[^"]*"', attrs):
        attrs = re.sub(r'\s+alt="[^"]*"', f' alt="{escape(alt, quote=True)}"', attrs, count=1)
    else:
        attrs += f' alt="{escape(alt, quote=True)}"'
    figure = match.group(1) + attrs + match.group(3) + match.group(4)
    caption = visual.get("caption", {}).get(locale)
    if caption:
        figure = re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{escape(caption)}</figcaption>', figure, count=1, flags=re.S)
    return text[:match.start()] + figure + text[match.end():]


def render_case_actions(data: dict) -> None:
    for project in data["projects"]:
        for locale in ("zh", "en"):
            path = SITE / project["case"][locale].lstrip("/") / "index.html"
            text = path.read_text(encoding="utf-8")
            actions = (
                f'<div class="case-actions" data-project-actions="{escape(project["slug"], quote=True)}">'
                f'{render_links(project, locale, on_case_page=True)}</div>'
            )
            pattern = r'<div class="case-actions"[^>]*>.*?</div>'
            if re.search(pattern, text, flags=re.S):
                text = re.sub(pattern, actions, text, count=1, flags=re.S)
            else:
                text = text.replace("</header>", actions + "</header>", 1)
            text = update_case_visual(text, project, locale, data["site_url"])
            path.write_text(text, encoding="utf-8")


def render_sitemap(data: dict) -> None:
    site_url = data["site_url"].rstrip("/")
    urls = [site_url + "/", site_url + "/en/", site_url + "/contact/", site_url + "/en/contact/", site_url + "/changelog/"]
    for project in sorted(data["projects"], key=lambda p: (p.get("section", ""), p.get("order", 0))):
        urls.append(absolute_case(site_url, project, "zh"))
        urls.append(absolute_case(site_url, project, "en"))
    body = "\n".join(f"  <url><loc>{escape(url)}</loc></url>" for url in urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def main() -> None:
    data = load_data()
    render_home(SITE / "index.html", data, "zh")
    render_home(SITE / "en/index.html", data, "en")
    render_case_actions(data)
    render_sitemap(data)
    print(f"Rendered {len(data['projects'])} projects from data/projects.json")


if __name__ == "__main__":
    main()
