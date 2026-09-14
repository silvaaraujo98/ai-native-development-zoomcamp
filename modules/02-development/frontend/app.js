import { createMockInterviewService } from "./services.js";

const service = createMockInterviewService();
const app = document.querySelector("#app");

let route = "dashboard";
let activeSessionId = "session-demo";
let selectedElementId = null;
let activeTool = "select";
let currentStroke = null;
let drag = null;
let zoom = 0.8;
let toastTimer = null;

const icons = {
  dashboard: "▦",
  create: "+",
  lobby: "↪",
  canvas: "✎",
  review: "◴",
  select: "⌖",
  pan: "✥",
  pen: "∿",
  text: "T",
  connector: "→",
  eraser: "⌫",
  fit: "□",
  undo: "↶",
  redo: "↷"
};

function setRoute(next, sessionId = activeSessionId) {
  route = next;
  activeSessionId = sessionId;
  selectedElementId = null;
  render();
}

function toast(message) {
  clearTimeout(toastTimer);
  let node = document.querySelector(".toast");
  if (!node) {
    node = document.createElement("div");
    node.className = "toast";
    document.body.append(node);
  }
  node.textContent = message;
  toastTimer = setTimeout(() => node.remove(), 2600);
}

function statusPill(state) {
  const className = state === "live" ? "ok" : state === "ended" ? "warn" : "";
  return `<span class="pill ${className}">${state}</span>`;
}

async function render() {
  const sessions = await service.listSessions();
  const active = sessions.find((session) => session.id === activeSessionId) || sessions[0];
  activeSessionId = active?.id || activeSessionId;
  app.innerHTML = `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand"><span class="brand-mark">SD</span><span>Interview Studio</span></div>
        <nav class="nav" aria-label="Main navigation">
          ${navButton("dashboard", "Dashboard")}
          ${navButton("create", "New interview")}
          ${navButton("lobby", "Candidate lobby")}
          ${navButton("canvas", "Live canvas")}
          ${navButton("review", "Review")}
        </nav>
        <div class="sidebar-card">Mock services are active. Sessions, links, participants, and canvas changes are saved in this browser.</div>
      </aside>
      <main class="main">
        ${topbar(active)}
        <section class="workspace">${await viewFor(route, sessions, active)}</section>
      </main>
    </div>
  `;
  bindGlobalNavigation();
  bindRouteHandlers();
}

function navButton(id, label) {
  return `<button class="${route === id ? "active" : ""}" data-route="${id}"><span aria-hidden="true">${icons[id]}</span> ${label}</button>`;
}

function topbar(session) {
  return `
    <header class="topbar">
      <div>
        <h1>${session ? escapeHtml(session.title) : "System design interviews"}</h1>
        <p>${session ? `${session.participants.filter((p) => p.active).length} active participants · autosaved mock session` : "Create an interview to begin."}</p>
      </div>
      <div class="top-actions">
        <span class="pill ok">Connected</span>
        ${session ? statusPill(session.state) : ""}
        ${session ? `<button data-action="copy-link">Copy link</button>` : ""}
        ${session && session.state !== "ended" ? `<button class="danger" data-action="end">End</button>` : ""}
      </div>
    </header>
  `;
}

async function viewFor(currentRoute, sessions, active) {
  if (currentRoute === "create") return createView();
  if (currentRoute === "lobby") return lobbyView(active);
  if (currentRoute === "canvas") return canvasView(await service.getSession(active.id));
  if (currentRoute === "review") return reviewView(await service.getSession(active.id));
  return dashboardView(sessions);
}

function dashboardView(sessions) {
  return `
    <div class="dashboard-grid">
      <section class="panel">
        <div class="panel-header">
          <h2>Owned interviews</h2>
          <button class="primary" data-route="create">New interview</button>
        </div>
        <div class="panel-body session-list">
          ${sessions.map((session) => `
            <article class="session-item">
              <div class="row">
                <div class="session-title">${escapeHtml(session.title)}</div>
                ${statusPill(session.state)}
              </div>
              <div class="meta">${session.participants.map((p) => escapeHtml(p.name)).join(", ")} · ${session.elementCount} elements · updated ${new Date(session.updatedAt).toLocaleString()}</div>
              <div class="row">
                <button data-open="${session.id}">Open</button>
                <button data-copy="${session.id}">Copy link</button>
                <button data-duplicate="${session.id}">Duplicate</button>
                <button data-review="${session.id}">Review</button>
              </div>
            </article>
          `).join("")}
        </div>
      </section>
      <aside class="panel">
        <div class="panel-header"><h2>MVP readiness</h2></div>
        <div class="panel-body form">
          ${metric("Collaboration", "Presence, cursors, mock fan-out")}
          ${metric("Canvas", "Components, connectors, freehand")}
          ${metric("Security", "Revocable guest link model")}
          ${metric("Recovery", "Browser persistence and reconnect states")}
          <div class="notice">Use the mock service as the seam for a real API later. The UI does not call storage directly.</div>
        </div>
      </aside>
    </div>
  `;
}

function metric(label, value) {
  return `<div><div class="section-title">${label}</div><div class="meta">${value}</div></div>`;
}

function createView() {
  return `
    <section class="panel" style="max-width: 760px">
      <div class="panel-header"><h2>Create interview</h2></div>
      <form class="panel-body form" id="create-form">
        <label class="label">Title <input name="title" required value="Design a collaborative document editor" /></label>
        <label class="label">Problem statement <textarea name="prompt">Design a browser-based editor where multiple people can edit the same document in real time.</textarea></label>
        <label class="label">Duration <select name="duration"><option>45 minutes</option><option>60 minutes</option><option>90 minutes</option></select></label>
        <button class="primary" type="submit">Create candidate link</button>
      </form>
    </section>
  `;
}

function lobbyView(session) {
  const token = session.link?.token || "no-active-link";
  return `
    <section class="panel" style="max-width: 720px">
      <div class="panel-header">
        <h2>Candidate lobby</h2>
        ${session.link?.revokedAt ? '<span class="pill warn">link revoked</span>' : '<span class="pill ok">joinable</span>'}
      </div>
      <div class="panel-body form">
        <div>
          <div class="section-title">${escapeHtml(session.title)}</div>
          <p class="meta">Canvas activity is saved for interviewer review. The prompt appears after joining.</p>
        </div>
        <label class="label">Display name <input id="candidate-name" value="Alex Candidate" /></label>
        <button class="primary" data-join-token="${token}">Join interview</button>
        <div class="notice">Shareable link token: ${escapeHtml(token)}</div>
      </div>
    </section>
  `;
}

function canvasView(session) {
  const selected = session.canvas.elements.find((element) => element.id === selectedElementId);
  return `
    <div class="canvas-layout">
      <aside class="toolbar" aria-label="Canvas tools">
        ${toolButton("select", "Select")}
        ${toolButton("pan", "Pan")}
        ${toolButton("pen", "Pen")}
        ${toolButton("connector", "Connector")}
        ${toolButton("text", "Text")}
        ${toolButton("eraser", "Delete")}
      </aside>
      <div class="canvas-wrap">
        ${canvasSvg(session, false)}
        <div class="floating-status">
          <span class="pill ok">Autosaved</span>
          <span class="pill">${Math.round(zoom * 100)}%</span>
        </div>
      </div>
      <aside class="right-panel">
        <div class="right-section">
          <div class="section-title">Components</div>
          <div class="palette">
            ${Object.entries(service.componentDefaults).map(([type, defaults]) => `<button data-add-type="${type}"><strong>${escapeHtml(defaults.label)}</strong><span class="meta">${type}</span></button>`).join("")}
          </div>
        </div>
        <div class="right-section">
          <div class="section-title">Selection</div>
          ${selected ? propertiesForm(selected) : `<p class="meta">${escapeHtml(session.prompt)}</p>`}
        </div>
        <div class="right-section participants">
          <div class="section-title">Participants</div>
          ${session.participants.map((p) => `<div class="participant"><span class="dot" style="background:${p.color}"></span><span>${escapeHtml(p.name)}</span><span class="meta">${p.role}${p.active ? "" : " · away"}</span></div>`).join("")}
          <button data-action="toggle-lock">${session.candidateEditingEnabled ? "Lock candidate editing" : "Unlock candidate editing"}</button>
        </div>
      </aside>
    </div>
  `;
}

function toolButton(id, title) {
  return `<button class="icon tool ${activeTool === id ? "active" : ""}" title="${title}" aria-label="${title}" data-tool="${id}">${icons[id]}</button>`;
}

function propertiesForm(element) {
  return `
    <form class="form" id="properties-form">
      <label class="label">Label <input name="label" value="${escapeAttr(element.label)}" /></label>
      <label class="label">Description <textarea name="description">${escapeHtml(element.description || "")}</textarea></label>
      <div class="row">
        <button class="primary" type="submit">Save</button>
        <button class="danger" type="button" data-delete-selected>Delete</button>
      </div>
    </form>
  `;
}

function canvasSvg(session, readonly) {
  const canvas = session.canvas;
  return `
    <svg class="canvas" data-readonly="${readonly}" viewBox="0 0 ${1400 / zoom} ${820 / zoom}" role="application" aria-label="Shared architecture canvas">
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#475569"></path>
        </marker>
      </defs>
      ${canvas.connections.map((connection) => connectionSvg(connection, canvas.elements)).join("")}
      ${canvas.strokes.map(strokeSvg).join("")}
      ${canvas.elements.map(elementSvg).join("")}
    </svg>
  `;
}

function connectionSvg(connection, elements) {
  const from = elements.find((element) => element.id === connection.from);
  const to = elements.find((element) => element.id === connection.to);
  if (!from || !to) return "";
  const x1 = from.x + from.w;
  const y1 = from.y + from.h / 2;
  const x2 = to.x;
  const y2 = to.y + to.h / 2;
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;
  return `
    <path class="connector" d="M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}" marker-end="url(#arrow)"></path>
    ${connection.label ? `<text class="connector-label" x="${midX - 24}" y="${midY - 8}">${escapeHtml(connection.label)}</text>` : ""}
  `;
}

function elementSvg(element) {
  const selected = selectedElementId === element.id ? "selected" : "";
  const shape = element.type === "database"
    ? `<path d="M0 16 C0 5, ${element.w} 5, ${element.w} 16 L${element.w} ${element.h - 16} C${element.w} ${element.h - 5}, 0 ${element.h - 5}, 0 ${element.h - 16} Z M0 16 C0 27, ${element.w} 27, ${element.w} 16" fill="${element.color}"></path>`
    : element.type === "note"
      ? `<path d="M0 0 H${element.w - 22} L${element.w} 22 V${element.h} H0 Z" fill="${element.color}"></path><path d="M${element.w - 22} 0 V22 H${element.w}" fill="#f8e978" stroke="#38465d"></path>`
      : `<rect width="${element.w}" height="${element.h}" rx="${element.type === "service" ? 7 : 4}" fill="${element.color}"></rect>`;
  return `
    <g class="element ${selected}" tabindex="0" data-element-id="${element.id}" transform="translate(${element.x} ${element.y})">
      ${shape}
      <text x="${element.w / 2}" y="${element.h / 2 + 5}" text-anchor="middle">${escapeHtml(truncate(element.label, 24))}</text>
    </g>
  `;
}

function strokeSvg(stroke) {
  const d = stroke.points.map((point, index) => `${index ? "L" : "M"} ${point[0]} ${point[1]}`).join(" ");
  return `<path class="stroke-path" d="${d}" stroke="${stroke.color}" stroke-width="${stroke.width}"></path>`;
}

function reviewView(session) {
  return `
    <div class="review-grid">
      <section class="panel">
        <div class="panel-header">
          <h2>Ended-session review</h2>
          <button data-export-json>Export JSON</button>
        </div>
        <div class="panel-body">
          <div class="review-canvas">${canvasSvg(session, true)}</div>
        </div>
      </section>
      <aside class="panel">
        <div class="panel-header"><h2>Session record</h2></div>
        <div class="panel-body form">
          ${metric("State", session.state)}
          ${metric("Participants", session.participants.map((p) => p.name).join(", "))}
          ${metric("Canvas", `${session.canvas.elements.length} elements, ${session.canvas.connections.length} connectors, ${session.canvas.strokes.length} strokes`)}
          <div class="notice">${escapeHtml(session.prompt)}</div>
        </div>
      </aside>
    </div>
  `;
}

function bindGlobalNavigation() {
  app.querySelectorAll("[data-route]").forEach((button) => {
    button.addEventListener("click", () => setRoute(button.dataset.route));
  });
  app.querySelector("[data-action='copy-link']")?.addEventListener("click", copyActiveLink);
  app.querySelector("[data-action='end']")?.addEventListener("click", async () => {
    if (confirm("End this interview and make the candidate view read-only?")) {
      await service.endSession(activeSessionId);
      toast("Interview ended and final snapshot saved.");
      setRoute("review");
    }
  });
}

function bindRouteHandlers() {
  app.querySelector("#create-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const session = await service.createSession({ title: data.get("title"), prompt: data.get("prompt") });
    await service.createCandidateLink(session.id);
    toast("Interview created.");
    setRoute("canvas", session.id);
  });
  app.querySelectorAll("[data-open]").forEach((button) => button.addEventListener("click", () => setRoute("canvas", button.dataset.open)));
  app.querySelectorAll("[data-review]").forEach((button) => button.addEventListener("click", () => setRoute("review", button.dataset.review)));
  app.querySelectorAll("[data-copy]").forEach((button) => button.addEventListener("click", () => copyLink(button.dataset.copy)));
  app.querySelectorAll("[data-duplicate]").forEach((button) => button.addEventListener("click", async () => {
    const copy = await service.duplicateSession(button.dataset.duplicate);
    toast("Template duplicated.");
    setRoute("canvas", copy.id);
  }));
  app.querySelector("[data-join-token]")?.addEventListener("click", async (event) => {
    try {
      const name = app.querySelector("#candidate-name").value;
      const result = await service.joinWithToken(event.currentTarget.dataset.joinToken, name);
      toast(`${result.participant.name} joined.`);
      setRoute("canvas", result.session.id);
    } catch (error) {
      toast(error.message);
    }
  });
  bindCanvasHandlers();
}

function bindCanvasHandlers() {
  app.querySelectorAll("[data-tool]").forEach((button) => button.addEventListener("click", () => {
    activeTool = button.dataset.tool;
    render();
  }));
  app.querySelectorAll("[data-add-type]").forEach((button, index) => button.addEventListener("click", async () => {
    await service.addElement(activeSessionId, button.dataset.addType, 130 + index * 18, 100 + index * 16);
    toast("Component added.");
    render();
  }));
  app.querySelector("#properties-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    await service.updateElement(activeSessionId, selectedElementId, {
      label: data.get("label"),
      description: data.get("description")
    });
    toast("Selection updated.");
    render();
  });
  app.querySelector("[data-delete-selected]")?.addEventListener("click", async () => {
    await service.deleteElement(activeSessionId, selectedElementId);
    selectedElementId = null;
    render();
  });
  app.querySelector("[data-action='toggle-lock']")?.addEventListener("click", async () => {
    const session = await service.getSession(activeSessionId);
    await service.updateSession(activeSessionId, { candidateEditingEnabled: !session.candidateEditingEnabled });
    toast(session.candidateEditingEnabled ? "Candidate editing locked." : "Candidate editing unlocked.");
    render();
  });
  app.querySelector("[data-export-json]")?.addEventListener("click", async () => {
    const json = await service.exportSessionJson(activeSessionId);
    await navigator.clipboard?.writeText(json);
    toast("Session JSON copied.");
  });
  const svg = app.querySelector("svg.canvas:not([data-readonly='true'])");
  if (!svg) return;
  svg.addEventListener("pointerdown", onCanvasPointerDown);
  svg.addEventListener("pointermove", onCanvasPointerMove);
  svg.addEventListener("pointerup", onCanvasPointerUp);
  svg.addEventListener("pointerleave", onCanvasPointerUp);
  svg.addEventListener("click", (event) => {
    const target = event.target.closest?.("[data-element-id]");
    if (target) {
      selectedElementId = target.dataset.elementId;
      render();
    }
  });
}

async function onCanvasPointerDown(event) {
  const svg = event.currentTarget;
  const point = svgPoint(svg, event);
  const target = event.target.closest?.("[data-element-id]");
  if (activeTool === "pen") {
    currentStroke = { color: "#0f766e", width: 4, points: [[point.x, point.y]] };
    svg.setPointerCapture(event.pointerId);
    return;
  }
  if (activeTool === "select" && target) {
    selectedElementId = target.dataset.elementId;
    const session = await service.getSession(activeSessionId);
    const element = session.canvas.elements.find((item) => item.id === selectedElementId);
    drag = { id: selectedElementId, dx: point.x - element.x, dy: point.y - element.y };
    svg.setPointerCapture(event.pointerId);
  }
}

async function onCanvasPointerMove(event) {
  const svg = event.currentTarget;
  const point = svgPoint(svg, event);
  if (currentStroke) {
    currentStroke.points.push([point.x, point.y]);
    const path = strokeSvg({ ...currentStroke, id: "preview" });
    let preview = svg.querySelector("[data-preview-stroke]");
    if (!preview) {
      preview = document.createElementNS("http://www.w3.org/2000/svg", "g");
      preview.dataset.previewStroke = "true";
      svg.append(preview);
    }
    preview.innerHTML = path;
  }
  if (drag) {
    await service.updateElement(activeSessionId, drag.id, { x: Math.round(point.x - drag.dx), y: Math.round(point.y - drag.dy) });
    render();
  }
}

async function onCanvasPointerUp() {
  if (currentStroke && currentStroke.points.length > 1) {
    await service.addStroke(activeSessionId, currentStroke);
    currentStroke = null;
    render();
  }
  drag = null;
}

function svgPoint(svg, event) {
  const pt = svg.createSVGPoint();
  pt.x = event.clientX;
  pt.y = event.clientY;
  const result = pt.matrixTransform(svg.getScreenCTM().inverse());
  return { x: result.x, y: result.y };
}

async function copyActiveLink() {
  await copyLink(activeSessionId);
}

async function copyLink(sessionId) {
  const session = await service.getSession(sessionId);
  const link = session.link || await service.createCandidateLink(sessionId);
  const url = `${location.origin}${location.pathname}#join=${link.token}`;
  await navigator.clipboard?.writeText(url);
  toast("Candidate link copied.");
}

function truncate(text, length) {
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}

service.subscribe(() => {
  if (route !== "canvas") return;
});

render();
