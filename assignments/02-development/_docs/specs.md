# FocusBoard - Product and Technical Scope

## Product Vision

Build FocusBoard, a personal Kanban board for managing daily to-dos, project tasks, and study tasks. The product should be simple, polished, and portfolio-ready, with clear product decisions and a clean full-stack architecture.

The project should demonstrate thoughtful product scope, API-first development, authentication, drag-and-drop interaction, and database-agnostic backend design.

## Target User

A single personal user who wants one focused Kanban board for organizing daily, project, and study work.

## MVP Goal

Create a polished personal Kanban web app where a user can log in, manage categorized tasks, move them through a fixed workflow, track due dates, and keep completion history.

The MVP should be strong enough to impress product-minded reviewers by showing clear tradeoffs, useful workflow design, and clean implementation boundaries.

## Fixed Board Workflow

The board has exactly four columns:

- To Do
- Doing
- Paused
- Done

Columns are fixed for the MVP. Users cannot add, rename, reorder, or delete columns.

## Task Card Fields

Each task card must include:

- Title
- Notes
- Due date
- Priority
- Category
- Recurrence setting

Priority values:

- Low
- Medium
- High

Category values:

- Daily
- Project
- Study

Recurrence values:

- None
- Daily
- Weekly

## Core MVP Features

### Authentication

The app must require login from the start.

MVP authentication uses:

- Username
- Password

Each authenticated user has exactly one board.

### Board

The user can view one personal board with the four fixed columns.

The board must show:

- Cards grouped by column
- Count of tasks in each column
- Summary of tasks due today
- Summary of overdue tasks

### Task Management

The user can:

- Create a task
- Edit a task
- Delete a task
- Move a task between columns using drag and drop
- Set title, notes, due date, priority, category, and recurrence
- View visual indication for tasks due today
- View visual indication for overdue tasks

### Recurring Tasks

Recurring tasks support simple daily and weekly recurrence.

When a recurring task is moved to Done:

- The completed task stays in Done
- A new task copy is created in To Do
- The new task receives the next due date based on the recurrence rule
- The completed task remains part of completion history

### Done Task Cleanup

Done tasks should support:

- Manual archive
- Automatic archive after 7 days in Done

Archived tasks should no longer appear on the active board.

## Out Of Scope For MVP

Do not include these in the MVP:

- Multiple boards per user
- Team sharing
- Comments
- Attachments
- Search
- Filtering
- Custom columns
- Custom priorities
- Custom categories
- Calendar view
- Notifications or reminders
- OAuth login
- Mobile app
- Desktop app
- Offline sync
- Multi-device sync beyond normal backend persistence

Small UX improvements are allowed if they do not expand the core product scope.

## Technical Constraints

### Repository Structure

Use this structure:

```text
/backend
/docs
/frontend
AGENTS.md
openapi.yaml
```

### Architecture

Use an API-first workflow.

`openapi.yaml` is the API contract and should be defined before implementing backend or frontend behavior.

The backend should be database-agnostic. Data access should be isolated behind repository interfaces so storage can evolve in this order:

1. Mock database
2. SQLite
3. PostgreSQL

The application should avoid coupling business logic directly to a specific database.

### Backend

Backend stack:

- Python
- uv
- FastAPI

Backend should include:

- Authentication endpoints
- Task endpoints
- Board/dashboard summary endpoints
- Repository abstraction
- Mock repository implementation for first development phase
- Clear path to SQLite and PostgreSQL implementations later
- Tests for core business behavior

### Frontend

Frontend stack:

- Node.js
- React

Frontend should include:

- Login screen
- Dark-mode-first UI
- Kanban board view
- Task create/edit UI
- Drag-and-drop card movement
- Column counts
- Due today and overdue summary
- Visual states for priority, due today, and overdue

### API Contract

The API should support at minimum:

- Login
- Get current user/session
- Get board data
- Create task
- Update task
- Delete task
- Move task between columns
- Archive task
- Get dashboard summary

## Milestones

### Backend Milestone

Implement the FastAPI backend using the API contract.

Backend completion means:

- Username/password login works
- Authenticated task access works
- One board per user is enforced
- Tasks can be created, read, updated, deleted, moved, and archived
- Recurring task completion creates the next task copy
- Done tasks can be auto-archived after 7 days
- Repository abstraction exists
- Mock database implementation works
- Core backend tests pass

### Frontend Milestone

Implement the React frontend against the API contract.

Frontend completion means:

- User can log in
- User can see the board
- User can create, edit, delete, and archive tasks
- User can drag tasks between columns
- Counts update correctly
- Due today and overdue tasks are visually distinct
- UI is dark-mode-first and polished

### Integration Milestone

Connect frontend and backend using `openapi.yaml` as the source of truth.

Integration completion means:

- Frontend works against the real backend
- Authenticated user flow works end to end
- Board state persists through the backend
- Recurring tasks behave correctly
- Archived tasks disappear from the active board
- MVP can be demonstrated cleanly

## User Stories

### Authentication

As a user, I want to log in with username and password so that my personal board is private.

Acceptance criteria:

- User can log in with valid credentials
- User cannot access board data without authentication
- Invalid credentials show an error

### View Board

As a user, I want to see my tasks organized into To Do, Doing, Paused, and Done so that I understand my current workload.

Acceptance criteria:

- Board shows all four fixed columns
- Each task appears in exactly one column
- Each column shows its task count

### Create Task

As a user, I want to create a task with useful details so that I can track what needs to be done.

Acceptance criteria:

- User can enter title, notes, due date, priority, category, and recurrence
- Title is required
- New task appears in To Do by default

### Move Task

As a user, I want to drag a task between columns so that I can update its status naturally.

Acceptance criteria:

- User can drag cards between columns
- Moved task keeps all existing details
- Board updates after move

### Due Date Awareness

As a user, I want overdue and due-today tasks to stand out so that I know what needs attention.

Acceptance criteria:

- Due today tasks have a distinct visual state
- Overdue tasks have a distinct visual state
- Dashboard summary shows due today and overdue counts

### Recurring Task

As a user, I want daily or weekly tasks to recreate themselves when completed so that repeated work is easy to manage.

Acceptance criteria:

- Completing a recurring task keeps the completed task in Done
- A new task copy is created in To Do
- The new task has the next due date
- Non-recurring tasks do not create copies

### Archive Done Tasks

As a user, I want old Done tasks archived so that my board stays clean while preserving completion history.

Acceptance criteria:

- User can manually archive Done tasks
- Done tasks older than 7 days are automatically archived
- Archived tasks do not appear on the active board

## Product Rules

- One user has one board
- One task belongs to one user
- One task belongs to one column
- Columns are fixed
- Categories are fixed
- Priorities are fixed
- Recurrence is limited to none, daily, or weekly
- Done tasks remain visible until manually archived or auto-archived after 7 days
- Search and filters are intentionally excluded from MVP

## Definition Of Done

The MVP is done when a user can:

- Log in
- Manage one personal board
- Create and edit categorized tasks
- Move tasks by drag and drop
- See column counts
- See due today and overdue summaries
- Complete recurring tasks and get the next occurrence
- Archive completed tasks
- Use the app through a polished dark-mode React interface backed by a FastAPI API
