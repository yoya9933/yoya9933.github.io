from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
REPO_URL = "https://github.com/yoya9933/-------_202601221138_XY_Propose_Minutes"
LIVE_URL = "https://sharegift.tw/"

ZH_CARD = f'''<article class="project-card" data-project="shareholder-cms"><div class="project-media"><img src="assets/projects/shareholder-cms.webp" alt="股東紀念品服務與 CMS 平台公開網站首頁截圖" loading="lazy"></div><div class="project-topline"><span class="project-number">04</span><span class="project-badge">BUSINESS CMS</span></div><h3>股東紀念品服務與 CMS 平台</h3><p>整合公開服務網站、商品與公告後台、Supabase 認證、PostgreSQL 與雲端圖片儲存的商業網站。</p><ul class="tags"><li>Vue 3 / TypeScript</li><li>Supabase Auth + RLS</li><li>CMS + Storage</li></ul><div class="project-links"><a class="project-primary" href="projects/shareholder-cms/">看 Case Study</a><a href="{LIVE_URL}" target="_blank">Live Site ↗</a><a href="{REPO_URL}" target="_blank">GitHub ↗</a></div></article>'''

EN_CARD = f'''<article class="project-card" data-project="shareholder-cms"><div class="project-media"><img src="../assets/projects/shareholder-cms.webp" alt="Shareholder Gift Service and CMS public website screenshot" loading="lazy"></div><div class="project-topline"><span class="project-number">04</span><span class="project-badge">BUSINESS CMS</span></div><h3>Shareholder Gift Service & CMS Platform</h3><p>A maintainable service website with product and announcement CMS, Supabase authentication, PostgreSQL and cloud image storage.</p><ul class="tags"><li>Vue 3 / TypeScript</li><li>Supabase Auth + RLS</li><li>CMS + Storage</li></ul><div class="project-links"><a class="project-primary" href="projects/shareholder-cms/">Case Study</a><a href="{LIVE_URL}" target="_blank">Live Site ↗</a><a href="{REPO_URL}" target="_blank">GitHub ↗</a></div></article>'''


def add_static_card(path: Path, *, english: bool) -> None:
    text = path.read_text(encoding="utf-8")
    card = EN_CARD if english else ZH_CARD

    if 'data-project="shareholder-cms"' not in text:
        text = text.replace('<div class="projects-grid">', '<div class="projects-grid has-four-selected">', 1)
        marker = '<section class="section shell" id="additional-work">'
        marker_pos = text.find(marker)
        if marker_pos < 0:
            raise RuntimeError(f"additional-work marker missing from {path}")
        projects_close = text.rfind('</div></section>', 0, marker_pos)
        if projects_close < 0:
            raise RuntimeError(f"projects closing marker missing from {path}")
        text = text[:projects_close] + card + text[projects_close:]
    else:
        text = text.replace('<div class="projects-grid">', '<div class="projects-grid has-four-selected">', 1)

    if english:
        text = text.replace(
            'Three projects across engineering data and AI, a multiplayer web product, and a field-ready full-stack operations workflow.',
            'Four selected projects spanning engineering data and AI, multiplayer web, field operations, and a maintainable business CMS.',
        )
        text = text.replace(
            '{"@type":"ListItem","position":4,"url":"https://yoya9933.page/en/projects/ai-media-pipeline/","name":"Reliable AI Media Automation Pipeline"}',
            '{"@type":"ListItem","position":4,"url":"https://yoya9933.page/en/projects/shareholder-cms/","name":"Shareholder Gift Service & CMS Platform"}',
        )
    else:
        text = text.replace(
            '三個代表專案對應工程資料與 AI、多人 Web 產品，以及真實活動現場的全端營運流程。',
            '四個代表專案涵蓋工程資料與 AI、多人 Web、活動現場營運，以及可持續維護的商業 CMS。',
        )
        text = text.replace(
            '{"@type":"ListItem","position":4,"url":"https://yoya9933.page/projects/ai-media-pipeline/","name":"Reliable AI Media Automation Pipeline"}',
            '{"@type":"ListItem","position":4,"url":"https://yoya9933.page/projects/shareholder-cms/","name":"股東紀念品服務與 CMS 平台"}',
        )

    path.write_text(text, encoding="utf-8")


def update_case(path: Path, *, english: bool) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace('https://yoya9933.page/assets/projects/shareholder-cms.svg', 'https://yoya9933.page/assets/projects/shareholder-cms.png')
    text = text.replace('../../assets/projects/shareholder-cms.svg', '../../assets/projects/shareholder-cms.webp')

    if LIVE_URL not in text:
        label = 'Live Site ↗' if english else '開啟公開網站 ↗'
        text = text.replace(
            '<div class="case-actions">',
            f'<div class="case-actions"><a class="button primary" href="{LIVE_URL}" target="_blank">{label}</a>',
            1,
        )

    if english:
        text = text.replace('Shareholder Gift Service and CMS architecture preview', 'Shareholder Gift Service public website screenshot')
        caption = 'The deployment captures the public homepage when reachable; a deterministic architecture visual is used only as a fallback. No authenticated admin page is captured.'
    else:
        text = text.replace('股東紀念品服務與 CMS 平台架構示意', '股東紀念品服務公開網站首頁截圖')
        caption = '部署時優先擷取公開正式網站首頁；若外部網站暫時無法連線才使用架構圖備援，不會擷取需要登入的管理後台。'

    text = re.sub(r'<figcaption>.*?</figcaption>', f'<figcaption>{caption}</figcaption>', text, count=1, flags=re.DOTALL)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    add_static_card(SITE / 'index.html', english=False)
    add_static_card(SITE / 'en/index.html', english=True)
    update_case(SITE / 'projects/shareholder-cms/index.html', english=False)
    update_case(SITE / 'en/projects/shareholder-cms/index.html', english=True)
    print('Published shareholder CMS as a static fourth selected project')


if __name__ == '__main__':
    main()
