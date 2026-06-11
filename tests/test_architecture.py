from src.generators.architecture import generate_architecture_doc
from src.copilot import CopilotClient


FASTAPI_INTENT = {
    "project_name": "task-manager",
    "project_type": "web api",
    "stack": ["FastAPI", "PostgreSQL", "JWT"],
    "description": "A FastAPI task manager with Postgres and JWT auth",
    "language": "Python",
}

PATTERNS = [
    "Use layered architecture: separate concerns into routes, services, models",
    "Write tests first: include pytest setup in initial scaffold",
    "Use environment variables for all secrets and config",
]


def test_generate_architecture_doc_fastapi():
    client = CopilotClient()
    result = generate_architecture_doc(FASTAPI_INTENT, PATTERNS, client)

    print("\nFirst 30 lines of ARCHITECTURE.md:")
    for line in result.splitlines()[:30]:
        print(line)

    assert isinstance(result, str) and len(result) > 0
    assert "## Overview" in result or "# Overview" in result
    assert "Data Flow" in result
