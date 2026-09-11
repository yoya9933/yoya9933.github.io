import { useEffect, useMemo, useState } from "react";
import {
  CalendarBlank, Check, CheckCircle, Clock, FileText, House, ListChecks,
  SignOut, Table, TrayArrowDown, UserCircle, UsersThree, WarningCircle,
  X,
} from "@phosphor-icons/react";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

const demoRequests = [
  { id: 1, employeeId: "D001", name: "測試同仁 A", department: "示範單位", date: "2026/08/17", time: "18:30–20:30", hours: 2, reason: "活動資料整理與行政文件彙整", status: "已核准" },
  { id: 2, employeeId: "D001", name: "測試同仁 A", department: "示範單位", date: "2026/08/14", time: "19:00–21:00", hours: 2, reason: "專案資料檢核與報表內容整理", status: "已核准" },
  { id: 3, employeeId: "D001", name: "測試同仁 A", department: "示範單位", date: "2026/08/12", time: "18:00–20:00", hours: 2, reason: "研習活動資料與簡報內容準備", status: "待審核" },
  { id: 4, employeeId: "D002", name: "測試同仁 B", department: "示範單位", date: "2026/08/18", time: "17:30–19:00", hours: 1.5, reason: "行政資料彙整與系統內容核對", status: "待審核" },
];

const demoImportedRows = [
  { name: "測試同仁 A", type: "加班", date: "8/11（二）", time: "16:30–17:00", stated: "30 分", calculated: "0.5 小時", reason: "行政資料整理與核對", issue: "" },
  { name: "測試同仁 B", type: "加班", date: "8/12（三）", time: "17:00–17:30", stated: "30 分", calculated: "0.5 小時", reason: "活動資料彙整與檢查", issue: "" },
  { name: "測試同仁 C", type: "加班", date: "8/05（三）", time: "17:30–19:00", stated: "1 小時", calculated: "1.5 小時", reason: "報表資料處理與確認", issue: "時數不一致" },
];

const nav = [
  ["申請", "加班申請", FileText],
  ["紀錄", "我的紀錄", ListChecks],
  ["審核", "審核作業", UsersThree],
  ["報表", "報表中心", Table],
  ["權限", "人員權限", UsersThree],
];

const roleLabels = { ADMIN: "系統管理者", MANAGER: "主管", SECRETARY: "秘書", EMPLOYEE: "同仁" };
const timeOptions = Array.from({ length: 15 }, (_, index) => {
  const totalMinutes = 16 * 60 + 30 + index * 30;
  return `${String(Math.floor(totalMinutes / 60)).padStart(2, "0")}:${String(totalMinutes % 60).padStart(2, "0")}`;
});

function localDateParts(date = new Date()) {
  const weekday = ["日", "一", "二", "三", "四", "五", "六"][date.getDay()];
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return { iso: `${year}-${month}-${day}`, slash: `${year}/${month}/${day}`, label: `${year}/${month}/${day}（星期${weekday}）`, weekday };
}

function getWeekRange(date = new Date()) {
  const start = new Date(date);
  start.setDate(start.getDate() - ((start.getDay() + 6) % 7));
  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  return { start: localDateParts(start), end: localDateParts(end) };
}

function Status({ children }) {
  const cls = children === "已核准" ? "approved" : children === "已駁回" ? "rejected" : "pending";
  return <span className={`status ${cls}`}>{children}</span>;
}

function LoginPanel() {
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function login(event) {
    event.preventDefault();
    setMessage("");
    setSubmitting(true);
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "登入失敗");
      window.location.reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "登入失敗");
      setSubmitting(false);
    }
  }

  return <div className="login-screen"><div className="login-panel"><Clock size={46} /><h1>加班管理系統</h1><p>輸入已授權的學校 Email 與密碼。第一次使用請輸入管理者提供的預設密碼。</p><form className="login-form" onSubmit={login}><label>學校 Email<input name="email" type="email" autoComplete="username" placeholder="name@example.edu.tw" required /></label><label>密碼<input name="password" type="password" autoComplete="current-password" minLength={8} required /></label>{message && <p className="login-error" role="alert">{message}</p>}<button className="login-button" type="submit" disabled={submitting}>{submitting ? "登入中…" : "登入"}</button></form><small>正式加班申請、時數認定與核銷仍以學校正式系統及行政程序為準。</small></div></div>;
}

function PasswordPanel({ email }) {
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function changePassword(event) {
    event.preventDefault();
    setMessage("");
    setSubmitting(true);
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch("/api/change-password", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ password: form.get("password"), confirmation: form.get("confirmation") }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "密碼更新失敗");
      window.location.reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "密碼更新失敗");
      setSubmitting(false);
    }
  }

  return <div className="login-screen"><div className="login-panel"><Clock size={46} /><h1>設定個人密碼</h1><p>{email} 已完成首次登入。</p><form className="login-form" onSubmit={changePassword}><label>新密碼<input name="password" type="password" autoComplete="new-password" minLength={8} required /></label><label>再輸入一次<input name="confirmation" type="password" autoComplete="new-password" minLength={8} required /></label>{message && <p className="login-error" role="alert">{message}</p>}<button className="login-button" type="submit" disabled={submitting}>{submitting ? "儲存中…" : "設定密碼"}</button></form></div></div>;
}

export function App() {
  const [view, setView] = useState("申請");
  const [requests, setRequests] = useState(DEMO_MODE ? demoRequests : []);
  const [start, setStart] = useState("18:00");
  const [end, setEnd] = useState("20:00");
  const [reason, setReason] = useState("專案活動資料整理與行政文件內容核對。");
  const [notice, setNotice] = useState("");
  const [imported, setImported] = useState(false);
  const [connected, setConnected] = useState(false);
  const [session, setSession] = useState({ loading: !DEMO_MODE, authenticated: DEMO_MODE, mustChangePassword: false, user: DEMO_MODE ? { name: "測試管理者", email: "demo@example.edu.tw", employeeId: "DEMO", department: "示範單位", role: "ADMIN" } : null });

  useEffect(() => {
    if (DEMO_MODE) return undefined;
    let active = true;
    fetch("/api/session", { headers: { accept: "application/json" } })
      .then(async (response) => {
        if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) throw new Error("API unavailable");
        return response.json();
      })
      .then(async (data) => {
        if (!active) return;
        setSession({ loading: false, authenticated: Boolean(data.authenticated), mustChangePassword: Boolean(data.mustChangePassword), user: data.user || null });
        if (!data.authenticated) return;
        const response = await fetch("/api/requests", { headers: { accept: "application/json" } });
        const requestData = await response.json();
        if (!response.ok) throw new Error(requestData.error || "資料載入失敗");
        if (active) {
          setRequests(Array.isArray(requestData.requests) ? requestData.requests : []);
          setConnected(true);
        }
      })
      .catch(() => {
        if (active) {
          setConnected(false);
          setSession((current) => ({ ...current, loading: false }));
        }
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (session.user?.role === "SECRETARY") setView("報表");
    if (session.user?.role === "MANAGER") setView("審核");
  }, [session.user?.role]);

  const requestHours = Math.max(0, Number(end.slice(0, 2)) + Number(end.slice(3)) / 60 - Number(start.slice(0, 2)) - Number(start.slice(3)) / 60);
  const today = localDateParts();
  const week = getWeekRange();
  const weekLabel = `${week.start.slash}～${week.end.slash}`;
  const currentEmployeeRequests = DEMO_MODE
    ? requests.filter((request) => request.employeeId === "D001")
    : requests.filter((request) => request.employeeId === session.user?.employeeId);
  const weeklyRequests = currentEmployeeRequests.filter((request) => {
    const requestDate = request.date.replaceAll("/", "-");
    return requestDate >= week.start.iso && requestDate <= week.end.iso;
  });
  const approved = weeklyRequests.filter((request) => request.status === "已核准").reduce((sum, request) => sum + request.hours, 0);
  const pending = weeklyRequests.filter((request) => request.status === "待審核").reduce((sum, request) => sum + request.hours, 0);
  const projected = approved + pending + requestHours;
  const chart = useMemo(() => [
    { name: "已核准", value: approved, color: "#1767d7" },
    { name: "待審核", value: pending, color: "#f18a2a" },
    { name: "本次申請", value: requestHours, color: "#76b947" },
    { name: "剩餘", value: Math.max(20 - projected, 0), color: "#e9edf2" },
  ], [approved, pending, requestHours, projected]);

  async function submit(event) {
    event.preventDefault();
    if (reason.trim().length < 10 || requestHours <= 0) {
      setNotice("請確認加班時段，並填寫至少 10 個字的具體事由。");
      return;
    }
    if (DEMO_MODE) {
      setRequests((list) => [{ id: Date.now(), employeeId: "D001", name: "測試同仁 A", department: "示範單位", date: today.slash, time: `${start}–${end}`, hours: requestHours, reason, status: "待審核" }, ...list]);
      setNotice("展示資料已加入目前畫面；不會寫入任何資料庫。");
      return;
    }
    try {
      const response = await fetch("/api/requests", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ date: today.iso, startTime: start, endTime: end, duration: requestHours, reason }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "送出失敗");
      setRequests((list) => [data.request, ...list]);
      setConnected(true);
      setNotice("申請已儲存，主管與秘書可立即查看。");
    } catch (error) {
      setNotice(`${error instanceof Error ? error.message : "送出失敗"}；資料未儲存。`);
    }
  }

  async function decide(id, status) {
    if (DEMO_MODE) {
      setRequests((list) => list.map((request) => request.id === id ? { ...request, status } : request));
      setNotice("展示狀態已更新；重新整理後會還原。");
      return;
    }
    try {
      const response = await fetch(`/api/requests/${id}/status`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ status }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "審核失敗");
      setRequests((list) => list.map((request) => request.id === id ? data.request : request));
      setNotice("審核結果已儲存。");
    } catch (error) {
      setNotice(`${error instanceof Error ? error.message : "審核失敗"}；狀態未變更。`);
    }
  }

  if (session.loading) return <div className="login-screen"><div className="login-panel"><Clock size={46} /><h1>加班管理系統</h1><p>正在確認登入狀態…</p></div></div>;
  if (!session.authenticated) return <LoginPanel />;
  if (session.mustChangePassword) return <PasswordPanel email={session.user?.email} />;

  const role = session.user?.role || "EMPLOYEE";
  const visibleNav = nav.filter(([key]) => role === "ADMIN" || (role === "MANAGER" ? ["紀錄", "審核"].includes(key) : role === "SECRETARY" ? ["紀錄", "報表"].includes(key) : ["申請", "紀錄"].includes(key)));
  const approvedHours = requests.filter((request) => request.status === "已核准").reduce((sum, request) => sum + request.hours, 0);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Clock size={31} /><span>加班管理系統</span></div>
        <button className="home-link" onClick={() => setView(role === "SECRETARY" ? "報表" : role === "MANAGER" ? "審核" : "申請")}><House size={26} />首頁</button>
        <nav>{visibleNav.map(([key, label, Icon]) => <button key={key} className={view === key ? "active" : ""} onClick={() => { setView(key); setNotice(""); }}><Icon size={26} /><span>{label}</span></button>)}</nav>
        <div className="profile"><UserCircle size={43} weight="fill" /><div><b>{session.user?.name}</b><span>{roleLabels[role]} · {session.user?.department}</span></div>{!DEMO_MODE && <button className="logout-button" aria-label="登出" type="button" onClick={async () => { await fetch("/api/logout", { method: "POST" }); window.location.reload(); }}><SignOut size={21} /></button>}</div>
      </aside>

      <main className="workspace">
        <header className="topbar"><div><CalendarBlank size={23} /><span>{today.iso}　星期{today.weekday}</span><span className={`connection ${connected ? "online" : "demo"}`}>{DEMO_MODE ? "展示模式" : connected ? "資料庫已連線" : "資料庫連線異常"}</span></div><p><Clock size={22} />常態申請需於今日 16:00 前送出</p></header>
        {notice && <div className={`notice ${notice.includes("已") || notice.includes("展示") ? "success" : "error"}`}>{notice.includes("已") || notice.includes("展示") ? <CheckCircle size={22} /> : <WarningCircle size={22} />}{notice}</div>}

        {view === "申請" && <>
          <section className="heading"><h1>加班申請 <small>（當日申請）</small></h1><p>三步驟完成申請，送出後由主管審核。</p></section>
          <form className="application" onSubmit={submit}>
            <div className="steps"><span><b>1</b>選擇日期與時段</span><i /><span><b>2</b>填寫事由</span><i /><span><b>3</b>確認工時影響</span></div>
            <div className="columns">
              <section className="form-section"><label><CalendarBlank size={23} />加班日期</label><input aria-label="加班日期" value={today.label} readOnly /><label><Clock size={23} />加班時段</label><div className="time-row"><select aria-label="開始時間" value={start} onChange={(event) => setStart(event.target.value)}>{timeOptions.slice(0, -1).map((time) => <option key={time}>{time}</option>)}</select><span>～</span><select aria-label="結束時間" value={end} onChange={(event) => setEnd(event.target.value)}>{timeOptions.slice(1).map((time) => <option key={time}>{time}</option>)}</select></div><p className="time-hint">最早 16:30 開始，每 30 分鐘為一個區間，單次至少 30 分鐘。</p><div className="hours-box"><Clock size={27} /><div className="hours-copy"><span className="hours-label">本次申請時數</span><div className="hours-value"><strong>{requestHours}</strong><em>小時</em></div></div></div></section>
              <section className="form-section reason-section"><label><FileText size={23} />加班事由</label><textarea aria-label="加班事由" maxLength={200} value={reason} onChange={(event) => setReason(event.target.value)} /><small>{reason.length} / 200</small></section>
              <section className="impact"><h2>本週加班時數 <small>（{weekLabel}）</small></h2><div className="chart-wrap"><ResponsiveContainer width="100%" height={270}><PieChart><Pie data={chart} dataKey="value" innerRadius={73} outerRadius={110} startAngle={90} endAngle={-270} paddingAngle={1}>{chart.map((entry) => <Cell key={entry.name} fill={entry.color} />)}</Pie></PieChart></ResponsiveContainer><div className="chart-center"><span>送出後預估</span><strong>{projected}</strong><small>小時</small></div></div><div className="legend">{chart.slice(0, 3).map((entry) => <p key={entry.name}><i style={{ background: entry.color }} />{entry.name}<b>{entry.value} 小時</b></p>)}</div><div className="projection"><span>送出後預估總時數</span><b>{projected} 小時（{Math.round(projected / 20 * 100)}%）</b></div></section>
            </div>
            <button className="primary" type="submit"><Check size={22} weight="bold" />確認並送出</button>
          </form>
          <RequestTable title="近期申請紀錄" rows={currentEmployeeRequests.slice(0, 4)} />
        </>}

        {view === "紀錄" && <Page title="我的加班紀錄" subtitle="查看申請狀態與每週累計時數。"><RequestTable rows={currentEmployeeRequests} /></Page>}
        {view === "審核" && <Page title="主管審核作業" subtitle="待審核申請依送出時間排序。"><div className="review-list">{requests.filter((request) => request.status === "待審核").map((request) => <article key={request.id}><div className="review-person"><UserCircle size={42} weight="fill" /><span><b>{request.name}</b><small>{request.department}</small></span></div><div className="review-main"><b>{request.date}　{request.time}　共 {request.hours} 小時</b><p>{request.reason}</p></div><div className="review-actions"><button className="reject" onClick={() => decide(request.id, "已駁回")}><X size={18} />駁回</button><button className="approve" onClick={() => decide(request.id, "已核准")}><Check size={18} />核准</button></div></article>)}</div></Page>}
        {view === "報表" && <Page title="秘書報表中心" subtitle="彙整主管核准資料與匯入檢核。"><div className="report-summary"><div><span>已核准申請</span><strong>{requests.filter((request) => request.status === "已核准").length}</strong><small>筆申請</small></div><div><span>待主管審核</span><strong>{requests.filter((request) => request.status === "待審核").length}</strong><small>筆申請</small></div><div><span>已核准時數</span><strong>{approvedHours}</strong><small>小時</small></div></div>{DEMO_MODE && <><div className="import-head"><div><h2>匯入檢核示範</h2><p>以下全部為 synthetic data，用於展示格式與異常檢查。</p></div><button onClick={() => setImported(true)}><TrayArrowDown size={20} />{imported ? "已模擬匯入" : "模擬匯入"}</button></div><ImportTable rows={demoImportedRows} imported={imported} /></>}</Page>}
        {view === "權限" && role === "ADMIN" && <Page title="人員與權限" subtitle="設定每位使用者可使用的前臺或管理功能。"><UserPermissions /></Page>}
      </main>
    </div>
  );
}

function Page({ title, subtitle, children }) {
  return <><section className="heading"><h1>{title}</h1><p>{subtitle}</p></section>{children}</>;
}

function RequestTable({ title, rows }) {
  return <section className="data-section">{title && <h2><ListChecks size={24} />{title}</h2>}<div className="table-scroll"><table><thead><tr><th>加班日期</th><th>時段</th><th>時數</th><th>事由</th><th>狀態</th></tr></thead><tbody>{rows.map((request) => <tr key={request.id}><td>{request.date}</td><td>{request.time}</td><td>{request.hours} 小時</td><td>{request.reason}</td><td><Status>{request.status}</Status></td></tr>)}</tbody></table></div></section>;
}

function ImportTable({ rows, imported }) {
  return <section className="data-section import-table"><div className="table-scroll"><table><thead><tr><th>姓名</th><th>類型</th><th>日期</th><th>時段</th><th>原始時數</th><th>系統計算</th><th>事由</th><th>檢核結果</th></tr></thead><tbody>{rows.map((row, index) => <tr key={index}><td>{row.name}</td><td>{row.type}</td><td>{row.date}</td><td>{row.time}</td><td>{row.stated}</td><td>{row.calculated}</td><td>{row.reason}</td><td>{row.issue ? <span className="issue"><WarningCircle size={17} />{row.issue}</span> : imported ? <span className="ok"><CheckCircle size={17} />已模擬匯入</span> : <span className="ok"><CheckCircle size={17} />格式正常</span>}</td></tr>)}</tbody></table></div></section>;
}

function UserPermissions() {
  const demoUsers = [
    { display_name: "測試同仁 A", email: "staff@example.edu.tw", employee_id: "D001", department: "示範單位", role: "EMPLOYEE" },
    { display_name: "測試主管", email: "manager@example.edu.tw", employee_id: "D002", department: "示範單位", role: "MANAGER" },
    { display_name: "測試秘書", email: "secretary@example.edu.tw", employee_id: "D003", department: "示範單位", role: "SECRETARY" },
  ];
  const [users, setUsers] = useState(DEMO_MODE ? demoUsers : []);
  const [message, setMessage] = useState(DEMO_MODE ? "展示模式：角色調整只保留在目前畫面。" : "正在載入使用者…");

  useEffect(() => {
    if (DEMO_MODE) return;
    fetch("/api/users").then(async (response) => {
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "無法載入使用者");
      setUsers(data.users || []);
      setMessage(data.users?.length ? "" : "尚無其他使用者登入");
    }).catch(() => setMessage("無法載入使用者"));
  }, []);

  async function update(employeeId, role) {
    if (DEMO_MODE) {
      setUsers((list) => list.map((user) => user.employee_id === employeeId ? { ...user, role } : user));
      setMessage("展示角色已更新；重新整理後會還原。");
      return;
    }
    try {
      const response = await fetch(`/api/users/${encodeURIComponent(employeeId)}/role`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ role }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "角色更新失敗");
      setUsers((list) => list.map((user) => user.employee_id === employeeId ? { ...user, role } : user));
      setMessage("角色已更新。");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "角色更新失敗");
    }
  }

  return <section className="permissions">{message && <p className="permission-message">{message}</p>}<div className="table-scroll"><table><thead><tr><th>姓名</th><th>Email</th><th>員工編號</th><th>部門</th><th>角色</th></tr></thead><tbody>{users.map((user) => <tr key={user.employee_id}><td>{user.display_name}</td><td>{user.email || ""}</td><td>{user.employee_id}</td><td>{user.department}</td><td><select aria-label={`${user.display_name}的角色`} value={user.role} onChange={(event) => update(user.employee_id, event.target.value)}><option value="EMPLOYEE">同仁</option><option value="MANAGER">主管</option><option value="SECRETARY">秘書</option><option value="ADMIN">系統管理者</option></select></td></tr>)}</tbody></table></div></section>;
}
