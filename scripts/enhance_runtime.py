from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
PROJECT_DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
PROJECT_SLUGS = tuple(project["slug"] for project in PROJECT_DATA["projects"])
PROJECT_SLUG_PATTERN = "|".join(re.escape(slug) for slug in PROJECT_SLUGS)
GITHUB_AVATAR = "https://github.com/yoya9933.png"


def ensure_github_avatar(tag: str) -> str:
    tag = re.sub(
        r'src="(?:https://github\.com/yoya9933\.png|/assets/avatar-fallback\.svg)"',
        f'src="{GITHUB_AVATAR}"',
        tag,
        count=1,
        flags=re.I,
    )
    tag = re.sub(r'\s+data-avatar-fallback="[^"]*"', '', tag, flags=re.I)
    if 'referrerpolicy=' not in tag:
        tag = tag[:-1] + ' referrerpolicy="no-referrer">'
    if 'width=' not in tag:
        tag = tag[:-1] + ' width="156">'
    if 'height=' not in tag:
        tag = tag[:-1] + ' height="156">'
    if 'decoding=' not in tag:
        tag = tag[:-1] + ' decoding="async">'
    return tag


def ensure_runtime(text: str) -> str:
    text = re.sub(r'<script\s+data-theme-bootstrap>.*?</script>', '', text, flags=re.I | re.S)
    text = re.sub(r'<button\b[^>]*data-theme-toggle[^>]*>.*?</button>', '', text, flags=re.I | re.S)
    text = re.sub(r'<html([^>]*)\sdata-theme="[^"]*"([^>]*)>', r'<html\1 data-theme="dark"\2>', text, count=1, flags=re.I)
    if 'data-theme="dark"' not in text:
        text = re.sub(r'<html([^>]*)>', r'<html\1 data-theme="dark">', text, count=1, flags=re.I)

    if 'name="theme-color"' in text:
        text = re.sub(r'<meta\s+name="theme-color"\s+content="[^"]*"[^>]*>', '<meta name="theme-color" content="#07111f">', text, count=1, flags=re.I)
    else:
        text = text.replace('</head>', '<meta name="theme-color" content="#07111f"></head>', 1)

    def menu_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'aria-label=' not in tag:
            lang_en = bool(re.search(r'<html[^>]+lang="en', text, re.I))
            label = 'Open navigation' if lang_en else '開啟導覽'
            tag = tag[:-1] + f' aria-label="{label}">'
        return tag
    text = re.sub(r'<button\b[^>]*class="[^"]*menu-toggle[^"]*"[^>]*>', menu_repl, text, count=1, flags=re.I)

    text = re.sub(
        r'<img\b[^>]*src="(?:https://github\.com/yoya9933\.png|/assets/avatar-fallback\.svg)"[^>]*>',
        lambda match: ensure_github_avatar(match.group(0)),
        text,
        flags=re.I,
    )

    text = re.sub(
        rf'(?P<prefix>(?:\.\./)*)assets/projects/(?P<name>{PROJECT_SLUG_PATTERN})\.webp',
        r'\g<prefix>assets/projects/snapshots/\g<name>.webp',
        text,
        flags=re.I,
    )

    if '<title>404' in text and 'assets/main.js' not in text:
        text = text.replace('</body>', '<script src="/assets/main.js" defer></script></body>', 1)
    return text


def main() -> None:
    for path in sorted(SITE.rglob('*.html')):
        path.write_text(ensure_runtime(path.read_text(encoding='utf-8')), encoding='utf-8')
    print(f'Applied dark runtime, GitHub avatar and snapshot routing for {len(PROJECT_SLUGS)} projects')


if __name__ == '__main__':
    main()
