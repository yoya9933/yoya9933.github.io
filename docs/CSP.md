# Content Security Policy

This portfolio is published as a static GitHub Pages site. The production CSP is generated per HTML page by `scripts/apply_csp.py` and validated by `scripts/check_csp.py`.

## Runtime resource inventory

Resources that the browser actually loads while rendering the portfolio:

| Resource type | Runtime source | CSP source |
| --- | --- | --- |
| HTML, CSS, JavaScript | `https://yoya9933.page` | `'self'` |
| Project images, icons, OG assets, manifest, CV | `https://yoya9933.page` | `'self'` |
| Hero profile image | `https://github.com/yoya9933.png` | `https://github.com` |
| GitHub avatar redirect target | GitHub avatar CDN | `https://avatars.githubusercontent.com` |
| Fonts | Local/system font stacks only; no web-font request | `'self'` only |
| Runtime API / XHR / fetch / SSE / WebSocket | None | `connect-src 'none'` |
| iframe / frame | None | `frame-src 'none'` |
| audio / video | None | `media-src 'none'` |
| Worker / Service Worker | None | `worker-src 'none'` |

External GitHub repositories, public demos, award evidence pages, `sharegift.tw`, and Workers URLs are ordinary navigation links. They are not fetched as page resources and therefore are not added to CSP fetch-source allowlists.

Two public sites are used only during CI media generation: `https://sharegift.tw/` and `https://neon-arena-holdem.sean8411.workers.dev/`. Headless Chrome captures those pages during the build and stores the resulting image in the deployment artifact. A visitor's browser does not connect to those hosts merely by opening the portfolio.

## Enforced meta policy

Each published HTML page receives a policy equivalent to:

```text
default-src 'self';
base-uri 'self';
object-src 'none';
script-src 'self' <per-page SHA-256 hashes for inline JSON-LD>;
script-src-attr 'none';
style-src 'self';
style-src-attr 'none';
img-src 'self' https://github.com https://avatars.githubusercontent.com;
font-src 'self';
connect-src 'none';
media-src 'none';
frame-src 'none';
worker-src 'none';
manifest-src 'self';
form-action 'self';
upgrade-insecure-requests
```

`'unsafe-inline'`, `'unsafe-eval'`, broad `https:` sources and wildcard `*` sources are intentionally not allowed. Inline JSON-LD is permitted with exact SHA-256 hashes generated from the final rendered page.

## Meta CSP limitation

GitHub Pages does not provide repository-controlled arbitrary response headers, so the policy is currently delivered with `<meta http-equiv="Content-Security-Policy">` near the start of `<head>`.

`frame-ancestors` cannot be enforced from a CSP meta element. If the site is later served through a layer that can set HTTP response headers (for example a proxied edge service), add the response header form of the policy and include:

```text
frame-ancestors 'none'
```

The HTTP-header policy should then become authoritative and the meta policy can remain as defense in depth or be removed after verification.

## Manual verification after deployment

Open the production homepage, both locale homepages, a Case Study, and the Event Check-in demo. In browser developer tools, check **Console** for messages containing `Content Security Policy`, `CSP`, `Refused to load`, or `Refused to execute`.

Also verify that:

- the GitHub avatar renders;
- CSS and navigation JavaScript still work;
- project screenshots/icons render;
- structured-data markup remains in the generated HTML;
- the Event Check-in demo remains interactive.

If a future feature adds an external script, stylesheet, font, image host, API, WebSocket, iframe, media file, or worker, update the inventory and CSP deliberately rather than broadening `default-src`.
