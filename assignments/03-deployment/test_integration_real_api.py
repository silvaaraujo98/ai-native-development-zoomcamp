"""End-to-end acceptance test against the running HTTP API and SQLite DB."""

from __future__ import annotations

import os
import uuid

import httpx


BASE_URL = os.getenv("RELAY_BASE_URL", "http://127.0.0.1:8000")


def test_acceptance_scenario_one_against_real_api_and_db() -> None:
    """Register, send, claim, complete, and read a task through real HTTP."""

    suffix = uuid.uuid4().hex[:8]
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        sender_response = client.post("/api/v1/agents", json={"name": f"integration-sender-{suffix}"})
        assert sender_response.status_code == 201, sender_response.text
        sender = sender_response.json()
        sender_headers = {"Authorization": f"Bearer {sender['token']}"}

        recipient_response = client.post("/api/v1/agents", json={"name": f"integration-worker-{suffix}"})
        assert recipient_response.status_code == 201, recipient_response.text
        recipient = recipient_response.json()
        recipient_headers = {"Authorization": f"Bearer {recipient['token']}"}

        task_response = client.post(
            "/api/v1/tasks",
            headers=sender_headers,
            json={"to": recipient["agent_id"], "input": "integration scenario one"},
        )
        assert task_response.status_code == 201, task_response.text
        task = task_response.json()

        claim_response = client.post(
            "/api/v1/tasks/claim",
            headers=recipient_headers,
            json={"worker_id": f"integration-worker-{suffix}", "wait_seconds": 0},
        )
        assert claim_response.status_code == 200, claim_response.text
        claim = claim_response.json()
        assert claim["task_id"] == task["task_id"]
        assert claim["attempt"] == 1

        complete_response = client.post(
            f"/api/v1/tasks/{task['task_id']}/complete",
            headers=recipient_headers,
            json={"claim_token": claim["claim_token"], "output": "INTEGRATION SCENARIO ONE"},
        )
        assert complete_response.status_code == 200, complete_response.text
        assert complete_response.json() == {"task_id": task["task_id"], "status": "completed"}

        result_response = client.get(f"/api/v1/tasks/{task['task_id']}", headers=sender_headers)
        assert result_response.status_code == 200, result_response.text
        result = result_response.json()
        assert result["status"] == "completed"
        assert result["output"] == "INTEGRATION SCENARIO ONE"
