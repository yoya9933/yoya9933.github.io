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
        case_href = project["case"][locale]
        links.append(f'<a class="project-primary" href="{escape(case_href, quote=True)}">{case_label}</a>')

    live = project.get("live")
    repo = project.get("repo")
    external_specs: list[tuple[str, str]] = []
    if live:
        external_specs.append((live, project.get("live_label", {}).get(locale, "Live Demo ↗")))
    if repo:
        external_specs.append((repo, "GitHub ↗"))

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
        f'alt="{escape(project["image_alt"][locale], quote=True)}" loading="lazy"></div>'
        f'<div class="project-topline"><span class="project-number">{project["order"]:02d}</span>{badge_html}</div>'
        f'<h3>{escape(project["title"][locale])}</h3>'
        f'<p>{escape(project["card_description"][locale])}</p>'
        f'<ul class="tags">{tags}</ul>'
        f'<div class="project-links">{render_links(project, locale)}</div>'
        f'</article>'
    )


def render_additional(project: dict, locale: str) -> str:
    prefix = "../" if locale == "en" else ""
    tags = "".join(f"<li>{escape(tag)}</li>" for tag in project["tags"][locale])
    note = project.get("note", {}).get(locale)
    note_html = f'<p class="case-meta-note">{escape(note)}</p>' if note else ""
    return (
        '<article class="secondary-project" data-project="' + escape(project["slug"], quote=True) + '">'
        f'<div class="secondary-project-media"><img src="{prefix}assets/projects/{escape(project["image"], quote=True)}" '
        f'alt="{escape(project["image_alt"][locale], quote=True)}" loading="lazy"></div>'
        '<div class="secondary-project-copy">'
        f'<p class="eyebrow">{escape(project.get("eyebrow", ""))}</p>'
        f'<h3>{escape(project["title"][locale])}</h3>'
        f'<p>{escape(project["card_description"][locale])}</p>'
        f'<ul class="tags">{tags}</ul>'
        f'<div class="project-links">{render_links(project, locale)}</div>'
        f'{note_html}</div></article>'
    )


def replace_project_grid(text: str, cards: str) -> str:
    start = text.find('<div class="projects-grid')
    if start < 0:
        raise RuntimeError("projects-grid not found")
    open_end = text.find('>', start)
    additional = text.find('<section class="section shell" id="additional-work">', open_end)
    if additional < 0:
        raise RuntimeError("additional-work section not found")
    close = text.rfind('</div></section>', open_end, additional)
    if close < 0:
        raise RuntimeError("project grid closing marker not found")
    return text[:start] + f'<div class="projects-grid has-four-selected">{cards}</div>' + text[close + len('</div>'):]


def replace_additional_card(text: str, article: str) -> str:
    pattern = r'<article class="secondary-project"[^>]*>.*?</article>'
    if not re.search(pattern, text, flags=re.S):
        raise RuntimeError("secondary-project article not found")
    return re.sub(pattern, article, text, count=1, flags=re.S)


def replace_heading_copy(text: str, locale: str, heading: str) -> str:
    candidates = (
        "三個代表專案對應工程資料與 AI、多人 Web 產品，以及真實活動現場的全端營運流程。",
        "四個代表專案涵蓋工程資料與 AI、多人 Web、活動現場營運，以及可持續維護的商業 CMS。",
        "Three projects across engineering data and AI, a multiplayer web product, and a field-ready full-stack operations workflow.",
        "Four selected projects spanning engineering data and AI, multiplayer web, field operations, and a maintainable business CMS.",
    )
    for candidate in candidates:
        text = text.replace(candidate, heading)
    return text


def home_schema(data: dict, locale: str, selected: list[dict]) -> str:
    site_url = data["site_url"].rstrip("/")
    home = site_url + ("/en/" if locale == "en" else "/")
    language = "en" if locale == "en" else "zh-Hant-TW"
    person = {
        "@type": "Person",
        "@id": site_url + "/#person",
        "name": "Yoya",
        "url": site_url + "/",
        "sameAs": ["https://github.com/yoya9933"],
        "knowsAbout": ["Engineering Data", "Data Analysis", "Artificial Intelligence", "Full-stack Web Development", "Operations Automation"],
    }
    website = {
        "@type": "WebSite",
        "@id": home + "#website",
        "url": home,
        "name": "Yoya | Engineering × Data × AI Portfolio" if locale == "en" else "Yoya｜Engineering × Data × AI Portfolio",
        "inLanguage": language,
        "author": {"@id": site_url + "/#person"},
    }
    item_list = {
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
    }
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [person, website, item_list]}, ensure_ascii=False, separators=(",", ":")) + '</script>'


def replace_home_schema(text: str, schema: str) -> str:
    pattern = r'<script type="application/ld\+json">.*?</script>'
    if re.search(pattern, text, flags=re.S):
        return re.sub(pattern, schema, text, count=1, flags=re.S)
    return text.replace('</head>', schema + '</head>', 1)


def render_home(path: Path, data: dict, locale: str) -> None:
    selected = sorted((p for p in data["projects"] if p.get("section") == "selected"), key=lambda p: p["order"])
    additional = sorted((p for p in data["projects"] if p.get("section") == "additional"), key=lambda p: p["order"])
    if len(additional) != 1:
        raise RuntimeError("the current homepage expects exactly one additional project")

    text = path.read_text(encoding="utf-8")
    cards = "".join(render_selected_card(project, locale) for project in selected)
    text = replace_project_grid(text, cards)
    text = replace_additional_card(text, render_additional(additional[0], locale))
    text = replace_heading_copy(text, locale, data["selected_heading"][locale])
    text = replace_home_schema(text, home_schema(data, locale, selected))
    path.write_text(text, encoding="utf-8")


def render_case_actions(data: dict) -> None:
    for project in data["projects"]:
        for locale in ("zh", "en"):
            path = SITE / project["case"][locale].lstrip("/") / "index.html"
            text = path.read_text(encoding="utf-8")
            actions = f'<div class="case-actions" data-project-actions="{escape(project["slug"], quote=True)}">{render_links(project, locale, on_case_page=True)}</div>'
            pattern = r'<div class="case-actions"[^>]*>.*?</div>'
            if re.search(pattern, text, flags=re.S):
                text = re.sub(pattern, actions, text, count=1, flags=re.S)
            else:
                text = text.replace('</header>', actions + '</header>', 1)

            if project["slug"] == "shareholder-cms":
                text = text.replace('https://yoya9933.page/assets/projects/shareholder-cms.svg', 'https://yoya9933.page/assets/projects/shareholder-cms.png')
                text = text.replace('../../assets/projects/shareholder-cms.svg', '../../assets/projects/shareholder-cms.webp')
                if locale == "en":
                    text = text.replace('Shareholder Gift Service and CMS architecture preview', 'Shareholder Gift Service public website screenshot')
                    caption = 'The deployment captures the public homepage when reachable; a deterministic architecture visual is used only as a fallback. No authenticated admin page is captured.'
                else:
                    text = text.replace('股東紀念品服務與 CMS 平台架構示意', '股東紀念品服務公開網站首頁截圖')
                    caption = '部署時優先擷取公開正式網站首頁；若外部網站暫時無法連線才使用架構圖備援，不會擷取需要登入的管理後台。'
                text = re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{caption}</figcaption>', text, count=1, flags=re.S)
            path.write_text(text, encoding="utf-8")


def render_sitemap(data: dict) -> None:
    site_url = data["site_url"].rstrip("/")
    urls = [site_url + "/", site_url + "/en/", site_url + "/contact/", site_url + "/en/contact/"]
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
