import pytest
from src.generators.ci import generate_ci_workflow


def test_python_ci():
    intent = {"language": "Python", "stack": ["FastAPI", "PostgreSQL", "JWT"]}
    result = generate_ci_workflow(intent)
    print(f"\nPython CI:\n{result}")
    assert "setup-python" in result
    assert "pip install" in result
    assert "pytest" in result


def test_node_ci():
    intent = {"language": "JavaScript", "stack": ["React", "Node.js"]}
    result = generate_ci_workflow(intent)
    print(f"\nNode CI:\n{result}")
    assert "setup-node" in result
    assert "npm install" in result
    assert "npm test" in result


def test_go_ci():
    intent = {"language": "Go", "stack": ["Go", "PostgreSQL"]}
    result = generate_ci_workflow(intent)
    print(f"\nGo CI:\n{result}")
    assert "setup-go" in result
    assert "go mod download" in result
    assert "go test" in result


def test_java_ci():
    intent = {"language": "Java", "stack": ["Spring Boot", "MySQL"]}
    result = generate_ci_workflow(intent)
    print(f"\nJava CI:\n{result}")
    assert "setup-java" in result
    assert "mvn install" in result


def test_ruby_ci():
    intent = {"language": "Ruby", "stack": ["Rails", "PostgreSQL"]}
    result = generate_ci_workflow(intent)
    print(f"\nRuby CI:\n{result}")
    assert "setup-ruby" in result
    assert "bundle install" in result
