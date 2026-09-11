# Overtime Operations System｜加班管理系統

以校內行政流程為背景的加班資料整理、主管審核與行政彙整工具。

> **實際使用**：本系統目前由 **國立成功大學教務處教學發展中心** 內部使用，協助加班資料整理、主管審核與行政彙整。正式加班申請、時數認定與核銷仍以學校正式系統與行政程序為準。
>
> **Real-world use**: This system is currently used internally by the **Center for Teaching and Learning Development, Office of Academic Affairs, National Cheng Kung University (NCKU)** to assist with overtime data collection, manager review, and administrative consolidation. Official overtime recognition and reimbursement remain subject to NCKU's formal systems and procedures.

官方單位資訊：<https://ctld-acad.ncku.edu.tw/index.php>

## 我負責的內容

- 設計並實作加班申請、審核、角色權限與行政彙整流程。
- 建立 Cloudflare Worker API 與 D1 資料模型。
- 實作首次登入改密碼、PBKDF2-SHA256 密碼雜湊、雜湊 session token 與 HttpOnly cookie。
- 在後端驗證 30 分鐘時段、最早加班時間、申請時數與重疊時段，避免只依賴前端檢查。
- 將同仁、主管、秘書與管理者權限分開，敏感查詢與角色異動在 API 再做授權檢查。

## 核心功能

- 學校 Email 登入與首次登入強制改密碼。
- 同仁提出加班申請並查看自己的紀錄。
- 主管核准／駁回並保留審核紀錄。
- 秘書查看行政彙整與資料檢核畫面。
- 管理者調整使用者角色。
- D1 持久化加班申請、帳號、session 與 approval log。

## 技術架構

| Layer | Technology |
| --- | --- |
| Frontend | React 19 + Vite |
| UI | Phosphor Icons + Recharts |
| API / Runtime | Cloudflare Workers |
| Database | Cloudflare D1 / SQLite |
| Authentication | PBKDF2-SHA256 + HttpOnly session cookie |

## 公開版與 Production 的界線

這個 branch 是從實際系統整理出的 **sanitized portfolio snapshot**，不是 production repository。為保護實際使用者與部署環境：

- 不包含任何教發中心同仁姓名、Email、加班事由或正式資料庫內容。
- 不包含 production D1 ID、Cloudflare account / project ID、密碼、token 或其他 secret。
- 畫面中的示範資料全部使用明確的測試名稱。
- 公開版移除「API 失敗時假裝已儲存」的 fallback；寫入失敗會明確顯示資料未儲存。
- 公開版登入預設採 fail-closed allowlist 設計，部署者需設定允許的 Email 或 Email domain；管理者帳號也需由環境設定明確指定。

因此，這個 repository 可以用來檢視我的程式設計與系統架構，但無法從公開程式碼取得或進入教發中心的 production 環境。

## 本機查看 UI

```bash
npm install
npm run dev:demo
```

`dev:demo` 使用純前端 synthetic data，不連 production API 或 D1。

## Production-like 設定

Worker 版本使用下列環境變數；**請只放在部署平台 secret / environment，不要 commit 真實值**：

```text
INITIAL_PASSWORD=replace-me
ALLOWED_EMAILS=user1@example.edu.tw,user2@example.edu.tw
ALLOWED_EMAIL_DOMAINS=example.edu.tw
ADMIN_EMAILS=admin@example.edu.tw
```

登入 allowlist 的判斷順序：若有 `ALLOWED_EMAILS` 則使用精確 Email 名單；否則使用 `ALLOWED_EMAIL_DOMAINS`。兩者皆未設定時拒絕登入，避免部署失誤造成公開註冊。

## Repository layout

```text
.
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
├── worker/
│   └── index.js
├── db/
│   └── schema.ts
├── migrations/
│   └── 0000_overtime_core.sql
├── index.html
└── package.json
```

## Scope note

這是我開發並投入實際行政使用的工具；它不是「國立成功大學官方加班系統」，也不代表校方對此公開 repository 的背書或認證。公開 repository 只用來展示工程實作與作品集證據。
