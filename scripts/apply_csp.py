from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

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
        "img-src 'self' https://github.com https://avatars.githubusercontent.com",
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


def main() -> None:
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        raise RuntimeError("no published HTML files found")
    for path in pages:
        text = path.read_text(encoding="utf-8")
        path.write_text(inject_meta(text), encoding="utf-8")
    print(f"Applied strict CSP meta policy to {len(pages)} HTML pages")


if __name__ == "__main__":
    main()
