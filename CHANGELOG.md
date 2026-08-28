# Changelog

網站版本遵循 Semantic Versioning（SemVer）：`MAJOR.MINOR.PATCH`。

## v1.1.1 — 2026-08-29

Stability Patch：降低部署與品質檢查的偶發失敗，並移除外部網站對 production build 的依賴。

- GitHub Actions 升級到目前支援 Node 24 的主要版本，移除既有 Node 20 deprecation 技術債。
- Lighthouse 改為每頁執行 3 次並使用 median 判定，降低單次量測波動造成的 false negative。
- Site Quality 無論成功或失敗都保留 Lighthouse report artifact 7 天，方便診斷。
- 股東紀念品 CMS 的 production build 改用 repository 內已審核的 frozen snapshot，不再於每次部署即時存取 `sharegift.tw`。
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
