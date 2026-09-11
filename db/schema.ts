export const schema = {
  overtimeRequests: {
    table: "overtime_requests",
    columns: ["id", "employee_id", "employee_name", "department", "overtime_date", "start_time", "end_time", "duration", "reason", "request_type", "status", "submitted_at", "updated_at"],
  },
  approvalLogs: {
    table: "approval_logs",
    columns: ["id", "request_id", "action", "actor_name", "note", "created_at"],
  },
  appUsers: {
    table: "app_users",
    columns: ["id", "auth_user_id", "email", "display_name", "employee_id", "department", "role", "created_at"],
  },
  staffCredentials: {
    table: "staff_credentials",
    columns: ["email", "password_hash", "must_change_password", "created_at", "updated_at"],
  },
  staffSessions: {
    table: "staff_sessions",
    columns: ["token_hash", "email", "expires_at", "created_at"],
  },
};
