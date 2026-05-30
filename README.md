# yoya9933.github.io

這個 repository 是你的個人網站，目前支援兩種工作流程：

1. 靜態 `index.html`（目前使用）
2. 原始 Yew (Rust) 應用 -> 使用 `trunk` 編譯成 WebAssembly 的流程

## 目前狀態
- `index.html`：主站內容（靜態）。
- `src/main.rs`：Yew 應用來源（可用 `trunk` 編譯輸出到 `dist/`）。
- `.github/workflows/deploy.yml`：GitHub Actions 工作流，會在 CI runner 上安裝 Rust、安裝 `trunk`，執行 `trunk build --release --public-url /`，並將 `./dist` 上傳部署到 GitHub Pages。

## 在本機測試（靜態）
最簡單：直接打開 `index.html` 在瀏覽器。

或使用臨時 HTTP 伺服器：

```bash
# Python 3
python -m http.server 8000
# 然後打開 http://localhost:8000
```

## 在本機測試（Yew + Trunk）
先安裝 Rust 與 trunk：

```bash
# 安裝 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-unknown-unknown

# 安裝 trunk (macOS / Linux 範例)
curl -L https://github.com/thedodd/trunk/releases/latest/download/trunk-x86_64-unknown-linux-gnu.tar.gz | tar -xzf -
sudo mv trunk /usr/local/bin/
```

本地即時開發伺服器：

```bash
trunk serve --open
```

或產生靜態輸出到 `dist/`：

```bash
trunk build --release --public-url /
```

## CI / 部署
- 當你 `git push` 到 `main`（或 `master`）時，GitHub Actions 會在 runner 上安裝 Rust 與 Trunk，執行 `trunk build`，然後把 `./dist` 的內容上傳並部署到 GitHub Pages（Actions 部署）。
- 若你只想維持純靜態 `index.html`，也可以直接編輯 `index.html` 並 push，CI 會把它打包部署（目前 workflow 會部署 `./dist`，若沒有 dist，請改為部署 repo 根目錄，或手動上傳）。

## 注意事項
- 若要回復成純 CI 編譯 Yew，請確保 `src/main.rs` 與 `Cargo.toml` 保留正確內容；CI 會負責編譯並上傳 `dist/`。
- 預覽或開發時使用 `trunk serve`，測試完成後再 `git push` 推到 GitHub 以觸發自動化部署。

---
如需我把 workflow 調整成只部署 `index.html`（無需 trunk），或保留 trunk 編譯流程但優化快取與 artifact，告訴我你的偏好，我會替你更新。