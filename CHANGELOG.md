# Changelog

網站版本遵循 Semantic Versioning（SemVer）：`MAJOR.MINOR.PATCH`。

## v1.6.2 — 2026-08-31

Chess Product UI Patch：重新整理楚河棋局 Case Study 的產品主視覺，讓大型木質棋盤圖片更自然地融入深色 Portfolio 版面。

- 中英文 Chess Case Study 的 Product 區塊改為專用 product-window showcase，不再把大型主視覺直接浮在內容欄。
- 保留原本木質棋盤與品牌畫面，但加入深色產品框、title bar 與較克制的說明層級，和前面的 Metrics / Architecture / Engineering 區塊保持一致。
- 桌面版限制圖片展示高度與比例，避免主視覺壓過工程內容；手機版使用更短的 viewport，降低長頁面負擔。
- 新增 `LIVE PRODUCT · MULTIPLAYER WEB` 標籤與補充說明，明確把視覺展示和多人同步、重連、持久化等工程成果區分開來。
- 沿用 v1.6.1 的 showcase 語言，使 Buoy Runtime 與 Chess Product 在不同內容類型下仍共享一致的 Portfolio 視覺系統。

## v1.6.1 — 2026-08-31

Buoy Runtime UI Patch：重新整理浮標 Case Study 的實際 Streamlit 執行畫面，讓大面積白底截圖與深色 Portfolio 視覺更協調。

- 中英文 Buoy Case Study 的 Runtime UI 改為專用 product-window showcase，不再直接把白底截圖鋪滿內容欄。
- 截圖加入深色框架、runtime title bar 與更克制的說明層級，和 Metrics / Architecture 區塊維持一致的視覺語言。
- 桌面版限制 runtime capture 的展示高度並聚焦畫面頂部實際功能區，減少無內容白色區域的視覺重量。
- 手機版使用較短的 capture viewport 與更緊湊的 frame spacing，避免 Case Study 被單張截圖拉得過長。
- 保留原始 Streamlit runtime 截圖與其可驗證來源，不以重新設計的 mockup 取代實際產品畫面。

## v1.6.0 — 2026-08-31

Neon Arena Case Study：將即時多人德州撲克正式加入第五個 Selected Work，補上雙語案例、公開 Demo、媒體擷取與作品清單整合。

- 首頁 Selected Work 由四個擴充為五個，新增 `Neon Arena｜即時多人德州撲克`。
- 新增中英文 Neon Arena Case Study，聚焦 2–6 人即時多人、伺服器權威狀態、私牌隔離、18 秒回合、斷線重連與主池／邊池結算。
- Neon Arena 使用 Cloudflare Workers、Durable Objects、Hibernation WebSocket 與 SQLite 的多人架構；Portfolio 明確標示目前仍是朋友局測試版。
- 首頁與 Case Study 只連公開 Live Demo；原始 repository 為 private，因此不顯示 GitHub CTA，也不在公開網站暴露 private repository 名稱。
- 建置優先擷取公開 Neon Arena Demo 作為作品預覽，若外站暫時無法擷取則回退至 Portfolio repository 內已審核的霓虹牌桌 SVG。
- Demo 明確標示全部籌碼皆為虛擬數字，沒有付費、儲值或兌現；未把 commit/reveal、正式帳號或跨裝置身分恢復等未完成功能寫成既有能力。
- 五張 Selected Work 在桌面維持一張 lead card 加四張 2×2 卡片的平衡版面，並同步進首頁 JSON-LD、sitemap 與 CI manifest 驗證。

## v1.5.1 — 2026-08-29

Hero Avatar Patch：依照網站視覺偏好，將首頁右側的 `Y` 品牌 placeholder 恢復成原本 GitHub 帳號頭像。

- 首頁中英文 Hero 重新使用 `https://github.com/yoya9933.png` 作為頭像來源。
- `enhance_runtime.py` 不再把 GitHub 頭像強制替換成 `/assets/avatar-fallback.svg`。
- GitHub 頭像保留固定尺寸、async decoding 與 `no-referrer`，避免影響版面穩定性。
- Performance gate 改為驗證 GitHub 頭像存在，並防止 `Y` placeholder 再次成為首頁 Hero 主圖。

## v1.5.0 — 2026-08-29

Release / Observability 2.0：讓版本、部署產物與正式站狀態可以互相核對，並在發布後自動確認 production 已切到正確 commit。

- 正式 Release 改為 immutable version identity：若既有 Git tag 已鎖定其他 commit，同版本的新部署會直接失敗並要求升版。
- `/version.json` 新增 GitHub Actions workflow、run ID、run number、ref 與 workflow run URL，部署問題可直接追到來源執行紀錄。
- 新增 `/build-manifest.json`，列出部署檔案數量、大小與 SHA-256；CI 會重新計算並驗證 artifact 完整性。
- 新增 observability build gate，確認版本、commit、workflow metadata 與 build manifest 一致。
- GitHub Pages 部署完成後執行 production smoke test，驗證正式站 `/version.json`、`/build-manifest.json` 與核心頁面都已切到同一個版本與 commit。
- 股東紀念品 CMS 首頁卡片恢復使用 `sharegift.tw` 公開首頁快照；若公開站暫時無法擷取，會自動使用已審核的架構圖 fallback，且不存取登入後台。

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
