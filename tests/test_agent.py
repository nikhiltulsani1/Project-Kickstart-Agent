"""Tests for ProjectKickstartAgent."""
import pytest

from src.agent import ProjectKickstartAgent



def test_parse_intent_fastapi(capsys):
    agent = ProjectKickstartAgent()
    result = agent.parse_intent("A FastAPI task manager with Postgres and JWT auth")
    print("Parsed intent:", result)
    assert isinstance(result, dict)
    # Assert all keys present
    expected_keys = {"project_name", "project_type", "stack", "description", "language"}
    assert set(result.keys()) == expected_keys
    # project_name is lowercase with no spaces
    assert result["project_name"] == result["project_name"].lower()
    assert " " not in result["project_name"]
    # FastAPI mentioned in stack (case-insensitive)
    stack_lower = [s.lower() for s in result["stack"]]
    assert "fastapi" in stack_lower or any("fastapi" in s for s in stack_lower)


def test_parse_intent_empty_raises():
    agent = ProjectKickstartAgent()
    with pytest.raises(ValueError):
        agent.parse_intent("")


def test_language_aware_structure():
    from src.language_config import detect_language_config

    # use a hardcoded intent — this tests language detection, not the LLM
    intent = {
        "project_name": "react-dashboard",
        "project_type": "web app",
        "stack": ["React", "Node.js", "MongoDB"],
        "description": "A React dashboard with Node.js API",
        "language": "JavaScript",
    }
    print("\nIntent:", intent)

    config = detect_language_config(intent)
    print("Detected language config:", config["language"])

    assert config["language"] == "nodejs"
    assert "package.json" in config["folder_structure"]
    assert "src/index.js" in config["folder_structure"]
