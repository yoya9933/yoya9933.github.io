# Changelog

網站版本遵循 Semantic Versioning（SemVer）：`MAJOR.MINOR.PATCH`。

## v1.7.8 — 2026-09-12

Case Study Screenshot Layout Fix：修正 Event Check-in Case Study 的公開 Demo 截圖在桌面窄欄位被固定 intrinsic height 與 `object-fit: cover` 橫向裁切的問題。

- 沿用既有 Case Study 圖片與 build-time intrinsic `width` / `height`，不重新截圖、不新增 JavaScript 或 dependency。
- 共用 `.case-shot img` 明確使用 `height: auto`，讓一般 Case Study 截圖維持原始比例並完整顯示左右內容。
- Buoy runtime 與 Chess product 既有專用 showcase 仍保留各自明確的固定高度與裁切規則，不受這次 generic 修正影響。

## v1.7.7 — 2026-09-12

EventOps Evidence & CV Cleanup：補上活動報到系統實際投入 2026 臺灣綜合大學系統新進教師專業知能研習營的使用證據，並同步更新中英履歷與精簡 CV build。

- Event Check-in Case Study 明確限定本人負責後端實作，補上 2026-08-28 成大活動的官方公開來源，正式 repository / database 仍維持 private，公開 Demo 僅使用虛構資料。
- 中英雙語履歷以 Event Check-in 實際活動後端取代已退役的 NCKU Return OS，並將中文 alias 統一為 `Yu`。
- `assets/Yu_CV_source.html` 直接保存最終正確內容，不再由 build-time regex 替換專案。
- CV QR 改用瀏覽器原生相對路徑解析 `/tmp/portfolio-qr.png`；刪除兩份內嵌 base64 與 `scripts/prepare_cv_html.py`。
- `scripts/build_site.sh` 成為網站驗證單一入口，GitHub Actions 不再重複執行同一批 checker；CSP、privacy、accessibility、Lighthouse、artifact integrity、release identity 與 production smoke test 全部保留。

## v1.7.6 — 2026-09-11

Profile Crop Fix：重新裁切首頁 Hero 個人照，保留頭頂上方留白，避免圓角方框切到頭髮。

- 直接替換既有 `assets/profile.jpg`，不增加 CSS hack、JavaScript、圖片 loader 或 dependency。
- 維持 320×320 本地 JPEG、既有 CSP 與圖片品質驗證。
- 這次修正的是圖片內容裁切，不再靠移動整個頭像區塊處理。

## v1.7.5 — 2026-09-11

Profile Position Patch：將首頁 Hero 的大頭照區塊往下移，改善照片在右側卡片內過度靠上的視覺重心。

- 沿用既有 `assets/profile.jpg`、HTML 與圖片品質，不重新裁切或壓縮照片。
- 直接在既有 CSS 加上最小的 `margin-top` 位移，不新增 JavaScript、dependency 或圖片處理流程。
- CSP、accessibility、Lighthouse 與既有圖片驗證維持不變。

## v1.7.4 — 2026-09-11

Brand Rename：將 Portfolio 對外品牌名稱統一改為 `Yu`，包含網站、SEO、Case Study、Contact、Release 文案與雙語履歷。

- 所有對外顯示的舊品牌名稱已改為 `Yu`，中英文頁面與 metadata 同步。
- 履歷 alias 改為 `Yu`，CV source / build output 改名為 `Yu_CV`，網站下載連結同步更新。
- GitHub 帳號 `yoya9933` 與正式網域 `yoya9933.page` 保持不變，因為它們是實際可用的技術識別與 URL。
- 不新增 dependency、redirect layer 或 alias abstraction；直接修改既有 source 與 build 路徑。

## v1.7.3 — 2026-09-11

Profile Image Quality Hotfix：改用原始上傳照片重新輸出高品質本地 JPEG，移除上一版救援縮圖造成的明顯模糊。

- `assets/profile.jpg` 直接由原始 428×592 照片重新輸出為高品質 JPEG，沿用既有圖片路徑、HTML、CSS 與 CSP。
- 不新增圖片 loader、第三方服務、AI 放大流程或 dependency；瀏覽器仍直接顯示既有本地靜態資產。
- 沿用 v1.7.2 的 JPEG 結構與最小尺寸 CI gate，避免損壞或尺寸不足的頭像再次通過部署。

## v1.7.2 — 2026-09-11

Visual Hotfix：修復正式站實際截圖暴露的首頁頭像破圖與 AI Media Automation 流程圖裁切問題，並補上最小必要的回歸檢查。

- 將損壞的 `assets/profile.jpg` 重新編碼為可正常解碼的本地 JPEG，沿用既有圖片路徑、HTML 與 CSP，不重新引入第三方頭像依賴。
- Additional System 的預覽圖片由 `object-fit: cover` 改為 `contain` 並置中，讓 AI Media Automation 的完整流程圖在桌面與手機版都不再被左右裁切。
- `check_performance.py` 新增 JPEG 結構與尺寸檢查，CI 會拒絕缺少 SOI / EOI、無有效 SOF 尺寸或過小的 Hero 頭像，避免「檔案存在但瀏覽器無法顯示」再次通過部署。
- 不新增套件、圖片 loader 或額外 render layer；修正仍沿用既有 build pipeline、local asset 與 performance gate。

## v1.7.1 — 2026-09-11

Portfolio Polish & Ponytail Cleanup：更新首頁個人照片與資訊順序，同時移除 dark-only 網站已不需要的 theme patch、legacy CSS 與第三方頭像 runtime 依賴。

- 首頁中英文改用 repository 內的 `assets/profile.jpg`，移除 GitHub avatar runtime request；CSP `img-src` 收緊為僅 `'self'`。
- 將「事蹟 / Achievements」移到 Selected Work 前方，並同步調整導覽與 section 編號。
- 移除 Hero 的 `$ build → test → improve_` 裝飾與對應 dead CSS。
- Contact、404、Buoy / Chess / Neon Arena 等 source HTML 直接固定 dark theme 與 theme-color，不再由 build-time regex 修補。
- `enhance_site.py` 刪除 theme runtime patch，只保留 SEO、accessibility、安全連結與 intrinsic image dimensions 等有價值的 build hardening。
- `p1.css` 刪除 legacy light-theme、theme-toggle 與 `has-four-selected` 規則；專案版面由既有 `.project-card.featured` 自然支援五張卡。
- 首頁由 `render_projects.py` / `data/projects.json` 直接產生專案內容，刪除 source 中失去意義的重複卡片 markup。
- CSP、privacy、Lighthouse、artifact integrity、release identity、production smoke test 與 menu accessibility checks 全部保留。

## v1.7.0 — 2026-09-10

Achievements：把既有首頁成果區擴充成完整的個人重要事蹟，保留公開可核對來源，同時納入競賽、學業表現、技術認證與自行車挑戰紀錄。

- 中文首頁將「成果」改為「事蹟」，完整列出競賽與挑戰、學業與校內表現、技術認證三類紀錄。
- 英文首頁同步提供相同內容，避免中英文履歷資訊落差。
- 保留 NODASS、高通台灣 AI 黑客松、臺灣海洋國際青年論壇既有公開證據連結；其他項目明確以個人紀錄列示，不假裝已有第三方驗證。
- 沿用既有 timeline / heading / reveal 元件，不新增資料層、JavaScript 或第三方依賴。

## v1.6.5 — 2026-09-03

Ponytail Cleanup II：繼續依照 YAGNI / reuse-first 原則，刪除只修單一硬編碼問題的腳本、重複 checker 與未引用資產，讓既有 build / validation 流程承擔同一份責任。

- 修正中文 Contact 原始頁面的英文版連結後，刪除只做兩個字串 replacement 的 `fix_locale_links.py`。
- 將 P2 SEO / accessibility 與 robots 驗證收進既有 `check_site.py`，刪除 `check_p2.py` 與 `check_robots.py`，保留原本必要的 SEO、noopener/noreferrer、skip-link、structured data 與 robots 檢查。
- 刪除根目錄 `sitemap.xml` 重複來源；正式 sitemap 只由 `render_projects.py` 依 manifest 產生。
- 刪除未被 build 或公開頁面引用的 `buoy-ui.svg`、`buoy-source.svg`、`chess-source.svg`。
- README / manifest 文件同步目前五個 Selected Work 與實際 lean build 流程。
- CSP、privacy、Lighthouse、artifact integrity、release identity 與 production smoke test 全部保留。

## v1.6.4 — 2026-09-03

Ponytail Cleanup：依照 DietrichGebert/ponytail 的 YAGNI / reuse-first 規則，移除已被既有 build 流程覆蓋的補丁層與重複部署資產，不改變公開網站功能。

- 刪除 `enhance_runtime.py`，把真正必要的 dark-mode / theme-color / GitHub avatar hardening 收進既有 `enhance_site.py`。
- 專案 WebP 只發布一份，不再同時保留 `assets/projects/*.webp` 與 `assets/projects/snapshots/*.webp` 兩份相同 deployment artifact。
- 移除已停用的 `avatar-fallback.svg` 與對應 build/checker wiring；GitHub 頭像的 privacy/performance 檢查仍保留。
- 移除 `has-four-selected` renderer flag 與五卡片特例 CSS，直接使用既有 `.project-card.featured` 版面規則。
- Light theme toggle 仍由 generic hardening 從舊 source 移除，但不再需要獨立 runtime patch stage。
- 保留 CSP、SEO、accessibility、privacy、Lighthouse、artifact integrity 與 release identity checks。

## v1.6.3 — 2026-09-02

CSP Security Hardening：盤點正式站瀏覽器實際載入的外部資源，並用最小權限 Content Security Policy 限制未列入來源的 script、style、image、network、frame 與 media 載入。

- 確認 Runtime 沒有外部 web font、CDN JavaScript / CSS、fetch / XHR / SSE / WebSocket、iframe、影音或 worker；相關 CSP directive 預設直接封鎖。
- Hero GitHub 頭像是目前唯一第三方 Runtime resource，`img-src` 僅額外允許 `https://github.com` 與可能的 avatar redirect `https://avatars.githubusercontent.com`。
- 新增 `apply_csp.py`，在所有發布 HTML 的 `<head>` 前段自動加入 CSP meta；本機 CSS / JS / 圖片 / manifest 維持 `'self'`。
- Inline JSON-LD 不使用 `'unsafe-inline'`，而是在每個最終頁面依實際內容產生 SHA-256 allowlist；同時封鎖 inline event handler、inline style attribute 與 `'unsafe-eval'`。
- `connect-src 'none'`、`frame-src 'none'`、`media-src 'none'`、`worker-src 'none'`、`object-src 'none'`，並啟用 `upgrade-insecure-requests`。
- 新增 `check_csp.py` build gate：未來若新增外部 script / stylesheet / image host、CSS import/url 或 JavaScript network API，CI 會要求先明確更新 CSP，而不是默默放寬 `default-src`。
- 新增 `docs/CSP.md`，記錄 Runtime 資源清單、Build-time-only 外站擷取、實際 CSP 規則與部署後 Console 手動驗證方式。
- GitHub Pages 目前使用 CSP meta，因此 `frame-ancestors` 無法由 meta 強制；若未來改由可設定 response headers 的 edge/proxy 提供服務，應在 HTTP CSP header 補上 `frame-ancestors 'none'`。

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
- Hero avatar 改為本地 `Yu` 品牌 SVG，不再在頁面載入 GitHub avatar，減少第三方 waterfall 與隱私依賴。
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
