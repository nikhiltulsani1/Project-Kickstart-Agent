import pytest

from src.generators.ci import generate_ci_workflow
from src.copilot import CopilotClient


FASTAPI_INTENT = {
    "project_name": "task-manager",
    "project_type": "web api",
    "stack": ["FastAPI", "PostgreSQL", "JWT"],
    "description": "A FastAPI task manager with Postgres and JWT auth",
    "language": "Python",
}


def test_generate_ci_workflow_fastapi():
    client = CopilotClient()
    result = generate_ci_workflow(FASTAPI_INTENT, client)

    print("\nFirst 20 lines of generated CI YAML:")
    for line in result.splitlines()[:20]:
        print(line)

    assert isinstance(result, str) and result.strip() != ""
    assert "pytest" in result
    assert "push" in result
