# AI-Native Development Workflow Checklist

## Executive Checklist

**Legend:** 👤 Human · 💬 ChatGPT · 🤖 Coding Agent · 📋 PM Agent · 💻 Engineer Agent · 🧪 QA Agent

- [ ] **1. 👤 + 💬 ChatGPT — Define the project scope and create `plan.md`**
- [ ] **2. 👤 Human — Create the GitHub repository, clone it locally, add `_docs/plan.md`, then commit and push**
- [ ] **3. 🤖 Coding Agent — Review `plan.md`, propose technology/architecture options → 👤 Human selects one**
- [ ] **4. 🤖 Coding Agent — Create the initial backlog in `_docs/tasks.md`**
- [ ] **5. 👤 + 🤖 Human + Coding Agent — Review, split, merge, reorder, or remove tasks as needed**
- [ ] **6. 🤖 Coding Agent — Convert `_docs/tasks.md` into GitHub Issues in the existing repository**
- [ ] **7. 👤 Human — Create `AGENTS.md`**
- [ ] **8. 👤 Human — Create `CLAUDE.md` with `@AGENTS.md` if using Claude Code**
- [ ] **9. 👤 Human — Create `_docs/process.md`**
- [ ] **10. 👤 + 🤖 Human + Coding Agent — Add optional project documentation when required**
- [ ] **11. 🤖 Coding Agent — Start a fresh session and implement Task 1**
- [ ] **12. 👤 Human — Create `_docs/team/pm.md`**
- [ ] **13. 👤 Human — Create `_docs/task-template.md`**
- [ ] **14. 👤 Human — Add the PM role to `_docs/process.md`**
- [ ] **15. 📋 PM Agent — Groom issue(s) → 👤 Human reviews the result**
- [ ] **16. 👤 Human — Create `_docs/team/software-engineer.md`**
- [ ] **17. 👤 Human — Add the Engineer role to `_docs/process.md`**
- [ ] **18. 💻 Engineer Agent — Implement a groomed issue**
- [ ] **19. 👤 Human — Create `_docs/team/qa-engineer.md`**
- [ ] **20. 👤 Human — Add the QA role to `_docs/process.md`**
- [ ] **21. 🧪 QA Agent — Validate the issue → `PASS` or `FAIL`**
- [ ] **22. 💻 Engineer → 🧪 QA — If `FAIL`, fix and retest until `PASS`**
- [ ] **23. 👤 Human — Optional: add Orchestrator instructions to `_docs/process.md`**
- [ ] **24. 🤖 Orchestrator — Optional: run `/goal work through the backlog`**

---

# 1. Define the Project Scope

**Actor:** 👤 Human + 💬 ChatGPT

Use ChatGPT or another conversational assistant to clarify the project before coding.

Prompt:

```text
I want to build [PROJECT].

Help me define the scope of this project precisely.
I want to brainstorm how the product should work and understand the main options.

Ask me one question at a time.
Keep your responses concise.
Do not write code yet.
```

Once the discussion is complete:

```text
Turn everything we decided into a concise Markdown project plan that I can download.
```

Save the file as:

```text
plan.md
```

---

# 2. Create the GitHub Repository

**Actor:** 👤 Human

Create a new repository on GitHub.

Clone it locally:

```bash
git clone <YOUR-GITHUB-REPO-URL>
cd <PROJECT-NAME>
```

Create the documentation directory:

```bash
mkdir -p _docs
```

Move the project plan into it:

```bash
mv ~/Downloads/plan.md _docs/plan.md
```

Commit and push:

```bash
git add _docs/plan.md
git commit -m "Add project plan"
git push
```

Repository structure:

```text
project/
└── _docs/
    └── plan.md
```

---

# 3. Select the Technology Stack

**Actor:** 🤖 Coding Agent → 👤 Human selects

Open the repository with your coding agent.

Prompt:

```text
Read _docs/plan.md.

Propose multiple reasonable technology stack and architecture options for this project.

Explain the trade-offs of each option.

Do not write code yet.
```

The agent proposes options.

**You choose the preferred stack.**

---

# 4. Create the Initial Backlog

**Actor:** 🤖 Coding Agent

Prompt:

```text
Create a backlog in _docs/tasks.md.

Each task should:

- be small enough to complete in one focused session
- have one clear outcome
- be understandable independently of the other tasks

Use this format:

## <number>. <title>

Goal: <one sentence>

Description: <two or three sentences describing the work>

The first task should set up an empty working project with at least one passing test.

Do not implement anything yet.
```

The agent creates:

```text
_docs/tasks.md
```

---

# 5. Review and Refine the Backlog

**Actor:** 👤 Human + 🤖 Coding Agent

Read `_docs/tasks.md`.

Review for:

```text
Too small   → merge
Too large   → split
Outside MVP → remove
Wrong order → reorder
```

Then ask the agent to revise it.

Example:

```text
Review _docs/tasks.md.

Merge tasks that are too small.
Split tasks that are too large for one session.
Remove work that is outside the MVP.
Reorder tasks if dependencies require it.
```

Repeat until the backlog is satisfactory.

---

# 6. Convert the Backlog to GitHub Issues

**Actor:** 🤖 Coding Agent

The GitHub repository already exists.

Prompt:

```text
Move each task from _docs/tasks.md into a GitHub issue in this repository.

Preserve each task's title, goal, and description.
```

After this:

```text
_docs/tasks.md
      ↓
GitHub Issues
```

From this point forward:

```text
GitHub Issues = active backlog
```

---

# 7. Create `AGENTS.md`

**Actor:** 👤 Human

Create:

```text
AGENTS.md
```

Example:

```markdown
# Commands

- `uv sync` - install dependencies
- `uv run pytest` - run the full test suite
- `uv run pytest tests/test_home.py` - run one test file

# Rules

- Dependencies are managed in `pyproject.toml`.
- Do not add a new dependency without approval.
```

Replace the examples with your project's actual commands and rules.

---

# 8. Create `CLAUDE.md`

**Actor:** 👤 Human

Only needed when using Claude Code.

Create:

```text
CLAUDE.md
```

Content:

```markdown
@AGENTS.md
```

---

# 9. Create `_docs/process.md`

**Actor:** 👤 Human

Create:

```text
_docs/process.md
```

Initial content:

```markdown
- Tasks are managed as GitHub Issues.
- Work on one issue at a time.
- Read the acceptance criteria before starting and before completing a task.
- Commit regularly.
```

Additional roles will be added later.

---

# 10. Add Optional Documentation as Needed

**Actor:** 👤 Human + 🤖 Coding Agent

Only create these when the project requires them:

```text
_docs/
├── testing-guidelines.md
├── design-system.md
└── api.md
```

Reference relevant documents from `AGENTS.md`.

Example:

```markdown
# Documents

- `_docs/process.md` - development workflow
- Before modifying tests, read `_docs/testing-guidelines.md`
- Before UI work, read `_docs/design-system.md`
- Before API changes, read `_docs/api.md`
```

When a correction becomes a reusable project rule:

```text
Review the corrections I made during this session.

Update the appropriate project documentation so future coding-agent sessions follow these rules automatically.

Commit the current implementation before changing documentation.
```

---

# 11. Implement Task 1

**Actor:** 🤖 Coding Agent

Start a **fresh coding-agent session**.

Prompt:

```text
Implement task 1.
```

Task 1 should establish:

```text
project skeleton
      +
dependencies
      +
at least one passing test
```

---

# 12. Create the PM Role

**Actor:** 👤 Human

Create:

```text
_docs/team/pm.md
```

Content:

```markdown
# Product Manager

You groom a task before implementation begins.

Responsibilities:

- Read the issue as written.
- Rewrite it using `_docs/task-template.md`.
- Make every acceptance criterion objectively checkable.
- Identify relevant edge cases.
- Do not write implementation code.

Definition of done:

- All four task sections are complete.
- Every acceptance criterion can be evaluated as PASS or FAIL.
- Anything moved out of scope links to a follow-up issue.
- An engineer unfamiliar with previous conversations can implement the task from the issue and linked documentation.

If something does not belong in the current task, do not silently remove it.
Create a follow-up issue and reference it under Out of Scope.
```

---

# 13. Create the Task Template

**Actor:** 👤 Human

Create:

```text
_docs/task-template.md
```

Content:

```markdown
## Goal

One or two sentences describing what should be true when the task is complete.

## Acceptance Criteria

- [ ] A clearly observable requirement
- [ ] One line per case, including important edge cases

## Out of Scope

- Work intentionally excluded from this task, moved to #TASK-NUMBER

## Constraints

- Relevant files or modules
- Required libraries
- Project guidelines to follow
```

---

# 14. Add the PM Role to `process.md`

**Actor:** 👤 Human

Add:

```markdown
# Roles

- PM - grooms tasks before implementation and follows `_docs/team/pm.md`
```

---

# 15. Groom Issues

**Actor:** 📋 PM Agent → 👤 Human reviews

Start a fresh coding-agent session.

Prompt:

```text
Groom issue #4.
```

Workflow:

```text
PM Agent
   ↓
Groomed issue
   ↓
Human review
   ↓
Corrections if needed
```

For the full backlog:

```text
Groom all GitHub issues.
Process one issue at a time.
```

If supported:

```text
/goal groom all issues
```

---

# 16. Create the Software Engineer Role

**Actor:** 👤 Human

Create:

```text
_docs/team/software-engineer.md
```

Content:

```markdown
# Software Engineer

You implement one groomed task at a time.

Responsibilities:

- Read the issue completely.
- Implement exactly what the acceptance criteria require.
- Do not modify the acceptance criteria.
- Respect the files and constraints defined by the issue.
- Write tests for the new behavior.
- Run the relevant test suite.
- Commit regularly.
- Do not close the issue.

Definition of done:

- Every acceptance criterion is implemented.
- Tests exist for the new behavior.
- The full relevant test suite passes.
- The work is committed.
- The issue remains open.
- Add a comment summarizing the implementation.

If an acceptance criterion is contradictory, impossible, or incorrect, comment on the issue instead of changing it.
```

---

# 17. Add the Engineer Role to `process.md`

**Actor:** 👤 Human

Update:

```markdown
# Roles

- PM - grooms tasks before implementation and follows `_docs/team/pm.md`
- Engineer - implements groomed tasks and follows `_docs/team/software-engineer.md`
```

---

# 18. Implement a Groomed Issue

**Actor:** 💻 Engineer Agent

Start a fresh coding-agent session.

Prompt:

```text
Implement issue #2.
```

Expected flow:

```text
Read issue
   ↓
Implement
   ↓
Write tests
   ↓
Run tests
   ↓
Commit
   ↓
Leave issue open
```

---

# 19. Create the QA Role

**Actor:** 👤 Human

Create:

```text
_docs/team/qa-engineer.md
```

Content:

```markdown
# QA Engineer

You validate completed work against the issue that specified it.

Responsibilities:

- Read the acceptance criteria.
- Check each criterion against the running implementation.
- Run the relevant tests and report the commands used.
- Identify acceptance criteria not covered by automated tests.
- Do not fix any problems you find.
- Report findings as an issue comment.

Your verdict must be:

PASS

or

FAIL

The task fails if any acceptance criterion fails.

For each criterion, report PASS or FAIL.

For every failure include:

- what you tested
- expected behavior
- actual behavior

Also include:

Tests: `<command>` — `<result>`

Do not modify production code during QA.

Evaluate the implementation based only on the acceptance criteria and actual behavior.
```

---

# 20. Add the QA Role to `process.md`

**Actor:** 👤 Human

Update:

```markdown
# Roles

- PM - grooms tasks before implementation and follows `_docs/team/pm.md`
- Engineer - implements groomed tasks and follows `_docs/team/software-engineer.md`
- QA - verifies completed work and follows `_docs/team/qa-engineer.md`
```

---

# 21. Validate the Issue

**Actor:** 🧪 QA Agent

Start a fresh coding-agent session.

Prompt:

```text
Test issue #2.
```

Expected verdict:

```text
PASS
```

or:

```text
FAIL
```

---

# 22. Handle QA Failures

**Actor:** 💻 Engineer Agent → 🧪 QA Agent

If QA returns:

```text
FAIL
```

Start a new Engineer session to fix the reported problems.

Then start a new QA session:

```text
Test issue #2.
```

Repeat:

```text
Engineer
   ↓
QA
   ↓
FAIL ─────→ Engineer
   ↓
PASS
```

Once QA returns `PASS`, the issue can be closed.

---

# 23. Optional: Add an Orchestrator

**Actor:** 👤 Human

Add to `_docs/process.md`:

```markdown
# Orchestrator

The main session acts as the orchestrator.

It coordinates the PM, Engineer, and QA agents, but does not perform their specialized work itself.

## Lifecycle

1. Select the next open issue.
2. PM grooms the issue.
3. Engineer implements it.
4. QA validates it.
5. If QA returns FAIL, return the issue to the Engineer with the QA findings.
6. If QA returns PASS, close the issue.
7. Continue until no implementation issues remain.

## Rules

- Do not skip grooming.
- The Engineer does not close issues.
- QA does not modify production code.
- The Orchestrator closes an issue only after QA returns PASS.
```

---

# 24. Optional: Run the Full Backlog

**Actor:** 🤖 Orchestrator

Start a fresh session:

```text
/goal work through the backlog
```

Workflow:

```text
Issue
  ↓
PM
  ↓
Engineer
  ↓
QA
 ├── FAIL → Engineer → QA
 └── PASS → Close → Next Issue
```

---

# Day-to-Day Workflow

Once the project setup is complete, normal work becomes:

```text
📋 New session
"Groom issue #X"

        ↓

👤 Review

        ↓

💻 New session
"Implement issue #X"

        ↓

🧪 New session
"Test issue #X"

        ↓

FAIL → Engineer fixes → QA retests

PASS → Close issue
```

For an automated workflow:

```text
/goal work through the backlog
```