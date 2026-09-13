from __future__ import annotations

import base64
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from common import SITE


CSP_META_RE = re.compile(
    r'<meta\s+http-equiv=["\']Content-Security-Policy["\'][^>]*>',
    re.IGNORECASE,
)
INLINE_SCRIPT_RE = re.compile(
    r'<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
CHARSET_META_RE = re.compile(r'<meta\s+charset=["\'][^"\']+["\'][^>]*>', re.IGNORECASE)


def sha256_source(body: str) -> str:
    digest = hashlib.sha256(body.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def build_policy(text: str) -> str:
    hashes = sorted({sha256_source(body) for body in INLINE_SCRIPT_RE.findall(text)})
    script_sources = " ".join(["'self'", *hashes])
    directives = [
        "default-src 'none'",
        "base-uri 'none'",
        "object-src 'none'",
        f"script-src {script_sources}",
        "script-src-attr 'none'",
        "style-src 'self'",
        "style-src-attr 'none'",
        "img-src 'self'",
        "font-src 'self'",
        "connect-src 'none'",
        "media-src 'none'",
        "frame-src 'none'",
        "worker-src 'none'",
        "manifest-src 'self'",
        "form-action 'none'",
        "upgrade-insecure-requests",
    ]
    return "; ".join(directives)


def inject_meta(text: str) -> str:
    text = CSP_META_RE.sub("", text)
    policy = build_policy(text)
    meta = f'<meta http-equiv="Content-Security-Policy" content="{policy}">'
    charset = CHARSET_META_RE.search(text)
    if charset:
        return text[: charset.end()] + meta + text[charset.end() :]
    head = re.search(r'<head\b[^>]*>', text, flags=re.IGNORECASE)
    if not head:
        raise RuntimeError("HTML document has no <head>")
    return text[: head.end()] + meta + text[head.end() :]


ALLOWED_EXTERNAL = {
    "img": set(), "script": set(), "style": set(), "font": set(),
    "connect": set(), "media": set(), "frame": set(), "manifest": set(),
}
NETWORK_JS_RE = re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon)\b")


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.resources: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value for key, value in attrs if value is not None}
        tag = tag.lower()
        if tag == "img" and data.get("src"):
            self.resources.append(("img", data["src"]))
        elif tag == "script" and data.get("src"):
            self.resources.append(("script", data["src"]))
        elif tag == "link" and data.get("href"):
            rel = {part.lower() for part in data.get("rel", "").split()}
            if "stylesheet" in rel:
                self.resources.append(("style", data["href"]))
            elif "manifest" in rel:
                self.resources.append(("manifest", data["href"]))
            elif rel & {"icon", "apple-touch-icon", "mask-icon"}:
                self.resources.append(("img", data["href"]))
        elif tag in {"audio", "video", "source"} and data.get("src"):
            self.resources.append(("media", data["src"]))
        elif tag == "video" and data.get("poster"):
            self.resources.append(("img", data["poster"]))
        elif tag in {"iframe", "frame"} and data.get("src"):
            self.resources.append(("frame", data["src"]))


def check() -> int:
    errors: list[str] = []
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("No published HTML found", file=sys.stderr)
        return 2

    for path in pages:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(SITE)
        metas = CSP_META_RE.findall(text)
        if len(metas) != 1:
            errors.append(f"{rel}: expected exactly one CSP meta, found {len(metas)}")
            continue
        meta = metas[0]
        content_match = re.search(r'content="([^"]*)"', meta, flags=re.IGNORECASE)
        if not content_match:
            errors.append(f"{rel}: CSP meta has no content attribute")
            continue
        actual = content_match.group(1)
        without_meta = CSP_META_RE.sub("", text)
        if actual != build_policy(without_meta):
            errors.append(f"{rel}: CSP policy does not match generated strict policy")
        if "'unsafe-inline'" in actual or "'unsafe-eval'" in actual or " *" in actual:
            errors.append(f"{rel}: CSP contains an unsafe broad source")
        positions = [pos for pos in (text.lower().find("<link"), text.lower().find("<script")) if pos >= 0]
        if positions and text.find(meta) > min(positions):
            errors.append(f"{rel}: CSP meta appears after a loadable head resource")
        if re.search(r'\son[a-z]+\s*=', text, flags=re.IGNORECASE):
            errors.append(f"{rel}: inline event handler conflicts with script-src-attr none")
        if re.search(r'\sstyle\s*=', text, flags=re.IGNORECASE):
            errors.append(f"{rel}: inline style attribute conflicts with style-src-attr none")

        parser = ResourceParser()
        parser.feed(text)
        for kind, value in parser.resources:
            parsed = urlparse(value)
            host = (parsed.hostname or "").lower() if parsed.scheme in {"http", "https"} else None
            if host and host not in ALLOWED_EXTERNAL[kind]:
                errors.append(f"{rel}: unapproved external {kind} resource: {value}")

    for css in sorted(SITE.rglob("*.css")):
        text = css.read_text(encoding="utf-8")
        if re.search(r'@import\s+(?:url\()?\s*["\']?https?://', text, flags=re.IGNORECASE):
            errors.append(f"{css.relative_to(SITE)}: external CSS import is not allowed")
        if re.search(r'url\(\s*["\']?https?://', text, flags=re.IGNORECASE):
            errors.append(f"{css.relative_to(SITE)}: external CSS URL is not allowed")
    for js in sorted(SITE.rglob("*.js")):
        if NETWORK_JS_RE.search(js.read_text(encoding="utf-8")):
            errors.append(f"{js.relative_to(SITE)}: runtime network API detected while connect-src is none")

    if errors:
        print("CSP checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CSP checks passed: self-hosted scripts/styles/images/fonts; connect-src none")
    return 0


def main() -> None:
    if "--check" in sys.argv[1:]:
        raise SystemExit(check())
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        raise RuntimeError("no published HTML files found")
    for path in pages:
        text = path.read_text(encoding="utf-8")
        path.write_text(inject_meta(text), encoding="utf-8")
    print(f"Applied strict CSP meta policy to {len(pages)} HTML pages")


if __name__ == "__main__":
    main()
