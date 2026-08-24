from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


def ensure_runtime(text: str) -> str:
    # Portfolio is intentionally dark-only. Remove legacy theme toggles/bootstrap
    # and force the published document into the single visual system.
    text = re.sub(r'<script\s+data-theme-bootstrap>.*?</script>', '', text, flags=re.I | re.S)
    text = re.sub(r'<button\b[^>]*data-theme-toggle[^>]*>.*?</button>', '', text, flags=re.I | re.S)
    text = re.sub(r'<html([^>]*)\sdata-theme="[^"]*"([^>]*)>', r'<html\1 data-theme="dark"\2>', text, count=1, flags=re.I)
    if 'data-theme="dark"' not in text:
        text = re.sub(r'<html([^>]*)>', r'<html\1 data-theme="dark">', text, count=1, flags=re.I)

    if 'name="theme-color"' in text:
        text = re.sub(r'<meta\s+name="theme-color"\s+content="[^"]*"[^>]*>', '<meta name="theme-color" content="#050b12">', text, count=1, flags=re.I)
    else:
        text = text.replace('</head>', '<meta name="theme-color" content="#050b12"></head>', 1)

    # Load the final editorial design layer on every page, including cases/contact/404.
    if 'redesign.css' not in text:
        depth = 0
        match = re.search(r'<link[^>]+href="([^"]*assets/styles\.css)"', text, re.I)
        if match:
            href = match.group(1)
            prefix = href[: href.rfind('assets/styles.css')]
            redesign = prefix + 'assets/redesign.css'
        else:
            redesign = '/assets/redesign.css'
        text = text.replace('</head>', f'<link rel="stylesheet" href="{redesign}"></head>', 1)

    def menu_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if 'aria-label=' not in tag:
            lang_en = bool(re.search(r'<html[^>]+lang="en', text, re.I))
            label = 'Open navigation' if lang_en else '開啟導覽'
            tag = tag[:-1] + f' aria-label="{label}">'
        return tag
    text = re.sub(r'<button\b[^>]*class="[^"]*menu-toggle[^"]*"[^>]*>', menu_repl, text, count=1, flags=re.I)

    # Keep GitHub avatar primary, with local fallback if the remote image is unavailable.
    text = re.sub(
        r'<img\s+src="https://github\.com/yoya9933\.png"([^>]*)>',
        r'<img src="https://github.com/yoya9933.png"\1 data-avatar-fallback="/assets/avatar-fallback.svg" referrerpolicy="no-referrer">',
        text,
        flags=re.I,
    )

    if '<title>404' in text and 'assets/main.js' not in text:
        text = text.replace('</body>', '<script src="/assets/main.js" defer></script></body>', 1)
    return text


def main() -> None:
    for path in sorted(SITE.rglob('*.html')):
        path.write_text(ensure_runtime(path.read_text(encoding='utf-8')), encoding='utf-8')
    print('Applied dark-only runtime, editorial CSS and avatar fallback')


if __name__ == '__main__':
    main()
