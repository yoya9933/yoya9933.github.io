# Yoya Portfolio

個人作品集網站，正式網址為 `https://yoya9933.page/`。網站採純靜態 HTML / CSS / JavaScript，並以 GitHub Actions 建立經過 allowlist 的 `_site` 部署產物。

## 代表內容

- 浮標資料分析與航道風險評估平台
- 楚河棋局｜線上中國象棋
- 活動報到與現場營運系統
- Reliable AI Media Automation Pipeline
- 中英文首頁、Case Study、Contact 與建置時產生的雙語 CV PDF

活動報到的正式系統與資料庫維持 private。此 repository 只發布以虛構資料製作、無持久化寫入權限的公開 Demo。

## 結構

```text
.
├── index.html
├── en/
├── projects/
├── demos/event-checkin/
├── contact/
├── assets/
├── scripts/
├── .github/workflows/
├── sitemap.xml
├── robots.txt
└── CNAME
```

## 本機建置

建置腳本需要 Chromium、`librsvg2-bin`、WebP、Ghostscript、Noto CJK 字型與 `qrencode`：

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
python3 scripts/check_p2.py
python3 scripts/check_p3.py
```

Pull request 會執行 Site Quality workflow，包括：

- allowlisted production build
- internal link 與 stale-content 檢查
- HTML validation
- Lighthouse CI

## 部署

Push / merge 到 `main` 後，`.github/workflows/deploy.yml` 會建置 `_site`，驗證通過後部署到 GitHub Pages。
