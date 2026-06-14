from src.language_config import get_placeholder_test


def test_python_placeholder():
    intent = {"language": "Python", "stack": ["FastAPI", "PostgreSQL"]}
    path, content = get_placeholder_test(intent, "my-api")
    print(f"\nPython → {path}\n{content}")
    assert "test_scaffold.py" in path
    assert "assert" in content


def test_node_placeholder():
    intent = {"language": "JavaScript", "stack": ["React", "Node.js"]}
    path, content = get_placeholder_test(intent, "my-dashboard")
    print(f"\nNode → {path}\n{content}")
    assert ".test.js" in path
    assert "describe" in content


def test_go_placeholder():
    intent = {"language": "Go", "stack": ["Go", "PostgreSQL"]}
    path, content = get_placeholder_test(intent, "my-service")
    print(f"\nGo → {path}\n{content}")
    assert "_test.go" in path
    assert "testing" in content


def test_java_placeholder():
    intent = {"language": "Java", "stack": ["Spring Boot", "MySQL"]}
    path, content = get_placeholder_test(intent, "my-app")
    print(f"\nJava → {path}\n{content}")
    assert "Test.java" in path
    assert "assertTrue" in content


def test_ruby_placeholder():
    intent = {"language": "Ruby", "stack": ["Rails", "PostgreSQL"]}
    path, content = get_placeholder_test(intent, "my-blog")
    print(f"\nRuby → {path}\n{content}")
    assert "_spec.rb" in path
    assert "RSpec" in content
