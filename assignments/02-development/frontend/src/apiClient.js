export const columns = [
  { id: "todo", label: "To Do" },
  { id: "doing", label: "Doing" },
  { id: "paused", label: "Paused" },
  { id: "done", label: "Done" },
];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const TOKEN_KEY = "focusboard-token";

const today = new Date();
const isoDate = (date) => date.toISOString().slice(0, 10);

function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) return null;

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      clearToken();
    }
    throw new Error(body?.detail ?? "Request failed.");
  }

  return body;
}

function toFrontendTask(task) {
  return {
    id: task.id,
    title: task.title,
    notes: task.notes ?? "",
    dueDate: task.due_date ?? "",
    priority: task.priority,
    category: task.category,
    recurrence: task.recurrence,
    column: task.column,
    completedAt: task.completed_at,
    archived: task.archived,
    subtasks: task.subtasks ?? [],
  };
}

function toBackendTask(task) {
  return {
    title: task.title,
    notes: task.notes ?? "",
    due_date: task.dueDate || null,
    priority: task.priority,
    category: task.category,
    recurrence: task.recurrence,
    column: task.column,
    subtasks: (task.subtasks ?? []).map((subtask) => ({
      id: subtask.id?.startsWith("draft-") ? undefined : subtask.id,
      title: subtask.title,
      completed: subtask.completed,
    })),
  };
}

export function emptyTaskForm() {
  return {
    title: "",
    notes: "",
    dueDate: isoDate(today),
    priority: "Medium",
    category: "Daily",
    recurrence: "None",
    column: "todo",
    subtasks: [],
  };
}

export function getDueState(task) {
  if (!task.dueDate || task.column === "done") return "";
  const now = isoDate(today);
  if (task.dueDate === now) return "due-today";
  if (task.dueDate < now) return "overdue";
  return "";
}

export const api = {
  async login({ username, password }) {
    const session = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    setToken(session.access_token);
    return session;
  },

  async logout() {
    clearToken();
    return { ok: true };
  },

  async getCurrentUser() {
    if (!getToken()) {
      throw new Error("You must be logged in.");
    }
    return request("/auth/me");
  },

  async getBoard() {
    const board = await request("/board");
    return {
      columns: board.columns,
      tasks: board.tasks.map(toFrontendTask),
    };
  },

  async getDashboardSummary() {
    const summary = await request("/dashboard/summary");
    return {
      dueToday: summary.due_today,
      overdue: summary.overdue,
      activeTasks: summary.active_tasks,
      doneVisible: summary.done_visible,
    };
  },

  async createTask(input) {
    const task = await request("/tasks", {
      method: "POST",
      body: JSON.stringify(toBackendTask(input)),
    });
    return toFrontendTask(task);
  },

  async updateTask(id, input) {
    const task = await request(`/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(toBackendTask(input)),
    });
    return toFrontendTask(task);
  },

  async deleteTask(id) {
    return request(`/tasks/${id}`, { method: "DELETE" });
  },

  async moveTask(id, column) {
    const task = await request(`/tasks/${id}/move`, {
      method: "POST",
      body: JSON.stringify({ column }),
    });
    return toFrontendTask(task);
  },

  async archiveTask(id) {
    const task = await request(`/tasks/${id}/archive`, { method: "POST" });
    return toFrontendTask(task);
  },
};
