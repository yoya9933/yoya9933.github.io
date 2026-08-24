from pathlib import Path

site = Path(__file__).resolve().parents[1] / "_site"

replacements = {
    "en/index.html": [('href="/contact/"', 'href="/en/contact/"')],
    "contact/index.html": [('href="../en/"', 'href="../en/contact/"')],
}

for rel, pairs in replacements.items():
    path = site / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

print("Normalized localized contact links")
