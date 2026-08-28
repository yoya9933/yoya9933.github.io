from __future__ import annotations

from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))

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


def facts_html(project: dict, locale: str) -> str:
    facts = project.get("case_facts")
    if not isinstance(facts, dict):
        raise RuntimeError(f"case_facts missing for {project['slug']}")
    labels = FACT_LABELS[locale]
    values = {
        "role": localized(facts.get("role"), locale),
        "scope": localized(facts.get("scope"), locale),
        "status": localized(facts.get("status"), locale),
        "stack": localized(facts.get("stack"), locale),
        "year": localized(facts.get("year"), locale),
    }
    items = "".join(
        f'<div><dt>{escape(labels[key])}</dt><dd>{escape(values[key])}</dd></div>'
        for key in ("role", "scope", "status", "stack", "year")
    )
    return (
        f'<div class="case-facts" data-case-facts="{escape(project["slug"], quote=True)}">'
        f'<dl>{items}</dl></div>'
    )


def framing_html(project: dict, locale: str) -> str:
    frame = project.get("case_frame")
    if not isinstance(frame, dict):
        raise RuntimeError(f"case_frame missing for {project['slug']}")
    labels = FRAME_LABELS[locale]
    cards = "".join(
        '<article class="case-card">'
        f'<strong>{escape(labels[key])}</strong>'
        f'{escape(localized(frame.get(key), locale))}'
        '</article>'
        for key in ("problem", "decision", "evidence", "next")
    )
    return (
        f'<section class="case-section case-framing" data-case-framing="{escape(project["slug"], quote=True)}">'
        '<h2>00 / Project framing</h2><div>'
        f'<h3>{escape(labels["heading"])}</h3>'
        f'<div class="case-grid">{cards}</div>'
        '</div></section>'
    )


def render(path: Path, project: dict, locale: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<div class="case-facts"[^>]*>.*?</dl></div>', '', text, flags=re.I | re.S)
    text = re.sub(r'<section class="case-section case-framing"[^>]*>.*?</section>', '', text, flags=re.I | re.S)

    facts = facts_html(project, locale)
    header_end = text.find("</header>")
    if header_end < 0:
        raise RuntimeError(f"case header missing: {path}")
    text = text[:header_end] + facts + text[header_end:]

    main_match = re.search(r'<main\b[^>]*class="[^"]*case-content[^"]*"[^>]*>', text, flags=re.I)
    if not main_match:
        raise RuntimeError(f"case main missing: {path}")
    frame = framing_html(project, locale)
    text = text[:main_match.end()] + frame + text[main_match.end():]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    rendered = 0
    for project in DATA["projects"]:
        for locale in ("zh", "en"):
            path = SITE / project["case"][locale].lstrip("/") / "index.html"
            if not path.is_file():
                raise RuntimeError(f"case page missing: {path}")
            render(path, project, locale)
            rendered += 1
    print(f"Rendered Case Study 2.0 framing for {rendered} localized pages")


if __name__ == "__main__":
    main()
