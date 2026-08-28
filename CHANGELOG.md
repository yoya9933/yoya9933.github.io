# Changelog

網站版本遵循 Semantic Versioning（SemVer）：`MAJOR.MINOR.PATCH`。

## v1.4.0 — 2026-08-29

Performance & Quality：把圖片尺寸、第三方依賴、鍵盤操作與 Lighthouse 品質門檻納入可驗證的 build invariants。

- 專案圖片在 build 時從實際 PNG 產物取得 intrinsic width / height，避免以固定 1200×720 猜測尺寸造成 layout shift。
- Hero avatar 改為本地 `Yoya` 品牌 SVG，不再在頁面載入 GitHub avatar，減少第三方 waterfall 與隱私依賴。
- 新增全站 `:focus-visible` 鍵盤 focus 樣式與 `prefers-reduced-motion` 降低動態效果規則。
- 新增 `check_performance.py`，驗證專案圖片尺寸、async decoding、本地 avatar 與 accessibility CSS 不會在後續 build 遺失。
- Lighthouse 仍採 3 次 median，但門檻提升為 Performance ≥ 75、Accessibility ≥ 95、Best Practices ≥ 90、SEO ≥ 95。

## v1.3.0 — 2026-08-29

Case Study 2.0：把作品頁從功能清單提升成可快速判讀的工程案例，同時保留可驗證證據與已知限制。

- 每篇中英文 Case Study 新增 Role / Scope / Status / Stack / Year，讓閱讀者快速理解實際工作範圍。
- 新增 Problem / Decision / Evidence / Next 標準化工程脈絡區，說明問題、技術判斷、可核對證據與下一步。
- Case Study framing 全部由 `data/projects.json` 驅動，中英文共用同一份專案事實來源。
- EventOps 明確保留公開 Demo 只有虛構資料的隱私邊界；AI Media Pipeline 明確標示 quality threshold 尚未被主流程強制為 publish blocker。
- 新增 `check_case_studies.py` build gate，避免後續更新遺漏標準欄位或把未完成能力寫成既有功能。

## v1.2.0 — 2026-08-29

Portfolio Architecture 2.0：把作品的公開資料、首頁 section、Case visual 與 media build plan 收斂到同一份 manifest。

- `data/projects.json` 新增中英文首頁標題、Additional System 文案與各專案 media build plan。
- `render_projects.py` 改為整段產生 Selected Work / Additional System，不再依賴舊文案逐字 replace 或卡片 closing marker。
- 專案 Card、Case Study actions、首頁 JSON-LD、sitemap 與可選 Case visual 都由同一份 project manifest 產生。
- 新增 `build_project_media.py`，統一處理 tracked snapshots、本機 synthetic demo capture 與 SVG architecture render；新增專案不再需要把 media 流程硬編碼進 shell script。
- Shareholder CMS 的 Case visual/caption 移入 manifest，不再在 renderer 裡用專案 slug 特判。
- 將 `project-cta-fix.css` 與 `header-nav-fix.css` 收斂為正式 `portfolio-layout.css` module，移除一次性 patch 檔案。

## v1.1.1 — 2026-08-29

Stability Patch：降低部署與品質檢查的偶發失敗，並移除外部網站對 production build 的依賴。

- GitHub Actions 升級到目前支援 Node 24 的主要版本，移除既有 Node 20 deprecation 技術債。
- Lighthouse 改為每頁執行 3 次並使用 median 判定，降低單次量測波動造成的 false negative。
- Site Quality 無論成功或失敗都保留 Lighthouse report artifact 7 天，方便診斷。
- 股東紀念品 CMS 的 production build 改用 repository 內已審核、可重現的架構 visual，不再於每次部署即時存取 `sharegift.tw`。
- 保留既有版本、SEO、隱私與 deployment artifact 驗證。

## v1.1.0 — 2026-08-29

建立完整的網站 Release Management 流程。

- 建立 Git tag 與 GitHub Release，讓正式版本固定對應到 Git commit。
- 新增 `/changelog/` 網站更新紀錄頁，並由 `CHANGELOG.md` 自動產生。
- GitHub Actions 在部署前驗證 `VERSION` / `CHANGELOG.md`，並自動建立缺少的 tag / release。
- `/version.json` 新增含時區的 build time 與 `production` / `ci` / `local` environment 資訊。
- README 加入版本、Release & Deploy、Site Quality 與正式網站 Badge。
- CSS / JavaScript 靜態資產加入以網站版本為基準的 cache-busting query。
- Changelog 提供相鄰正式版本的 GitHub Compare 連結。

## v1.0.0 — 2026-08-29

第一個正式追蹤的 Portfolio 網頁版本。

- 以 `data/projects.json` 集中管理作品名稱、順序、Demo、GitHub、標籤與 Case Study 路徑。
- 中英文首頁包含四個 Selected Work 與一個 Additional System。
- 提供 Case Study、公開 Demo、雙語 CV、SEO / JSON-LD、sitemap 與 GitHub Pages CI/CD。
- 加入網頁版本資訊：Footer、HTML metadata、`/version.json` 與 Git commit 對應。

之後網站內容或樣式的小幅修正增加 PATCH；新增向下相容功能增加 MINOR；若網站資訊架構或公開介面有不相容的大幅變更則增加 MAJOR。
