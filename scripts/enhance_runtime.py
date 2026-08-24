from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

BOOTSTRAP = """<script data-theme-bootstrap>(function(){try{var s=localStorage.getItem('portfolioTheme');var l=window.matchMedia('(prefers-color-scheme: light)').matches;document.documentElement.dataset.theme=s||(l?'light':'dark')}catch(e){}})();</script>"""


def ensure_runtime(text: str) -> str:
    # Apply the saved/system theme before stylesheets paint to avoid a light/dark flash.
    if "data-theme-bootstrap" not in text:
        text = text.replace("<head>", "<head>" + BOOTSTRAP, 1)

    # Keep browser chrome aligned with the default theme; main.js updates this on toggle.
    if 'name="theme-color"' not in text:
        text = text.replace("</head>", '<meta name="theme-color" content="#07111f"></head>', 1)

    # Give controls useful accessible names in the initial HTML, before deferred JS executes.
    def menu_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "aria-label=" not in tag:
            lang_en = bool(re.search(r'<html[^>]+lang="en', text, re.I))
            label = "Open navigation" if lang_en else "開啟導覽"
            tag = tag[:-1] + f' aria-label="{label}">'
        return tag
    text = re.sub(r'<button\b[^>]*class="[^"]*menu-toggle[^"]*"[^>]*>', menu_repl, text, count=1, flags=re.I)

    def theme_repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "aria-label=" not in tag:
            tag = tag[:-1] + ' aria-label="Switch color theme">'
        if "aria-pressed=" not in tag:
            tag = tag[:-1] + ' aria-pressed="false">'
        return tag
    text = re.sub(r'<button\b[^>]*data-theme-toggle[^>]*>', theme_repl, text, flags=re.I)

    # Keep the GitHub avatar, but guarantee a local fallback if the remote image is unavailable.
    text = re.sub(
        r'<img\s+src="https://github\.com/yoya9933\.png"([^>]*)>',
        r'<img src="https://github.com/yoya9933.png"\1 data-avatar-fallback="/assets/avatar-fallback.svg" referrerpolicy="no-referrer">',
        text,
        flags=re.I,
    )

    # Make the 404 page use the same runtime behavior as the rest of the site.
    if '<title>404' in text and 'assets/main.js' not in text:
        text = text.replace("</body>", '<script src="/assets/main.js" defer></script></body>', 1)
    return text


def main() -> None:
    for path in sorted(SITE.rglob("*.html")):
        path.write_text(ensure_runtime(path.read_text(encoding="utf-8")), encoding="utf-8")
    print("Enhanced theme bootstrap, runtime accessibility and avatar fallback")


if __name__ == "__main__":
    main()
