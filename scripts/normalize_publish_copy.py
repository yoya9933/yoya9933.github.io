from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "_site"

REPLACEMENTS = {
    "浮標資料分析平台實際執行畫面": "浮標資料分析平台功能預覽",
    "楚河棋局實際產品畫面": "楚河棋局產品預覽",
    "NCKU Return OS 實際介面截圖": "NCKU Return OS 功能預覽",
    "<h3>真正啟動原始 Streamlit App 的畫面</h3>": "<h3>可重現的產品流程預覽</h3>",
    "浮標資料分析平台原始 Streamlit App 實際執行畫面": "浮標資料分析平台功能與流程預覽",
    "原始 app.py 由 GitHub Actions 啟動，搭配最小測試資料後以 Chromium 擷取。": "此圖由作品集內的固定向量素材產生，用來呈現資料 QA、LSTM、驗證與風險規則的產品流程；不冒充真實觀測或模型 benchmark。",
    "Buoy analytics Streamlit runtime": "Buoy analytics feature preview",
    "Chuhe Xiangqi product": "Chuhe Xiangqi product preview",
    "NCKU Return OS": "NCKU Return OS",
    "Actual Streamlit runtime": "Buoy platform feature preview",
    "The original app.py was started in GitHub Actions and captured with Chromium using a minimal fixture dataset.": "This deterministic portfolio preview summarizes the product flow across data QA, LSTM, validation and risk rules; it is not presented as a real-data benchmark screenshot.",
    "Chuhe Xiangqi product interface": "Chuhe Xiangqi product preview",
}

for html in SITE.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    updated = text
    for old, new in REPLACEMENTS.items():
        updated = updated.replace(old, new)
    if updated != text:
        html.write_text(updated, encoding="utf-8")
