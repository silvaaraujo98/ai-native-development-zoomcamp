import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, columns, emptyTaskForm, getDueState } from "./apiClient";
import "./styles.css";

function Login({ onLogin }) {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const session = await api.login({ username, password });
      onLogin(session.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel">
        <p className="eyebrow">Personal workflow</p>
        <h1>FocusBoard</h1>
        <p className="login-copy">
          A focused board for daily work, projects, and study tasks.
        </p>
        <form className="login-form" onSubmit={submit}>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error ? <p className="form-error">{error}</p> : null}
          <button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}

function TaskModal({ task, onClose, onSave }) {
  const [form, setForm] = useState(task ?? emptyTaskForm());
  const isEditing = Boolean(task?.id);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function submit(event) {
    event.preventDefault();
    if (!form.title.trim()) return;
    onSave({ ...form, title: form.title.trim() });
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="task-modal" onSubmit={submit}>
        <div className="modal-heading">
          <div>
            <p className="eyebrow">{isEditing ? "Edit task" : "New task"}</p>
            <h2>{isEditing ? "Update card" : "Create card"}</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close">
            x
          </button>
        </div>
        <label>
          Title
          <input
            autoFocus
            required
            value={form.title}
            onChange={(e) => update("title", e.target.value)}
          />
        </label>
        <label>
          Notes
          <textarea value={form.notes} onChange={(e) => update("notes", e.target.value)} />
        </label>
        <div className="form-grid">
          <label>
            Due date
            <input
              type="date"
              value={form.dueDate}
              onChange={(e) => update("dueDate", e.target.value)}
            />
          </label>
          <label>
            Priority
            <select value={form.priority} onChange={(e) => update("priority", e.target.value)}>
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </label>
          <label>
            Category
            <select value={form.category} onChange={(e) => update("category", e.target.value)}>
              <option>Daily</option>
              <option>Project</option>
              <option>Study</option>
            </select>
          </label>
          <label>
            Recurrence
            <select
              value={form.recurrence}
              onChange={(e) => update("recurrence", e.target.value)}
            >
              <option>None</option>
              <option>Daily</option>
              <option>Weekly</option>
            </select>
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit">{isEditing ? "Save changes" : "Create task"}</button>
        </div>
      </form>
    </div>
  );
}

function TaskCard({ task, onEdit, onDelete, onArchive, onDragStart, actionInProgress }) {
  const dueState = getDueState(task);
  const stopButtonDrag = (event) => event.stopPropagation();

  return (
    <article
      className={`task-card priority-${task.priority.toLowerCase()} ${dueState}`}
      draggable={!actionInProgress}
      onDragStart={(event) => onDragStart(event, task.id)}
    >
      <div className="card-topline">
        <span className="category">{task.category}</span>
        <span className="priority">{task.priority}</span>
      </div>
      <h3>{task.title}</h3>
      {task.notes ? <p>{task.notes}</p> : null}
      <div className="card-meta">
        <span>{task.dueDate || "No due date"}</span>
        <span>{task.recurrence}</span>
      </div>
      {dueState === "due-today" ? <strong className="due-label">Due today</strong> : null}
      {dueState === "overdue" ? <strong className="due-label overdue-label">Overdue</strong> : null}
      <div className="card-actions">
        <button type="button" onPointerDown={stopButtonDrag} onClick={() => onEdit(task)}>
          Edit
        </button>
        {task.column === "done" ? (
          <button
            type="button"
            disabled={actionInProgress}
            onPointerDown={stopButtonDrag}
            onClick={() => onArchive(task.id)}
          >
            {actionInProgress ? "Archiving..." : "Archive"}
          </button>
        ) : null}
        <button
          type="button"
          className="danger-button"
          disabled={actionInProgress}
          onPointerDown={stopButtonDrag}
          onClick={() => onDelete(task.id)}
        >
          {actionInProgress ? "Deleting..." : "Delete"}
        </button>
      </div>
    </article>
  );
}

function Board({ user, onLogout }) {
  const [tasks, setTasks] = useState([]);
  const [summary, setSummary] = useState({ dueToday: 0, overdue: 0 });
  const [modalTask, setModalTask] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [draggedId, setDraggedId] = useState(null);
  const [actionTaskId, setActionTaskId] = useState(null);
  const [error, setError] = useState("");

  async function refresh() {
    const [board, nextSummary] = await Promise.all([api.getBoard(), api.getDashboardSummary()]);
    setTasks(board.tasks);
    setSummary(nextSummary);
  }

  useEffect(() => {
    refresh();
  }, []);

  const grouped = useMemo(() => {
    return columns.reduce((acc, column) => {
      acc[column.id] = tasks.filter((task) => task.column === column.id);
      return acc;
    }, {});
  }, [tasks]);

  function createTask() {
    setModalTask(null);
    setModalOpen(true);
  }

  async function saveTask(task) {
    setError("");
    if (task.id) {
      await api.updateTask(task.id, task);
    } else {
      await api.createTask(task);
    }
    setModalOpen(false);
    await refresh();
  }

  async function dropOnColumn(columnId) {
    if (!draggedId) return;
    setError("");
    await api.moveTask(draggedId, columnId);
    setDraggedId(null);
    await refresh();
  }

  async function runTaskAction(id, action) {
    setError("");
    setDraggedId(null);
    setActionTaskId(id);
    try {
      await action(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionTaskId(null);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Signed in as {user.name}</p>
          <h1>FocusBoard</h1>
        </div>
        <div className="header-actions">
          <button type="button" onClick={createTask}>
            New task
          </button>
          <button type="button" className="secondary-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      </header>

      <section className="summary-row" aria-label="Dashboard summary">
        <div>
          <span>Due today</span>
          <strong>{summary.dueToday}</strong>
        </div>
        <div>
          <span>Overdue</span>
          <strong>{summary.overdue}</strong>
        </div>
        <div>
          <span>Active tasks</span>
          <strong>{tasks.filter((task) => task.column !== "done").length}</strong>
        </div>
        <div>
          <span>Done visible</span>
          <strong>{grouped.done?.length ?? 0}</strong>
        </div>
      </section>

      {error ? <p className="form-error board-error">{error}</p> : null}

      <section className="board" aria-label="Kanban board">
        {columns.map((column) => (
          <div
            className="column"
            key={column.id}
            onDragOver={(event) => event.preventDefault()}
            onDrop={() => dropOnColumn(column.id)}
          >
            <div className="column-header">
              <h2>{column.label}</h2>
              <span>{grouped[column.id]?.length ?? 0}</span>
            </div>
            <div className="task-list">
              {(grouped[column.id] ?? []).map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onEdit={(nextTask) => {
                    setModalTask(nextTask);
                    setModalOpen(true);
                  }}
                  onDelete={async (id) => {
                    await runTaskAction(id, api.deleteTask);
                  }}
                  onArchive={async (id) => {
                    await runTaskAction(id, api.archiveTask);
                  }}
                  onDragStart={(event, id) => {
                    if (actionTaskId) {
                      event.preventDefault();
                      return;
                    }
                    event.dataTransfer.effectAllowed = "move";
                    setDraggedId(id);
                  }}
                  actionInProgress={actionTaskId === task.id}
                />
              ))}
            </div>
          </div>
        ))}
      </section>

      {modalOpen ? (
        <TaskModal task={modalTask} onClose={() => setModalOpen(false)} onSave={saveTask} />
      ) : null}
    </main>
  );
}

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    api.getCurrentUser().then(setUser).catch(() => setUser(null));
  }, []);

  if (!user) return <Login onLogin={setUser} />;
  return <Board user={user} onLogout={() => api.logout().then(() => setUser(null))} />;
}

createRoot(document.getElementById("root")).render(<App />);
