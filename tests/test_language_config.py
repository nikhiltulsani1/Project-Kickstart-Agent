import pytest
from src.language_config import detect_language_config


def test_python():
    intent = {"language": "Python", "stack": ["FastAPI", "PostgreSQL"]}
    config = detect_language_config(intent)
    print(f"\nPython config: {config}")
    assert config["language"] == "python"


def test_node():
    intent = {"language": "JavaScript", "stack": ["React", "Node.js"]}
    config = detect_language_config(intent)
    print(f"\nNode config: {config}")
    assert config["language"] == "nodejs"


def test_go():
    intent = {"language": "Go", "stack": ["Go", "Postgres"]}
    config = detect_language_config(intent)
    print(f"\nGo config: {config}")
    assert config["language"] == "go"


def test_java():
    intent = {"language": "Java", "stack": ["Spring Boot", "MySQL"]}
    config = detect_language_config(intent)
    print(f"\nJava config: {config}")
    assert config["language"] == "java"


def test_ruby():
    intent = {"language": "Ruby", "stack": ["Rails", "PostgreSQL"]}
    config = detect_language_config(intent)
    print(f"\nRuby config: {config}")
    assert config["language"] == "ruby"


def test_fallback():
    intent = {"language": "Rust", "stack": ["Actix", "Diesel"]}
    config = detect_language_config(intent)
    print(f"\nFallback config: {config}")
    assert config["language"] == "python"
