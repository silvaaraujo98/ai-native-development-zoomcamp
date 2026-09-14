export const columns = [
  { id: "todo", label: "To Do" },
  { id: "doing", label: "Doing" },
  { id: "paused", label: "Paused" },
  { id: "done", label: "Done" },
];

const today = new Date();
const isoDate = (date) => date.toISOString().slice(0, 10);
const addDays = (base, days) => {
  const next = new Date(base);
  next.setDate(next.getDate() + days);
  return isoDate(next);
};

let session = null;
let tasks = [
  {
    id: "task-1",
    title: "Review FastAPI contract",
    notes: "Sketch the endpoints before backend work starts.",
    dueDate: isoDate(today),
    priority: "High",
    category: "Project",
    recurrence: "None",
    column: "todo",
    completedAt: null,
    archived: false,
  },
  {
    id: "task-2",
    title: "Daily study block",
    notes: "Spend 45 minutes on the course material.",
    dueDate: addDays(today, -1),
    priority: "Medium",
    category: "Study",
    recurrence: "Daily",
    column: "doing",
    completedAt: null,
    archived: false,
  },
  {
    id: "task-3",
    title: "Plan demo recording",
    notes: "Show login, create, drag, complete recurring, archive.",
    dueDate: addDays(today, 3),
    priority: "Low",
    category: "Project",
    recurrence: "None",
    column: "paused",
    completedAt: null,
    archived: false,
  },
  {
    id: "task-4",
    title: "Clear inbox notes",
    notes: "Keep this visible until manually archived.",
    dueDate: addDays(today, -2),
    priority: "Medium",
    category: "Daily",
    recurrence: "Weekly",
    column: "done",
    completedAt: isoDate(today),
    archived: false,
  },
];

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function delay(value) {
  return new Promise((resolve) => setTimeout(() => resolve(clone(value)), 160));
}

function requireSession() {
  if (!session) throw new Error("You must be logged in.");
}

function nextId() {
  return `task-${crypto.randomUUID()}`;
}

function autoArchiveDoneTasks() {
  const sevenDaysAgo = addDays(today, -7);
  tasks = tasks.map((task) => {
    if (task.column === "done" && task.completedAt && task.completedAt < sevenDaysAgo) {
      return { ...task, archived: true };
    }
    return task;
  });
}

function nextDueDate(task) {
  if (!task.dueDate) return "";
  const days = task.recurrence === "Weekly" ? 7 : 1;
  return addDays(new Date(`${task.dueDate}T00:00:00`), days);
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
  };
}

export function getDueState(task) {
  if (!task.dueDate || task.column === "done") return "";
  const date = task.dueDate;
  const now = isoDate(today);
  if (date === now) return "due-today";
  if (date < now) return "overdue";
  return "";
}

export const api = {
  async login({ username, password }) {
    if (!username.trim() || !password.trim()) {
      throw new Error("Enter a username and password.");
    }
    if (password !== "demo") {
      throw new Error("Invalid credentials. Try demo / demo.");
    }
    session = { user: { id: "user-1", name: username.trim() } };
    return delay(session);
  },

  async logout() {
    session = null;
    return delay({ ok: true });
  },

  async getCurrentUser() {
    requireSession();
    return delay(session.user);
  },

  async getBoard() {
    requireSession();
    autoArchiveDoneTasks();
    return delay({ columns, tasks: tasks.filter((task) => !task.archived) });
  },

  async getDashboardSummary() {
    requireSession();
    const activeTasks = tasks.filter((task) => !task.archived);
    return delay({
      dueToday: activeTasks.filter((task) => getDueState(task) === "due-today").length,
      overdue: activeTasks.filter((task) => getDueState(task) === "overdue").length,
    });
  },

  async createTask(input) {
    requireSession();
    const task = {
      ...emptyTaskForm(),
      ...input,
      id: nextId(),
      column: "todo",
      completedAt: null,
      archived: false,
    };
    tasks = [task, ...tasks];
    return delay(task);
  },

  async updateTask(id, input) {
    requireSession();
    let updated;
    tasks = tasks.map((task) => {
      if (task.id !== id) return task;
      updated = { ...task, ...input, id };
      return updated;
    });
    return delay(updated);
  },

  async deleteTask(id) {
    requireSession();
    tasks = tasks.filter((task) => task.id !== id);
    return delay({ ok: true });
  },

  async moveTask(id, column) {
    requireSession();
    let copiedTask = null;
    tasks = tasks.map((task) => {
      if (task.id !== id) return task;
      const moved = {
        ...task,
        column,
        completedAt: column === "done" ? isoDate(today) : null,
      };
      if (column === "done" && task.column !== "done" && task.recurrence !== "None") {
        copiedTask = {
          ...task,
          id: nextId(),
          column: "todo",
          dueDate: nextDueDate(task),
          completedAt: null,
          archived: false,
        };
      }
      return moved;
    });
    if (copiedTask) tasks = [copiedTask, ...tasks];
    return delay({ ok: true });
  },

  async archiveTask(id) {
    requireSession();
    tasks = tasks.map((task) => (task.id === id ? { ...task, archived: true } : task));
    return delay({ ok: true });
  },
};
