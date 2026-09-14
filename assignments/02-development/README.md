# FocusBoard

FocusBoard is a full-stack personal Kanban app built for Homework 2 of the AI Native Development Zoomcamp. It helps one user manage daily, project, and study tasks across a fixed workflow:

- To Do
- Doing
- Paused
- Done

The app has a React frontend and a FastAPI backend. The frontend runs in the browser and talks to the backend API over HTTP.

## Demo Video

[Watch the FocusBoard demo](./app-demo.mp4)

## Tech Stack

- Frontend: React, Vite, Node.js
- Backend: Python, FastAPI, uv
- API contract: OpenAPI
- Tests: pytest

## Project Structure

```text
02-development/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── _docs/
│   └── specs.md
├── openapi.yaml
└── README.md
```

## Requirements

Install these before running the project:

- Python 3.12+
- uv
- Node.js
- npm

## Run The Full Application

You need two terminals: one for the backend and one for the frontend.

### 1. Start The Backend

From the project root:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend API will run at:

```text
http://127.0.0.1:8000
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

### 2. Start The Frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will usually run at:

```text
http://127.0.0.1:5173
```

Open that frontend URL in your browser to use the full application.

## Login

The demo backend initializes with this password:

```text
demo
```

Use the app login screen to sign in before accessing the board.

## Backend Tests

From the `backend` folder:

```powershell
uv run pytest
```

## Useful Commands

Run backend:

```powershell
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run frontend:

```powershell
cd frontend
npm run dev
```

Build frontend:

```powershell
cd frontend
npm run build
```

Run backend tests:

```powershell
cd backend
uv run pytest
```

## Notes

- `http://127.0.0.1:8000` is the backend API, not the full app UI.
- `http://127.0.0.1:5173` is the frontend app.
- The frontend uses `http://127.0.0.1:8000` as its default backend API URL.
- If port `8000` is already in use, stop the existing backend process or run the backend on another port and configure the frontend API URL accordingly.
