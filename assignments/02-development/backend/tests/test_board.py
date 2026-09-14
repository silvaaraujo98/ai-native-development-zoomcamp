from datetime import date, timedelta

from app.store import store


def test_board_returns_seeded_columns_and_tasks(client, auth_headers):
    response = client.get("/board", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert [column["id"] for column in body["columns"]] == ["todo", "doing", "paused", "done"]
    assert len(body["tasks"]) == 4


def test_summary_counts_due_today_and_overdue_active_tasks(client, auth_headers):
    response = client.get("/dashboard/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "due_today": 1,
        "overdue": 1,
        "active_tasks": 3,
        "done_visible": 1,
    }


def test_done_tasks_are_auto_archived_after_seven_days(client, auth_headers):
    store.set_task_completed_at("user-1", "task-4", date.today() - timedelta(days=8))

    response = client.get("/board", headers=auth_headers)

    assert response.status_code == 200
    task_ids = {task["id"] for task in response.json()["tasks"]}
    assert "task-4" not in task_ids
    assert store.get_task("user-1", "task-4").archived is True


def test_done_tasks_on_cutoff_are_auto_archived(client, auth_headers):
    store.set_task_completed_at("user-1", "task-4", date.today() - timedelta(days=7))

    response = client.get("/board", headers=auth_headers)

    assert response.status_code == 200
    task_ids = {task["id"] for task in response.json()["tasks"]}
    assert "task-4" not in task_ids
