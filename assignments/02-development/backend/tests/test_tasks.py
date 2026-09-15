from datetime import date, timedelta


def test_create_task_defaults_to_todo(client, auth_headers):
    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Write backend tests",
            "notes": "Cover the main workflow.",
            "due_date": str(date.today()),
            "priority": "High",
            "category": "Project",
            "recurrence": "None",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write backend tests"
    assert body["column"] == "todo"


def test_create_task_rejects_fifth_high_priority_task_on_same_day(client, auth_headers):
    target_date = date.today() + timedelta(days=1)
    for index in range(4):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "title": f"High priority task {index}",
                "due_date": str(target_date),
                "priority": "High",
            },
        )
        assert response.status_code == 201

    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "One high priority too many",
            "due_date": str(target_date),
            "priority": "High",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You already have 4 high-priority tasks for this day."


def test_create_task_allows_high_priority_tasks_on_different_days(client, auth_headers):
    target_date = date.today() + timedelta(days=1)
    for index in range(4):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "title": f"High priority task {index}",
                "due_date": str(target_date),
                "priority": "High",
            },
        )
        assert response.status_code == 201

    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Different day high priority",
            "due_date": str(target_date + timedelta(days=1)),
            "priority": "High",
        },
    )

    assert response.status_code == 201


def test_update_task_rejects_fifth_high_priority_task_on_same_day(client, auth_headers):
    target_date = date.today() + timedelta(days=1)
    for index in range(4):
        response = client.post(
            "/tasks",
            headers=auth_headers,
            json={
                "title": f"High priority task {index}",
                "due_date": str(target_date),
                "priority": "High",
            },
        )
        assert response.status_code == 201

    response = client.patch(
        "/tasks/task-3",
        headers=auth_headers,
        json={"due_date": str(target_date), "priority": "High"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You already have 4 high-priority tasks for this day."


def test_update_task_allows_existing_high_priority_task_to_keep_its_day(client, auth_headers):
    response = client.patch(
        "/tasks/task-1",
        headers=auth_headers,
        json={"title": "Keep high priority credit"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Keep high priority credit"


def test_update_task_edits_fields(client, auth_headers):
    response = client.patch(
        "/tasks/task-1",
        headers=auth_headers,
        json={"title": "Review final OpenAPI contract", "priority": "Medium"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Review final OpenAPI contract"
    assert body["priority"] == "Medium"


def test_delete_task_removes_it_from_board(client, auth_headers):
    response = client.delete("/tasks/task-1", headers=auth_headers)
    assert response.status_code == 200

    board = client.get("/board", headers=auth_headers).json()
    assert "task-1" not in {task["id"] for task in board["tasks"]}


def test_move_recurring_task_to_done_creates_next_copy(client, auth_headers):
    response = client.post(
        "/tasks/task-2/move",
        headers=auth_headers,
        json={"column": "done"},
    )

    assert response.status_code == 200
    moved = response.json()
    assert moved["column"] == "done"
    assert moved["completed_at"] == str(date.today())

    board = client.get("/board", headers=auth_headers).json()
    tasks = board["tasks"]
    daily_study_tasks = [task for task in tasks if task["title"] == "Daily study block"]
    assert len(daily_study_tasks) == 2
    next_task = next(task for task in daily_study_tasks if task["column"] == "todo")
    assert next_task["due_date"] == str(date.today())


def test_move_non_recurring_task_to_done_does_not_create_copy(client, auth_headers):
    response = client.post(
        "/tasks/task-1/move",
        headers=auth_headers,
        json={"column": "done"},
    )

    assert response.status_code == 200
    board = client.get("/board", headers=auth_headers).json()
    matching = [task for task in board["tasks"] if task["title"] == "Review FastAPI contract"]
    assert len(matching) == 1


def test_archive_task_hides_it_from_board(client, auth_headers):
    response = client.post("/tasks/task-4/archive", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["archived"] is True

    board = client.get("/board", headers=auth_headers).json()
    assert "task-4" not in {task["id"] for task in board["tasks"]}


def test_missing_task_returns_404(client, auth_headers):
    response = client.patch(
        "/tasks/missing",
        headers=auth_headers,
        json={"title": "Nope"},
    )

    assert response.status_code == 404
