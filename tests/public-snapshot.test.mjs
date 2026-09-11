import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const app = await readFile(new URL("../src/App.jsx", import.meta.url), "utf8");
const worker = await readFile(new URL("../worker/index.js", import.meta.url), "utf8");

const retiredDemoTokens = ["少公主", "王主任", "張00", "林怡君", "張雅婷"];

test("public snapshot contains no retired production-like demo identities", () => {
  for (const token of retiredDemoTokens) {
    assert.equal(app.includes(token), false, `${token} leaked into App.jsx`);
    assert.equal(worker.includes(token), false, `${token} leaked into worker/index.js`);
  }
});

test("write failures cannot be converted into local success", () => {
  assert.match(app, /資料未儲存/);
  assert.match(app, /狀態未變更/);
  assert.doesNotMatch(app, /正式資料庫連線後會永久保存/);
});

test("identity provisioning fails closed", () => {
  assert.match(worker, /ALLOWED_EMAILS/);
  assert.match(worker, /ALLOWED_EMAIL_DOMAINS/);
  assert.match(worker, /ADMIN_EMAILS/);
  assert.match(worker, /管理者尚未設定登入 allowlist/);
  assert.doesNotMatch(worker, /COUNT\(\*\).*app_users/);
});

test("server errors do not expose internal exception messages", () => {
  assert.doesNotMatch(worker, /detail\s*:\s*error\.message/);
  assert.match(worker, /系統暫時無法處理，請稍後再試/);
});
