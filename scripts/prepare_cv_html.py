from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / "assets" / "Yoya_CV_source.html").read_text(encoding="utf-8")

replacements = {
'''      <article class="project">
        <div class="project-top"><h3>NCKU Return OS · Credit & Course Decision Tool</h3><span class="badge">DECISION TOOL</span></div>
        <ul>
          <li>Built an offline-first 135-credit decision tool for graduation gaps, prerequisites, timetable conflicts, risk / necessity scores, and A/B/C course plans.</li>
          <li>Uses LocalStorage for persistence with JSON backup and CSV export for portable planning.</li>
        </ul>
        <div class="tech"><span>HTML</span><span>CSS</span><span>JavaScript</span><span>LocalStorage</span></div>
      </article>''':
'''      <article class="project">
        <div class="project-top"><h3>Event Check-in & Operations System</h3><span class="badge">FULL-STACK OPS</span></div>
        <ul>
          <li>Built a QR check-in workflow with attendee lookup, live attendance / seating metrics, five operational filter dimensions, and CSV export.</li>
          <li>Separated the private production system from a public read-only demo that uses fully synthetic attendee, seat, and token data.</li>
        </ul>
        <div class="tech"><span>TypeScript</span><span>Next.js</span><span>REST API</span><span>Cloudflare D1</span><span>Drizzle</span></div>
      </article>''',
'''      <article class="project">
        <div class="project-top"><h3>NCKU Return OS · 學分與修課決策工具</h3><span class="badge">DECISION TOOL</span></div>
        <ul>
          <li>把 135 學分畢業規則、先修、衝堂、必要性 / 風險分數與 A/B/C 三種修課方案整合成離線決策工具。</li>
          <li>使用 LocalStorage 保存狀態，並支援 JSON 備份與 CSV 匯出，方便持續更新。</li>
        </ul>
        <div class="tech"><span>HTML</span><span>CSS</span><span>JavaScript</span><span>LocalStorage</span></div>
      </article>''':
'''      <article class="project">
        <div class="project-top"><h3>活動報到與現場營運系統</h3><span class="badge">FULL-STACK OPS</span></div>
        <ul>
          <li>整合 QR 報到、名單查詢、即時簽到 / 入席統計、五維營運篩選與 CSV 匯出。</li>
          <li>將正式 private 系統與公開唯讀 Demo 分離；展示版只使用虛構姓名、機構、座位與 token。</li>
        </ul>
        <div class="tech"><span>TypeScript</span><span>Next.js</span><span>REST API</span><span>Cloudflare D1</span><span>Drizzle</span></div>
      </article>''',
}
for old, new in replacements.items():
    if old not in source:
        raise SystemExit("Expected CV project block was not found")
    source = source.replace(old, new, 1)

qr_uri = Path("/tmp/portfolio-qr.png").as_uri()
source, count = re.subn(r'src="data:image/png;base64,[^"]+"', f'src="{qr_uri}"', source)
if count != 2:
    raise SystemExit(f"Expected to replace 2 embedded QR images, replaced {count}")
Path("/tmp/Yoya_CV_print.html").write_text(source, encoding="utf-8")
