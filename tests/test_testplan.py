from src.generators.testplan import generate_test_plan
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


def test_generate_test_plan_fastapi():
    client = CopilotClient()
    result = generate_test_plan(FASTAPI_INTENT, PATTERNS, client)

    print("\nFirst 40 lines of TESTPLAN.md:")
    for line in result.splitlines()[:40]:
        print(line)

    assert isinstance(result, str) and len(result) > 0
    assert "Test Cases" in result or "Test Case" in result
    assert "Unit" in result
    assert "Integration" in result
