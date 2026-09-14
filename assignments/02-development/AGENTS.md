# Project Agent Instructions

## Backend

- Use `uv` for Python dependency management.
- Useful commands:
  - `uv sync`
  - `uv add <PACKAGE-NAME>`
  - `uv run python <PYTHON-FILE>`
  - `uv run pytest`
  - `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`

## Git Discipline

- Commit regularly. Do not wait until the end of a long task.
- Make a commit after each meaningful milestone, such as:
  - adding or changing a project spec or API contract
  - creating a frontend prototype
  - creating a backend scaffold
  - making tests pass
  - connecting frontend to backend
  - fixing a bug after verification
- Before every commit, run `git status --short` and inspect the staged diff.
- Stage only files related to the current task. Never include unrelated user changes in a commit.
- If unrelated changes exist, leave them unstaged and mention them in the final response.
- Use concise commit messages that describe the completed milestone.
- After committing, report the commit SHA in the response.
- If a commit cannot be made, explain exactly why and what is still uncommitted.

## Verification

- Run the relevant test or build command before committing whenever practical.
- For backend changes, prefer `uv run pytest`.
- For frontend changes, prefer `npm.cmd run build`.
- If verification cannot run because of environment or permission issues, explain the blocker and still keep the git state clear.
