const requestTableSql = `CREATE TABLE IF NOT EXISTS overtime_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_id TEXT NOT NULL,
  employee_name TEXT NOT NULL,
  department TEXT NOT NULL,
  overtime_date TEXT NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  duration REAL NOT NULL CHECK(duration > 0),
  reason TEXT NOT NULL,
  request_type TEXT NOT NULL DEFAULT 'REGULAR',
  status TEXT NOT NULL DEFAULT 'PENDING_MANAGER',
  submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

const approvalTableSql = `CREATE TABLE IF NOT EXISTS approval_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  actor_name TEXT NOT NULL,
  note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (request_id) REFERENCES overtime_requests(id)
)`;

const userTableSql = `CREATE TABLE IF NOT EXISTS app_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  auth_user_id TEXT NOT NULL UNIQUE,
  email TEXT,
  display_name TEXT NOT NULL,
  employee_id TEXT NOT NULL UNIQUE,
  department TEXT NOT NULL DEFAULT '未設定',
  role TEXT NOT NULL DEFAULT 'EMPLOYEE',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

const credentialTableSql = `CREATE TABLE IF NOT EXISTS staff_credentials (
  email TEXT PRIMARY KEY NOT NULL,
  password_hash TEXT NOT NULL,
  must_change_password INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)`;

const sessionTableSql = `CREATE TABLE IF NOT EXISTS staff_sessions (
  token_hash TEXT PRIMARY KEY NOT NULL,
  email TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (email) REFERENCES staff_credentials(email) ON DELETE CASCADE
)`;

const SESSION_COOKIE = "staff_session";
const SESSION_SECONDS = 60 * 60 * 12;
const HASH_ITERATIONS = 210000;

function envList(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

function emailPolicy(env) {
  return {
    emails: envList(env.ALLOWED_EMAILS),
    domains: envList(env.ALLOWED_EMAIL_DOMAINS).map((domain) => domain.replace(/^@/, "")),
  };
}

function isAllowedEmail(email, env) {
  const { emails, domains } = emailPolicy(env);
  if (emails.length) return emails.includes(email);
  return domains.length > 0 && domains.some((domain) => email.endsWith(`@${domain}`));
}

function bytesToBase64Url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

function base64UrlToBytes(value) {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/").padEnd(Math.ceil(value.length / 4) * 4, "=");
  return Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
}

async function derivePassword(password, salt, iterations) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations }, key, 256);
  return new Uint8Array(bits);
}

async function hashPassword(password) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const hash = await derivePassword(password, salt, HASH_ITERATIONS);
  return `pbkdf2-sha256:${HASH_ITERATIONS}:${bytesToBase64Url(salt)}:${bytesToBase64Url(hash)}`;
}

function constantTimeEqual(left, right) {
  if (left.length !== right.length) return false;
  let difference = 0;
  for (let index = 0; index < left.length; index += 1) difference |= left[index] ^ right[index];
  return difference === 0;
}

async function verifyPassword(password, storedHash) {
  const [algorithm, iterationsValue, saltValue, hashValue] = String(storedHash || "").split(":");
  const iterations = Number(iterationsValue);
  if (algorithm !== "pbkdf2-sha256" || !iterations || !saltValue || !hashValue) return false;
  const actual = await derivePassword(password, base64UrlToBytes(saltValue), iterations);
  return constantTimeEqual(actual, base64UrlToBytes(hashValue));
}

async function matchesInitialPassword(password, initialPassword) {
  const encoder = new TextEncoder();
  const [left, right] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(password)),
    crypto.subtle.digest("SHA-256", encoder.encode(initialPassword)),
  ]);
  return constantTimeEqual(new Uint8Array(left), new Uint8Array(right));
}

async function tokenHash(value) {
  return bytesToBase64Url(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value))));
}

function cookieValue(request, name) {
  for (const item of (request.headers.get("cookie") || "").split(";")) {
    const [key, ...value] = item.trim().split("=");
    if (key === name) return value.join("=");
  }
  return null;
}

function sessionCookie(token, requestUrl, maxAge = SESSION_SECONDS) {
  const secure = new URL(requestUrl).protocol === "https:" ? "; Secure" : "";
  return `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure}`;
}

async function ensureSchema(db) {
  await db.batch([
    db.prepare(requestTableSql),
    db.prepare(approvalTableSql),
    db.prepare(userTableSql),
    db.prepare(credentialTableSql),
    db.prepare(sessionTableSql),
    db.prepare("CREATE INDEX IF NOT EXISTS idx_overtime_employee_date ON overtime_requests(employee_id, overtime_date)"),
    db.prepare("CREATE INDEX IF NOT EXISTS idx_overtime_status_date ON overtime_requests(status, overtime_date)"),
    db.prepare("CREATE INDEX IF NOT EXISTS idx_staff_sessions_email ON staff_sessions(email)"),
    db.prepare("CREATE INDEX IF NOT EXISTS idx_staff_sessions_expires_at ON staff_sessions(expires_at)"),
  ]);
}

async function getAppUser(db, request) {
  const token = cookieValue(request, SESSION_COOKIE);
  if (!token) return null;
  const session = await db.prepare("SELECT email FROM staff_sessions WHERE token_hash = ? AND expires_at > ?")
    .bind(await tokenHash(token), Math.floor(Date.now() / 1000)).first();
  if (!session) return null;
  return db.prepare("SELECT * FROM app_users WHERE email = ? ORDER BY id LIMIT 1").bind(session.email).first();
}

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}

function mapRequest(row) {
  const statusMap = { PENDING_MANAGER: "待審核", APPROVED_MANAGER: "已核准", REJECTED_MANAGER: "已駁回" };
  return {
    id: row.id,
    employeeId: row.employee_id,
    name: row.employee_name,
    department: row.department,
    date: row.overtime_date.replaceAll("-", "/"),
    time: `${row.start_time}–${row.end_time}`,
    hours: row.duration,
    reason: row.reason,
    status: statusMap[row.status] || row.status,
    submittedAt: row.submitted_at,
  };
}

function minutesFromTime(value) {
  const match = /^(\d{2}):(\d{2})$/.exec(String(value || ""));
  if (!match) return NaN;
  return Number(match[1]) * 60 + Number(match[2]);
}

async function handleAuthApi(request, env, url) {
  if (!env.DB) return json({ error: "資料庫尚未連線" }, 503);
  await ensureSchema(env.DB);

  if (url.pathname === "/api/login" && request.method === "POST") {
    const body = await request.json();
    const email = String(body.email || "").trim().toLowerCase();
    const password = String(body.password || "");
    if (!/^\S+@\S+\.\S+$/.test(email) || password.length < 8) return json({ error: "請輸入有效的學校 Email 與密碼" }, 400);

    const policy = emailPolicy(env);
    if (!policy.emails.length && !policy.domains.length) return json({ error: "管理者尚未設定登入 allowlist" }, 503);
    if (!isAllowedEmail(email, env)) return json({ error: "此 Email 未被授權使用系統" }, 403);

    let credential = await env.DB.prepare("SELECT * FROM staff_credentials WHERE email = ?").bind(email).first();
    if (!credential) {
      if (!env.INITIAL_PASSWORD) return json({ error: "管理者尚未設定預設密碼" }, 503);
      if (!(await matchesInitialPassword(password, env.INITIAL_PASSWORD))) return json({ error: "首次登入請使用管理者提供的預設密碼" }, 401);
      await env.DB.prepare("INSERT INTO staff_credentials (email, password_hash, must_change_password) VALUES (?, ?, 1)")
        .bind(email, await hashPassword(password)).run();
      credential = await env.DB.prepare("SELECT * FROM staff_credentials WHERE email = ?").bind(email).first();

      const existingUser = await env.DB.prepare("SELECT id FROM app_users WHERE email = ? LIMIT 1").bind(email).first();
      if (!existingUser) {
        const role = envList(env.ADMIN_EMAILS).includes(email) ? "ADMIN" : "EMPLOYEE";
        const employeeId = `U${(await tokenHash(email)).slice(0, 10)}`;
        const displayName = email.split("@")[0];
        await env.DB.prepare("INSERT INTO app_users (auth_user_id, email, display_name, employee_id, role) VALUES (?, ?, ?, ?, ?)")
          .bind(`local:${email}`, email, displayName, employeeId, role).run();
      }
    } else if (!(await verifyPassword(password, credential.password_hash))) {
      return json({ error: "Email 或密碼不正確" }, 401);
    }

    const token = bytesToBase64Url(crypto.getRandomValues(new Uint8Array(32)));
    const now = Math.floor(Date.now() / 1000);
    await env.DB.batch([
      env.DB.prepare("DELETE FROM staff_sessions WHERE expires_at <= ?").bind(now),
      env.DB.prepare("INSERT INTO staff_sessions (token_hash, email, expires_at, created_at) VALUES (?, ?, ?, ?)")
        .bind(await tokenHash(token), email, now + SESSION_SECONDS, now),
    ]);
    return Response.json(
      { authenticated: true, mustChangePassword: Boolean(credential.must_change_password) },
      { headers: { "cache-control": "no-store", "set-cookie": sessionCookie(token, request.url) } },
    );
  }

  if (url.pathname === "/api/change-password" && request.method === "POST") {
    const token = cookieValue(request, SESSION_COOKIE);
    const session = token
      ? await env.DB.prepare("SELECT email FROM staff_sessions WHERE token_hash = ? AND expires_at > ?")
        .bind(await tokenHash(token), Math.floor(Date.now() / 1000)).first()
      : null;
    if (!session) return json({ error: "登入已逾時，請重新登入" }, 401);
    const body = await request.json();
    const password = String(body.password || "");
    if (password.length < 8) return json({ error: "新密碼至少需要 8 個字元" }, 400);
    if (password !== String(body.confirmation || "")) return json({ error: "兩次輸入的密碼不一致" }, 400);
    await env.DB.prepare("UPDATE staff_credentials SET password_hash = ?, must_change_password = 0, updated_at = CURRENT_TIMESTAMP WHERE email = ?")
      .bind(await hashPassword(password), session.email).run();
    return json({ updated: true });
  }

  if (url.pathname === "/api/logout" && request.method === "POST") {
    const token = cookieValue(request, SESSION_COOKIE);
    if (token) await env.DB.prepare("DELETE FROM staff_sessions WHERE token_hash = ?").bind(await tokenHash(token)).run();
    return Response.json(
      { signedOut: true },
      { headers: { "cache-control": "no-store", "set-cookie": sessionCookie("", request.url, 0) } },
    );
  }

  if (url.pathname === "/api/session" && request.method === "GET") {
    const user = await getAppUser(env.DB, request);
    if (!user) return json({ authenticated: false });
    const credential = await env.DB.prepare("SELECT must_change_password FROM staff_credentials WHERE email = ?").bind(user.email).first();
    return json({
      authenticated: true,
      mustChangePassword: Boolean(credential?.must_change_password),
      user: { name: user.display_name, email: user.email, employeeId: user.employee_id, department: user.department, role: user.role },
    });
  }

  return null;
}

async function handleApi(request, env, url) {
  if (["/api/login", "/api/change-password", "/api/logout", "/api/session"].includes(url.pathname)) {
    return handleAuthApi(request, env, url);
  }

  const statusMatch = url.pathname.match(/^\/api\/requests\/(\d+)\/status$/);
  const userRoleMatch = url.pathname.match(/^\/api\/users\/([^/]+)\/role$/);
  const supported = (url.pathname === "/api/requests" && ["GET", "POST"].includes(request.method)) ||
    (url.pathname === "/api/summary" && request.method === "GET") ||
    (statusMatch && request.method === "PATCH") ||
    (url.pathname === "/api/users" && request.method === "GET") ||
    (userRoleMatch && request.method === "PATCH");
  if (!supported) return json({ error: "找不到此 API" }, 404);
  if (!env.DB) return json({ error: "資料庫尚未連線" }, 503);

  await ensureSchema(env.DB);
  const appUser = await getAppUser(env.DB, request);
  if (!appUser) return json({ error: "請先登入" }, 401);

  if (url.pathname === "/api/requests" && request.method === "GET") {
    const elevated = ["ADMIN", "MANAGER", "SECRETARY"].includes(appUser.role);
    const result = elevated
      ? await env.DB.prepare("SELECT * FROM overtime_requests ORDER BY submitted_at DESC, id DESC").all()
      : await env.DB.prepare("SELECT * FROM overtime_requests WHERE employee_id = ? ORDER BY submitted_at DESC, id DESC")
        .bind(appUser.employee_id).all();
    return json({ requests: result.results.map(mapRequest) });
  }

  if (url.pathname === "/api/requests" && request.method === "POST") {
    const body = await request.json();
    const { date, startTime, endTime, duration, reason, type = "REGULAR" } = body;
    if (!date || !startTime || !endTime || !Number(duration) || String(reason || "").trim().length < 10) {
      return json({ error: "申請資料不完整，事由至少需要 10 個字" }, 400);
    }
    const startMinutes = minutesFromTime(startTime);
    const endMinutes = minutesFromTime(endTime);
    const calculatedDuration = (endMinutes - startMinutes) / 60;
    if (!Number.isFinite(startMinutes) || !Number.isFinite(endMinutes) || startMinutes < 16 * 60 + 30) {
      return json({ error: "加班開始時間最早為 16:30" }, 400);
    }
    if (startMinutes % 30 !== 0 || endMinutes % 30 !== 0 || calculatedDuration < 0.5 || !Number.isInteger(calculatedDuration * 2)) {
      return json({ error: "加班時間須以 30 分鐘為單位，且單次至少 30 分鐘" }, 400);
    }
    if (Math.abs(calculatedDuration - Number(duration)) > 0.001) {
      return json({ error: "申請時數與起訖時間不一致" }, 400);
    }
    const overlap = await env.DB.prepare(
      "SELECT id FROM overtime_requests WHERE employee_id = ? AND overtime_date = ? AND status != 'REJECTED_MANAGER' AND start_time < ? AND end_time > ? LIMIT 1",
    ).bind(appUser.employee_id, date, endTime, startTime).first();
    if (overlap) return json({ error: "此時段已有申請，請勿重複送出" }, 409);

    const result = await env.DB.prepare(
      "INSERT INTO overtime_requests (employee_id, employee_name, department, overtime_date, start_time, end_time, duration, reason, request_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    ).bind(
      appUser.employee_id,
      appUser.display_name,
      appUser.department,
      date,
      startTime,
      endTime,
      Number(duration),
      String(reason).trim(),
      type,
    ).run();
    const created = await env.DB.prepare("SELECT * FROM overtime_requests WHERE id = ?").bind(result.meta.last_row_id).first();
    return json({ request: mapRequest(created) }, 201);
  }

  if (statusMatch && request.method === "PATCH") {
    if (!["ADMIN", "MANAGER"].includes(appUser.role)) return json({ error: "只有主管可以審核申請" }, 403);
    const body = await request.json();
    const statusMap = { "已核准": "APPROVED_MANAGER", "已駁回": "REJECTED_MANAGER" };
    const nextStatus = statusMap[body.status];
    if (!nextStatus) return json({ error: "不支援的審核狀態" }, 400);
    const id = Number(statusMatch[1]);
    const existing = await env.DB.prepare("SELECT id FROM overtime_requests WHERE id = ?").bind(id).first();
    if (!existing) return json({ error: "找不到申請資料" }, 404);
    await env.DB.batch([
      env.DB.prepare("UPDATE overtime_requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(nextStatus, id),
      env.DB.prepare("INSERT INTO approval_logs (request_id, action, actor_name, note) VALUES (?, ?, ?, ?)")
        .bind(id, nextStatus, appUser.display_name, body.note || null),
    ]);
    const updated = await env.DB.prepare("SELECT * FROM overtime_requests WHERE id = ?").bind(id).first();
    return json({ request: mapRequest(updated) });
  }

  if (url.pathname === "/api/summary" && request.method === "GET") {
    const employeeId = ["ADMIN", "MANAGER", "SECRETARY"].includes(appUser.role)
      ? (url.searchParams.get("employee_id") || appUser.employee_id)
      : appUser.employee_id;
    const startDate = url.searchParams.get("start_date");
    const endDate = url.searchParams.get("end_date");
    if (!startDate || !endDate) return json({ error: "請提供統計週期 start_date 與 end_date" }, 400);
    const result = await env.DB.prepare(
      "SELECT status, COALESCE(SUM(duration), 0) AS hours FROM overtime_requests WHERE employee_id = ? AND overtime_date BETWEEN ? AND ? GROUP BY status",
    ).bind(employeeId, startDate, endDate).all();
    return json({ summary: result.results });
  }

  if (url.pathname === "/api/users" && request.method === "GET") {
    if (appUser.role !== "ADMIN") return json({ error: "只有管理者可以查看使用者" }, 403);
    const result = await env.DB.prepare(
      "SELECT display_name, email, employee_id, department, role, created_at FROM app_users ORDER BY created_at",
    ).all();
    return json({ users: result.results });
  }

  if (userRoleMatch && request.method === "PATCH") {
    if (appUser.role !== "ADMIN") return json({ error: "只有管理者可以調整角色" }, 403);
    const body = await request.json();
    if (!["EMPLOYEE", "MANAGER", "SECRETARY", "ADMIN"].includes(body.role)) return json({ error: "角色不正確" }, 400);
    await env.DB.prepare("UPDATE app_users SET role = ? WHERE employee_id = ?")
      .bind(body.role, decodeURIComponent(userRoleMatch[1])).run();
    return json({ updated: true });
  }

  return json({ error: "找不到此 API" }, 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      try {
        return await handleApi(request, env, url);
      } catch {
        return json({ error: "系統暫時無法處理，請稍後再試" }, 500);
      }
    }

    if (!env.ASSETS) return new Response("Static asset binding is not configured", { status: 503 });
    const response = await env.ASSETS.fetch(request);
    const acceptsHtml = request.headers.get("accept")?.includes("text/html");
    if (response.status !== 404 || !acceptsHtml || !["GET", "HEAD"].includes(request.method)) return response;

    const indexUrl = new URL(request.url);
    indexUrl.pathname = "/index.html";
    indexUrl.search = "";
    return env.ASSETS.fetch(new Request(indexUrl, request));
  },
};
