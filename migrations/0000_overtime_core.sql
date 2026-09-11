CREATE TABLE IF NOT EXISTS overtime_requests (
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
);

CREATE TABLE IF NOT EXISTS approval_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  actor_name TEXT NOT NULL,
  note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (request_id) REFERENCES overtime_requests(id)
);

CREATE TABLE IF NOT EXISTS app_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  auth_user_id TEXT NOT NULL UNIQUE,
  email TEXT,
  display_name TEXT NOT NULL,
  employee_id TEXT NOT NULL UNIQUE,
  department TEXT NOT NULL DEFAULT '未設定',
  role TEXT NOT NULL DEFAULT 'EMPLOYEE',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff_credentials (
  email TEXT PRIMARY KEY NOT NULL,
  password_hash TEXT NOT NULL,
  must_change_password INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff_sessions (
  token_hash TEXT PRIMARY KEY NOT NULL,
  email TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (email) REFERENCES staff_credentials(email) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_overtime_employee_date ON overtime_requests(employee_id, overtime_date);
CREATE INDEX IF NOT EXISTS idx_overtime_status_date ON overtime_requests(status, overtime_date);
CREATE INDEX IF NOT EXISTS idx_staff_sessions_email ON staff_sessions(email);
CREATE INDEX IF NOT EXISTS idx_staff_sessions_expires_at ON staff_sessions(expires_at);

PRAGMA optimize;
