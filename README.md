# Yu Portfolio

[![Version](https://img.shields.io/github/v/release/yoya9933/yoya9933.github.io?label=version)](https://github.com/yoya9933/yoya9933.github.io/releases/latest)
[![Release and Deploy](https://github.com/yoya9933/yoya9933.github.io/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/yoya9933/yoya9933.github.io/actions/workflows/deploy.yml)
[![Site Quality](https://github.com/yoya9933/yoya9933.github.io/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/yoya9933/yoya9933.github.io/actions/workflows/quality.yml)
[![Website](https://img.shields.io/badge/website-yoya9933.page-5eead4)](https://yoya9933.page/)

個人作品集網站，正式網址為 `https://yoya9933.page/`。網站採純靜態 HTML / CSS / JavaScript，並以 GitHub Actions 建立經過 allowlist 的 `_site` 部署產物。

**Current website version:** [`VERSION`](./VERSION)

- 版本單一來源：[`VERSION`](./VERSION)
- 版本紀錄：[`CHANGELOG.md`](./CHANGELOG.md)／[網站版 Changelog](https://yoya9933.page/changelog/)
- GitHub 正式版本：[`Releases`](https://github.com/yoya9933/yoya9933.github.io/releases)
- 正式站機器可讀資訊：`https://yoya9933.page/version.json`
- 網頁 Footer 會顯示版本號與實際部署的 Git commit short SHA。

## 代表內容

Selected Work：

- 浮標資料分析與航道風險評估平台
- 楚河棋局｜線上中國象棋
- 活動報到與現場營運系統
- 股東紀念品服務與 CMS 平台
- Neon Arena｜即時多人德州撲克
- 加班管理與行政彙整系統
- Reliable AI Media Automation Pipeline

另提供中英文首頁、Case Study、Contact 與建置時產生的雙語 CV PDF。

活動報到的正式系統與資料庫維持 private。此 repository 只發布以虛構資料製作、無持久化寫入權限的公開 Demo。

## 版本管理

網站版本採 Semantic Versioning：

```text
MAJOR.MINOR.PATCH
```

發布新版本時修改根目錄 `VERSION`，並同步在 `CHANGELOG.md` 新增相同版本的說明。Pull request 會先驗證兩者一致；合併到 `main` 後，Release workflow 會先完成建置、品質檢查、Pages 部署與正式站版本驗證，再建立尚未存在的 Git tag / GitHub Release。

Build 會自動：

- 將版本寫入所有 HTML 的 `application-version` metadata
- 在中英文首頁 Footer 顯示 `v版本號 · commit`
- 由 `CHANGELOG.md` 產生 `/changelog/`
- 由 project manifest 產生 `sitemap.xml`
- 產生 `/version.json`，包含版本、commit、build time 與 environment
- 將 commit 連回該次 GitHub 原始碼

## 結構

```text
.
├── VERSION
├── CHANGELOG.md
├── data/projects.json
├── index.html
├── en/
├── projects/
├── demos/event-checkin/
├── contact/
├── assets/
├── scripts/
├── .github/workflows/
├── robots.txt
└── CNAME
```

## 本機建置

建置腳本需要 Chromium、`librsvg2-bin`、WebP、Ghostscript、Noto CJK 字型、`qrencode` 與 Pillow（`python3-pil`）：

```bash
bash scripts/build_site.sh
```

輸出位置：

```text
_site/
```

部署腳本只會複製明確允許的公開檔案，不會把 repository metadata、CV 原始 HTML、淘汰的專案頁面或 private event data 放入 Pages artifact。

## 驗證

```bash
python3 scripts/check_site.py
```

Pull request 會執行 Site Quality workflow，包括：

- VERSION / CHANGELOG release metadata validation
- allowlisted production build
- internal link、SEO、robots 與 stale-content 檢查
- HTML validation
- Lighthouse CI

## 部署

Push / merge 到 `main` 後，`.github/workflows/deploy.yml` 會依序執行版本驗證、`_site` 建置與品質檢查、部署及正式站驗證，成功後才建立必要的 Git tag / GitHub Release。
