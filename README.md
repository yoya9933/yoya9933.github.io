# yoya9933.github.io

這個 repository 是你的個人網站，目前為靜態 `index.html` 網站。

## 目前狀態
- `index.html`：主站內容（靜態）。
- `.github/workflows/deploy.yml` / `.github/workflows/gh-pages.yml`：GitHub Actions 工作流，部署 repo 根目錄的靜態頁面（`index.html`）。

## 在本機測試（靜態）
最簡單：直接打開 `index.html` 在瀏覽器。

或使用臨時 HTTP 伺服器：

```bash
# Python 3
python -m http.server 8000
# 然後打開 http://localhost:8000
```

## CI / 部署
- 當你 `git push` 到 `main`（或 `master`）時，GitHub Actions 會直接將 repo 根目錄上傳部署到 GitHub Pages。

## 注意事項
- 靜態網站只需修改 `index.html` 後推送即可。

---
如需我把 workflow 調整成只部署 `index.html`（無需 trunk），或保留 trunk 編譯流程但優化快取與 artifact，告訴我你的偏好，我會替你更新。