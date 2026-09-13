from __future__ import annotations

from pathlib import Path
import json

from apply_csp import inject_meta
from common import ROOT, SITE
from render_changelog import render_page as render_changelog


# Inlined from the former standalone renderer module.
from html import escape
from pathlib import Path
import json
import re
from urllib.parse import urlparse

from common import ROOT, SITE, case_output, case_url, insert_before_head_end, load_projects, project_image, selected_projects

FACT_LABELS = {
    "zh": {"role": "角色", "scope": "範圍", "status": "狀態", "stack": "技術", "year": "年份"},
    "en": {"role": "Role", "scope": "Scope", "status": "Status", "stack": "Stack", "year": "Year"},
}
FRAME_LABELS = {
    "zh": {"heading": "專案脈絡與工程判斷", "problem": "Problem", "decision": "Decision", "evidence": "Evidence", "next": "Next"},
    "en": {"heading": "Project framing and engineering decisions", "problem": "Problem", "decision": "Decision", "evidence": "Evidence", "next": "Next"},
}


def localized(value: object, locale: str) -> str:
    if isinstance(value, dict):
        result = value.get(locale)
        if isinstance(result, str) and result.strip():
            return result.strip()
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise RuntimeError(f"missing localized case-study value for {locale}: {value!r}")


def facts_html(project: dict, locale: str, year: str) -> str:
    facts = project.get("case_facts")
    if not isinstance(facts, dict):
        raise RuntimeError(f"case_facts missing for {project['slug']}")
    labels = FACT_LABELS[locale]
    values = {key: localized(facts.get(key), locale) for key in ("role", "scope", "status", "stack")}
    values["year"] = year
    items = "".join(
        f'<div><dt>{escape(labels[key])}</dt><dd>{escape(values[key])}</dd></div>'
        for key in ("role", "scope", "status", "stack", "year")
    )
    return f'<div class="case-facts" data-case-facts="{escape(project["slug"], quote=True)}"><dl>{items}</dl></div>'


def framing_html(project: dict, locale: str) -> str:
    frame = project.get("case_frame")
    if not isinstance(frame, dict):
        raise RuntimeError(f"case_frame missing for {project['slug']}")
    labels = FRAME_LABELS[locale]
    cards = "".join(
        '<article class="case-card">'
        f'<strong>{escape(labels[key])}</strong>{escape(localized(frame.get(key), locale))}'
        '</article>'
        for key in ("problem", "decision", "evidence", "next")
    )
    return (
        f'<section class="case-section case-framing" data-case-framing="{escape(project["slug"], quote=True)}">'
        '<h2>00 / Project framing</h2><div>'
        f'<h3>{escape(labels["heading"])}</h3><div class="case-grid">{cards}</div>'
        '</div></section>'
    )


def render_case_framing(text: str, project: dict, locale: str, year: str) -> str:
    text = re.sub(r'<div class="case-facts"[^>]*>.*?</dl></div>', '', text, flags=re.I | re.S)
    text = re.sub(r'<section class="case-section case-framing"[^>]*>.*?</section>', '', text, flags=re.I | re.S)
    header_end = text.find("</header>")
    if header_end < 0:
        raise RuntimeError(f"case header missing: {project['slug']} ({locale})")
    text = text[:header_end] + facts_html(project, locale, year) + text[header_end:]
    main = re.search(r'<main\b[^>]*class="[^"]*case-content[^"]*"[^>]*>', text, flags=re.I)
    if not main:
        raise RuntimeError(f"case main missing: {project['slug']} ({locale})")
    return text[:main.end()] + framing_html(project, locale) + text[main.end():]


def load_data() -> dict:
    data = load_projects()
    projects = data.get("projects", [])
    slugs = [p["slug"] for p in projects]
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("duplicate project slug in data/projects.json")

    selected = selected_projects({"projects": projects})
    orders = [p["order"] for p in selected]
    if orders != list(range(1, len(selected) + 1)):
        raise RuntimeError(f"selected project order must be contiguous from 1; got {orders}")

    for key in ("selected_title", "selected_heading"):
        if not all(data.get(key, {}).get(locale) for locale in ("zh", "en")):
            raise RuntimeError(f"missing bilingual homepage copy: {key}")

    for project in projects:
        for locale in ("zh", "en"):
            case_file = case_output(project, locale)
            if not case_file.exists():
                raise RuntimeError(f"missing case study for {project['slug']} ({locale}): {case_file}")
    return data


def link_attrs(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"}:
        return ' target="_blank" rel="noopener noreferrer"'
    return ""


def absolute_case(site_url: str, project: dict, locale: str) -> str:
    return site_url.rstrip("/") + case_url(project, locale)


def render_links(project: dict, locale: str, *, on_case_page: bool = False) -> str:
    links: list[str] = []
    if not on_case_page:
        case_label = "看 Case Study" if locale == "zh" else "Case Study"
        links.append(
            f'<a class="project-primary" href="{escape(case_url(project, locale), quote=True)}">{case_label}</a>'
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
        f'<div class="project-media"><img src="{prefix}assets/projects/{escape(project_image(project), quote=True)}" '
        f'alt="{escape(project["image_alt"][locale], quote=True)}" loading="lazy" decoding="async"></div>'
        f'<div class="project-topline"><span class="project-number">{project["order"]:02d}</span>{badge_html}</div>'
        f'<h3>{escape(project["title"][locale])}</h3>'
        f'<p>{escape(project["card_description"][locale])}</p>'
        f'<ul class="tags">{tags}</ul>'
        f'<div class="project-links">{render_links(project, locale)}</div>'
        "</article>"
    )


def render_selected_section(data: dict, locale: str, selected: list[dict]) -> str:
    cards = "".join(render_selected_card(project, locale) for project in selected)
    return (
        '<section class="section shell" id="projects">'
        '<div class="section-heading"><p class="section-index">02 / SELECTED WORK</p><div>'
        f'<h2>{escape(data["selected_title"][locale])}</h2>'
        f'<p>{escape(data["selected_heading"][locale])}</p>'
        '</div></div>'
        f'<div class="projects-grid">{cards}</div>'
        '</section>'
    )


def render_timeline(groups: list[dict], locale: str) -> str:
    rendered_groups: list[str] = []
    for group in groups:
        items: list[str] = []
        for item in group["items"]:
            detail = localized(item["detail"], locale)
            link = item.get("link")
            if link:
                detail += (
                    f' <a class="evidence-link" href="{escape(link["url"], quote=True)}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f'{escape(localized(link["label"], locale))}</a>'
                )
            items.append(
                '<div class="timeline-item">'
                f'<time>{escape(localized(item["date"], locale))}</time>'
                f'<div><strong>{escape(localized(item["title"], locale))}</strong>'
                f'<span>{detail}</span></div></div>'
            )
        rendered_groups.append(
            f'<div class="achievement-group"><h3>{escape(localized(group["heading"], locale))}</h3>'
            f'<div class="timeline">{"".join(items)}</div></div>'
        )
    return "".join(rendered_groups)


def render_timeline_section(text: str, locale: str) -> str:
    timeline_path = ROOT / "data" / "timeline.json"
    groups = json.loads(timeline_path.read_text(encoding="utf-8"))["groups"]
    generated = render_timeline(groups, locale)
    if "<!-- timeline-items -->" in text:
        return text.replace("<!-- timeline-items -->", generated, 1)
    pattern = r'<div class="achievement-group">.*?(?=</section>)'
    if re.search(pattern, text, flags=re.S):
        return re.sub(pattern, generated, text, count=1, flags=re.S)
    raise RuntimeError(f"timeline section placeholder missing for {locale}")


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
            "name": "Yu",
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
            "name": "Yu | Engineering × Data × AI Portfolio" if locale == "en" else "Yu｜Engineering × Data × AI Portfolio",
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
    return insert_before_head_end(text, schema)


def render_home_text(text: str, data: dict, locale: str) -> str:
    selected = selected_projects(data)
    text = render_timeline_section(text, locale)
    text = replace_section(text, "projects", render_selected_section(data, locale, selected))
    return replace_home_schema(text, home_schema(data, locale, selected))


def render_home(path: Path, data: dict, locale: str) -> None:
    path.write_text(render_home_text(path.read_text(encoding="utf-8"), data, locale), encoding="utf-8")


def update_case_visual(text: str, project: dict, locale: str, site_url: str) -> str:
    visual = project.get("case_visual")
    if not visual:
        return text

    og_url = f'{site_url.rstrip("/")}/assets/projects/{project["slug"]}.png'
    text = re.sub(
        r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
        lambda match: match.group(1) + escape(og_url, quote=True) + match.group(2),
        text,
        count=1,
        flags=re.I,
    )

    asset = project_image(project)
    prefix = "../../../" if locale == "en" else "../../"
    replacement_src = f'{prefix}assets/projects/{asset}'
    figure_pattern = r'(<figure\s+class="case-shot"[^>]*>.*?<img\b)([^>]*)(>)(.*?</figure>)'
    match = re.search(figure_pattern, text, flags=re.I | re.S)
    if not match:
        return text

    attrs = match.group(2)
    attrs = re.sub(r'\s+src="[^"]*"', f' src="{escape(replacement_src, quote=True)}"', attrs, count=1)
    alt = project["image_alt"][locale]
    if re.search(r'\s+alt="[^"]*"', attrs):
        attrs = re.sub(r'\s+alt="[^"]*"', f' alt="{escape(alt, quote=True)}"', attrs, count=1)
    else:
        attrs += f' alt="{escape(alt, quote=True)}"'
    figure = match.group(1) + attrs + match.group(3) + match.group(4)
    caption = visual.get("caption", {}).get(locale)
    if caption:
        figure = re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{escape(caption)}</figcaption>', figure, count=1, flags=re.S)
    return text[:match.start()] + figure + text[match.end():]


def render_case_actions_text(text: str, project: dict, locale: str, data: dict) -> str:
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
    return render_case_framing(text, project, locale, data["project_year"])


def render_case_page(project: dict, locale: str, data: dict) -> str:
    page = project["case_page"][locale]
    route = case_url(project, locale)
    asset_prefix = "../../../" if locale == "en" else "../../"
    home_url = "/en/#projects" if locale == "en" else "/#projects"
    locale_url = case_url(project, "zh" if locale == "en" else "en")
    back_label = "← Back to portfolio" if locale == "en" else "← 回到作品集"
    locale_label = "中文" if locale == "en" else "EN"
    lang = "en" if locale == "en" else "zh-Hant-TW"
    canonical = data["site_url"].rstrip("/") + route
    og_image = data["site_url"].rstrip("/") + f"/assets/projects/{project['slug']}.png"
    fragment = ROOT / "data" / "case-studies" / f"{project['slug']}.{locale}.html"
    if not fragment.is_file():
        raise RuntimeError(f"case-study content missing: {fragment}")
    content = fragment.read_text(encoding="utf-8").strip()
    return (
        '<!DOCTYPE html><html lang="' + escape(lang, quote=True) + '" data-theme="dark"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="theme-color" content="#07111f">'
        f'<title>{escape(page["title"])}</title>'
        f'<meta name="description" content="{escape(page["description"], quote=True)}">'
        f'<link rel="canonical" href="{escape(canonical, quote=True)}">'
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">'
        '<meta property="og:type" content="article">'
        f'<meta property="og:title" content="{escape(page["og_title"], quote=True)}">'
        f'<meta property="og:description" content="{escape(page["og_description"], quote=True)}">'
        f'<meta property="og:image" content="{escape(og_image, quote=True)}">'
        f'<link rel="stylesheet" href="{asset_prefix}assets/styles.css">'
        '</head><body class="case-page">'
        f'<a class="skip-link" href="#main">{"Skip to main content" if locale == "en" else "跳到主要內容"}</a>'
        f'<nav class="case-nav shell"><a href="{home_url}">{back_label}</a>'
        f'<span class="toolbar"><a href="{locale_url}">{locale_label}</a></span></nav>'
        f'{content}<script src="{asset_prefix}assets/main.js" defer></script></body></html>'
    )


def render_all(pages: dict[Path, str], data: dict) -> None:
    for rel, locale in (("index.html", "zh"), ("en/index.html", "en")):
        path = SITE / rel
        pages[path] = render_home_text(pages[path], data, locale)
    for project in data["projects"]:
        for locale in ("zh", "en"):
            path = case_output(project, locale)
            page = render_case_page(project, locale, data)
            pages[path] = render_case_actions_text(page, project, locale, data)
    render_sitemap(data)


def render_sitemap(data: dict) -> None:
    site_url = data["site_url"].rstrip("/")
    urls = [site_url + "/", site_url + "/en/", site_url + "/contact/", site_url + "/en/contact/", site_url + "/changelog/"]
    for project in selected_projects(data):
        urls.append(absolute_case(site_url, project, "zh"))
        urls.append(absolute_case(site_url, project, "en"))
    body = "\n".join(f"  <url><loc>{escape(url)}</loc></url>" for url in urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")


# Inlined from the former standalone renderer module.
from html import escape
from pathlib import Path
import json
import re

from common import SITE, insert_before_head_end, load_projects, png_dimensions

PROJECT_DATA = load_projects()

PROJECT_BY_REL: dict[str, tuple[dict, str]] = {}
for project in PROJECT_DATA["projects"]:
    PROJECT_BY_REL[f"projects/{project['slug']}/index.html"] = (project, "zh")
    PROJECT_BY_REL[f"en/projects/{project['slug']}/index.html"] = (project, "en")


def project_dimensions() -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for project in PROJECT_DATA["projects"]:
        dimensions = png_dimensions(SITE / "assets" / "projects" / f"{project['slug']}.png")
        if dimensions:
            result[project["slug"]] = dimensions
    return result


PROJECT_DIMENSIONS = project_dimensions()


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
    return re.sub(r'\s+', ' ', match.group(1)).strip() if match else "Yu Portfolio"


def description(text: str) -> str:
    return attr(text, "description") or "Engineering, data and AI portfolio by Yu."


def add_before_head_end(text: str, fragment: str) -> str:
    return insert_before_head_end(text, fragment)


def ensure_meta(text: str, key: str, value: str, *, prop: bool = False) -> str:
    kind = "property" if prop else "name"
    pattern = rf'<meta\s+{kind}="{re.escape(key)}"\s+content="[^"]*"[^>]*>'
    tag = f'<meta {kind}="{key}" content="{escape(value, quote=True)}">'
    if re.search(pattern, text, re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return add_before_head_end(text, tag)


def ensure_link(text: str, rel: str, href: str, extra: str = "") -> str:
    tag = f'<link rel="{escape(rel, quote=True)}" href="{escape(href, quote=True)}"{extra}>'
    pattern = rf'<link\s+rel="{re.escape(rel)}"[^>]*>'
    if re.search(pattern, text, re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return add_before_head_end(text, tag)


def ensure_hreflang(text: str, path: Path, url: str) -> str:
    rel = path.relative_to(SITE).as_posix()
    if rel.startswith("en/"):
        zh_rel, en_rel = rel[3:], rel
    else:
        zh_rel, en_rel = rel, f"en/{rel}"
    zh_path = SITE / zh_rel
    en_path = SITE / en_rel
    if not zh_path.is_file() or not en_path.is_file():
        zh_url = url.replace("/en/", "/") if "/en/" in url else url
        return ensure_alternate(text, "x-default", zh_url)

    site_url = PROJECT_DATA["site_url"].rstrip("/")
    route = url[len(site_url):] if url.startswith(site_url) else "/"
    if route.startswith("/en/"):
        zh_route, en_route = "/" + route[4:], route
    elif route == "/en/":
        zh_route, en_route = "/", route
    elif route in {"", "/"}:
        zh_route, en_route = "/", "/en/"
    else:
        zh_route, en_route = route, "/en" + route
    text = ensure_alternate(text, "zh-Hant", site_url + zh_route)
    text = ensure_alternate(text, "en", site_url + en_route)
    return ensure_alternate(text, "x-default", site_url + zh_route)


def ensure_alternate(text: str, locale: str, href: str) -> str:
    tag = f'<link rel="alternate" hreflang="{locale}" href="{escape(href, quote=True)}">'
    pattern = rf'<link\s+rel="alternate"\s+hreflang="{re.escape(locale)}"[^>]*>'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return add_before_head_end(text, tag)


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
        src_match = re.search(r'src="[^"]*assets/projects/([^/".]+)\.(?:webp|png|svg)"', tag, re.I)
        slug = src_match.group(1) if src_match else ""
        width, height = PROJECT_DIMENSIONS.get(slug, (1200, 720))
        if re.search(r'\swidth="[^"]*"', tag, re.I):
            tag = re.sub(r'\swidth="[^"]*"', f' width="{width}"', tag, count=1, flags=re.I)
        else:
            tag = tag[:-1] + f' width="{width}">'
        if re.search(r'\sheight="[^"]*"', tag, re.I):
            tag = re.sub(r'\sheight="[^"]*"', f' height="{height}"', tag, count=1, flags=re.I)
        else:
            tag = tag[:-1] + f' height="{height}">'
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
        "author": {"@type": "Person", "name": "Yu", "url": "https://yoya9933.page/"},
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


def transform(path: Path, text: str) -> str:
    rel = path.relative_to(SITE).as_posix()
    if rel == "404.html":
        return ensure_accessibility(harden_blank_links(text))

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
        text = ensure_hreflang(text, path, url)
        schema = project_schema(rel, text, url)
        if schema and '"@type":"CreativeWork"' not in text:
            text = add_before_head_end(text, schema)
        if rel in {"index.html", "en/index.html"}:
            text = ensure_meta(text, "author", "Yu")
            text = ensure_meta(text, "robots", "index,follow")
            text = ensure_meta(text, "og:locale", "en_US" if rel == "en/index.html" else "zh_TW", prop=True)
            text = ensure_meta(text, "og:image:type", "image/png", prop=True)
            text = ensure_meta(text, "og:image:width", "1200", prop=True)
            text = ensure_meta(text, "og:image:height", "630", prop=True)
            text = ensure_link(text, "apple-touch-icon", "/assets/apple-touch-icon.png", ' sizes="180x180"')
            text = ensure_link(text, "manifest", "/site.webmanifest")

    text = ensure_accessibility(text)
    text = harden_blank_links(text)
    text = ensure_image_dimensions(text)
    return text


# Inlined from the former standalone renderer module.
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import os
import re
import subprocess

from common import ROOT, SITE, SEMVER_RE, env_int, expected_environment, insert_before_head_end

VERSION_FILE = ROOT / "VERSION"
REPOSITORY = "https://github.com/yoya9933/yoya9933.github.io"
SITE_URL = "https://yoya9933.page"
BUILD_TIMEZONE = ZoneInfo("Asia/Taipei")
ASSET_REF_RE = re.compile(
    r'(?P<prefix>\b(?:href|src)=")(?P<url>[^"?#]+\.(?:css|js))(?P<query>\?[^"#]*)?(?P<fragment>#[^"]*)?(?P<suffix>")',
    re.I,
)


def read_version() -> str:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise RuntimeError(f"VERSION is not valid SemVer: {version!r}")
    return version


def read_commit() -> str:
    candidate = os.environ.get("GITHUB_SHA", "").strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", candidate):
        return candidate
    try:
        candidate = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip().lower()
    except (OSError, subprocess.CalledProcessError):
        return "local"
    return candidate if re.fullmatch(r"[0-9a-f]{40}", candidate) else "local"


def build_environment() -> str:
    return expected_environment()


def ensure_version_meta(text: str, version: str) -> str:
    tag = f'<meta name="application-version" content="{escape(version, quote=True)}">'
    pattern = r'<meta\s+name="application-version"\s+content="[^"]*"[^>]*>'
    if re.search(pattern, text, flags=re.I):
        return re.sub(pattern, tag, text, count=1, flags=re.I)
    return insert_before_head_end(text, tag)


def version_asset_refs(text: str, version: str) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group("url")
        if url.startswith(("http://", "https://", "//", "data:")):
            return match.group(0)
        fragment = match.group("fragment") or ""
        return f'{match.group("prefix")}{url}?v={escape(version, quote=True)}{fragment}{match.group("suffix")}'

    return ASSET_REF_RE.sub(replace, text)


def footer_version(version: str, commit: str) -> str:
    changelog_url = "/changelog/"
    if commit == "local":
        commit_url = REPOSITORY
        commit_label = "local"
    else:
        commit_url = f"{REPOSITORY}/commit/{commit}"
        commit_label = commit[:7]
    return (
        '<span class="site-version" role="group" aria-label="Website version">'
        f'<a href="{changelog_url}">v{escape(version)}</a>'
        '<span aria-hidden="true">·</span>'
        f'<a href="{commit_url}" target="_blank" rel="noopener noreferrer">{escape(commit_label)}</a>'
        '</span>'
    )


def inject_footer(text: str, version: str, commit: str) -> str:
    text = re.sub(r'<span class="site-version"[^>]*>.*?</span>', '', text, flags=re.I | re.S)
    marker = "</div></footer>"
    if marker not in text:
        return text
    return text.replace(marker, footer_version(version, commit) + marker, 1)


def build_payload() -> tuple[str, str, dict[str, object]]:
    version = read_version()
    commit = read_commit()
    build_time = datetime.now(BUILD_TIMEZONE).isoformat(timespec="seconds")
    environment = build_environment()
    run_id = env_int("GITHUB_RUN_ID")
    run_number = env_int("GITHUB_RUN_NUMBER")
    repository_slug = os.environ.get("GITHUB_REPOSITORY", "").strip()
    workflow_run = (
        f"https://github.com/{repository_slug}/actions/runs/{run_id}"
        if repository_slug and run_id is not None
        else None
    )

    payload = {
        "version": version,
        "commit": commit,
        "build_time": build_time,
        "environment": environment,
        "ref": os.environ.get("GITHUB_REF") or None,
        "workflow": os.environ.get("GITHUB_WORKFLOW") or None,
        "run_id": run_id,
        "run_number": run_number,
        "workflow_run": workflow_run,
        "repository": REPOSITORY,
        "changelog": f"{SITE_URL}/changelog/",
        "source_changelog": f"{REPOSITORY}/blob/main/CHANGELOG.md",
        "release": f"{REPOSITORY}/releases/tag/v{version}",
        "commit_url": REPOSITORY if commit == "local" else f"{REPOSITORY}/commit/{commit}",
    }
    return version, commit, payload


def transform_html(text: str, path: Path, version: str, commit: str) -> str:
    text = ensure_version_meta(text, version)
    text = version_asset_refs(text, version)
    if path.relative_to(SITE).as_posix() in {"index.html", "en/index.html"}:
        text = inject_footer(text, version, commit)
    return text


def main() -> None:
    pages: dict[Path, str] = {
        path: path.read_text(encoding="utf-8")
        for path in sorted(SITE.rglob("*.html"))
    }
    if not pages:
        raise RuntimeError("no staged HTML pages found")

    data = load_data()
    render_all(pages, data)
    changelog_path, changelog_html, changelog_count = render_changelog()
    pages[changelog_path] = changelog_html

    version, commit, version_info = build_payload()
    for path, text in pages.items():
        text = transform(path, text)
        text = transform_html(text, path, version, commit)
        pages[path] = inject_meta(text)

    for path, text in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    (SITE / "version.json").write_text(
        json.dumps(version_info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Rendered {len(data['projects'])} projects and {changelog_count} changelog releases")
    print(f"Rendered and hardened {len(pages)} HTML pages in a single write pass")
    print(
        f"Rendered website version v{version} ({commit[:7] if commit != 'local' else 'local'}) "
        f"for {version_info['environment']} at {version_info['build_time']}"
    )



if __name__ == "__main__":
    main()
