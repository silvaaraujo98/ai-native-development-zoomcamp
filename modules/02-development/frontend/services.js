const STORAGE_KEY = "sysdesign.interview.mock.v1";

const componentDefaults = {
  service: { label: "Service", w: 150, h: 76, color: "#d9e8ff" },
  database: { label: "Database", w: 132, h: 86, color: "#dff7e8" },
  cache: { label: "Cache", w: 126, h: 72, color: "#fff1c2" },
  queue: { label: "Queue", w: 138, h: 72, color: "#f1e3ff" },
  gateway: { label: "API gateway", w: 152, h: 76, color: "#d6f1ff" },
  worker: { label: "Worker", w: 132, h: 76, color: "#ffe2d3" },
  client: { label: "Client", w: 128, h: 72, color: "#e9edf5" },
  vector: { label: "Vector DB", w: 140, h: 82, color: "#d8fbf4" },
  llm: { label: "LLM/model", w: 142, h: 76, color: "#efe9ff" },
  note: { label: "Assumption", w: 160, h: 110, color: "#fff59d" }
};

const seedSession = {
  id: "session-demo",
  title: "Design a real-time analytics platform",
  prompt: "Design a system that ingests user events, aggregates metrics in near real time, and exposes dashboards for product teams.",
  state: "live",
  candidateEditingEnabled: true,
  createdAt: "2026-08-03T14:00:00.000Z",
  updatedAt: "2026-08-03T14:22:00.000Z",
  link: { token: "candidate-demo-link", revokedAt: null, expiresAt: null, maxUses: 10 },
  participants: [
    { id: "p-owner", name: "Maya", role: "Owner", color: "#2563eb", active: true },
    { id: "p-candidate", name: "Jordan", role: "Candidate", color: "#059669", active: true },
    { id: "p-observer", name: "Ravi", role: "Observer", color: "#7c3aed", active: false }
  ],
  canvas: {
    elements: [
      makeElement("client", 70, 120, "Web clients"),
      makeElement("gateway", 300, 120, "API gateway"),
      makeElement("service", 540, 74, "Ingestion service"),
      makeElement("queue", 780, 120, "Event stream"),
      makeElement("worker", 540, 250, "Aggregation workers"),
      makeElement("database", 780, 250, "Metrics store"),
      makeElement("cache", 1010, 250, "Dashboard cache"),
      makeElement("note", 90, 300, "Clarify peak write rate and retention window")
    ],
    connections: [
      makeConnection("el-1", "el-2", "HTTPS"),
      makeConnection("el-2", "el-3", "validated events"),
      makeConnection("el-3", "el-4", "append"),
      makeConnection("el-4", "el-5", "consume"),
      makeConnection("el-5", "el-6", "write"),
      makeConnection("el-6", "el-7", "read-through")
    ],
    strokes: [
      { id: "stroke-1", color: "#e11d48", width: 4, points: [[520, 52], [645, 44], [705, 92]] }
    ]
  }
};

function makeId(prefix) {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function makeElement(type, x, y, label) {
  const defaults = componentDefaults[type] || componentDefaults.service;
  return {
    id: makeId("el"),
    type,
    x,
    y,
    w: defaults.w,
    h: defaults.h,
    label: label || defaults.label,
    color: defaults.color,
    description: ""
  };
}

function makeConnection(from, to, label = "") {
  return { id: makeId("conn"), from, to, label, directed: true, style: "solid" };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function initialState() {
  const session = clone(seedSession);
  session.canvas.elements.forEach((element, index) => {
    element.id = `el-${index + 1}`;
  });
  session.canvas.connections = [
    makeConnection("el-1", "el-2", "HTTPS"),
    makeConnection("el-2", "el-3", "validated events"),
    makeConnection("el-3", "el-4", "append"),
    makeConnection("el-4", "el-5", "consume"),
    makeConnection("el-5", "el-6", "write"),
    makeConnection("el-6", "el-7", "read-through")
  ].map((connection, index) => ({ ...connection, id: `conn-${index + 1}` }));
  return { sessions: [session], auditEvents: [] };
}

function createMemoryStore(seed = initialState()) {
  let state = clone(seed);
  return {
    load() {
      return clone(state);
    },
    save(next) {
      state = clone(next);
    },
    reset(next = initialState()) {
      state = clone(next);
    }
  };
}

function createLocalStorageStore(storage = globalThis.localStorage) {
  return {
    load() {
      const raw = storage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : initialState();
    },
    save(next) {
      storage.setItem(STORAGE_KEY, JSON.stringify(next));
    },
    reset(next = initialState()) {
      storage.setItem(STORAGE_KEY, JSON.stringify(next));
    }
  };
}

function createMockInterviewService(store = createLocalStorageStore()) {
  const listeners = new Set();

  function read() {
    return store.load();
  }

  function write(mutator, event) {
    const state = read();
    const result = mutator(state);
    if (event) state.auditEvents.unshift({ id: makeId("audit"), at: new Date().toISOString(), ...event });
    store.save(state);
    listeners.forEach((listener) => listener(clone(state)));
    return clone(result);
  }

  function findSession(state, sessionId) {
    const session = state.sessions.find((item) => item.id === sessionId);
    if (!session) throw new Error("Session not found");
    return session;
  }

  return {
    componentDefaults,
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    reset() {
      store.reset();
      listeners.forEach((listener) => listener(read()));
    },
    async listSessions() {
      return read().sessions.map(({ canvas, ...session }) => ({
        ...session,
        elementCount: canvas.elements.length,
        strokeCount: canvas.strokes.length
      }));
    },
    async createSession(input) {
      return write((state) => {
        const now = new Date().toISOString();
        const session = {
          id: makeId("session"),
          title: input.title.trim(),
          prompt: input.prompt.trim(),
          state: "draft",
          candidateEditingEnabled: true,
          createdAt: now,
          updatedAt: now,
          link: null,
          participants: [{ id: makeId("p"), name: "You", role: "Owner", color: "#2563eb", active: true }],
          canvas: { elements: [], connections: [], strokes: [] }
        };
        state.sessions.unshift(session);
        return session;
      }, { type: "session.created", label: input.title });
    },
    async createCandidateLink(sessionId) {
      return write((state) => {
        const session = findSession(state, sessionId);
        session.link = { token: makeId("join").replace("join-", ""), revokedAt: null, expiresAt: null, maxUses: 10 };
        session.updatedAt = new Date().toISOString();
        return session.link;
      }, { type: "link.rotated", sessionId });
    },
    async revokeCandidateLink(sessionId) {
      return write((state) => {
        const session = findSession(state, sessionId);
        if (session.link) session.link.revokedAt = new Date().toISOString();
        session.updatedAt = new Date().toISOString();
        return session.link;
      }, { type: "link.revoked", sessionId });
    },
    async joinWithToken(token, displayName) {
      return write((state) => {
        const session = state.sessions.find((item) => item.link?.token === token && !item.link.revokedAt && item.state !== "archived");
        if (!session) throw new Error("This interview link is no longer available.");
        if (session.state === "ended") throw new Error("This interview has ended.");
        const participant = { id: makeId("p"), name: displayName.trim(), role: "Candidate", color: "#dc2626", active: true };
        session.participants.push(participant);
        session.updatedAt = new Date().toISOString();
        return { session, participant };
      }, { type: "participant.joined", label: displayName });
    },
    async getSession(sessionId) {
      return findSession(read(), sessionId);
    },
    async updateSession(sessionId, patch) {
      return write((state) => {
        const session = findSession(state, sessionId);
        Object.assign(session, patch, { updatedAt: new Date().toISOString() });
        return session;
      }, { type: "session.updated", sessionId });
    },
    async endSession(sessionId) {
      return this.updateSession(sessionId, { state: "ended", endedAt: new Date().toISOString(), candidateEditingEnabled: false });
    },
    async duplicateSession(sessionId) {
      return write((state) => {
        const source = findSession(state, sessionId);
        const now = new Date().toISOString();
        const copy = clone(source);
        copy.id = makeId("session");
        copy.title = `${source.title} copy`;
        copy.state = "draft";
        copy.link = null;
        copy.createdAt = now;
        copy.updatedAt = now;
        copy.startedAt = null;
        copy.endedAt = null;
        state.sessions.unshift(copy);
        return copy;
      }, { type: "session.duplicated", sessionId });
    },
    async addElement(sessionId, type, x, y) {
      return write((state) => {
        const session = findSession(state, sessionId);
        const element = makeElement(type, x, y);
        session.canvas.elements.push(element);
        session.updatedAt = new Date().toISOString();
        return element;
      }, { type: "canvas.element_added", sessionId });
    },
    async updateElement(sessionId, elementId, patch) {
      return write((state) => {
        const session = findSession(state, sessionId);
        const element = session.canvas.elements.find((item) => item.id === elementId);
        if (!element) throw new Error("Element not found");
        Object.assign(element, patch);
        session.updatedAt = new Date().toISOString();
        return element;
      }, { type: "canvas.element_updated", sessionId });
    },
    async deleteElement(sessionId, elementId) {
      return write((state) => {
        const session = findSession(state, sessionId);
        session.canvas.elements = session.canvas.elements.filter((item) => item.id !== elementId);
        session.canvas.connections = session.canvas.connections.filter((item) => item.from !== elementId && item.to !== elementId);
        session.updatedAt = new Date().toISOString();
        return session.canvas;
      }, { type: "canvas.element_deleted", sessionId });
    },
    async addConnection(sessionId, from, to, label = "") {
      return write((state) => {
        const session = findSession(state, sessionId);
        const connection = makeConnection(from, to, label);
        session.canvas.connections.push(connection);
        session.updatedAt = new Date().toISOString();
        return connection;
      }, { type: "canvas.connection_added", sessionId });
    },
    async addStroke(sessionId, stroke) {
      return write((state) => {
        const session = findSession(state, sessionId);
        const next = { id: makeId("stroke"), color: stroke.color, width: stroke.width, points: stroke.points };
        session.canvas.strokes.push(next);
        session.updatedAt = new Date().toISOString();
        return next;
      }, { type: "canvas.stroke_added", sessionId });
    },
    async exportSessionJson(sessionId) {
      return JSON.stringify(findSession(read(), sessionId), null, 2);
    }
  };
}

export { createMockInterviewService, createMemoryStore, initialState, makeElement, makeConnection };
