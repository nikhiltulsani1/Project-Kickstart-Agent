_CONFIGS = {
    "python": {
        "language": "python",
        "package_manager": "pip",
        "dependency_file": "requirements.txt",
        "test_framework": "pytest",
        "test_command": "pytest",
        "install_command": "pip install -r requirements.txt && pip install pytest",
        "ci_setup_action": "actions/setup-python@v4",
        "ci_version_key": "python-version",
        "ci_version_val": "3.11",
        "src_folder": "src",
        "placeholder_test": "pytest",
    },
    "nodejs": {
        "language": "nodejs",
        "package_manager": "npm",
        "dependency_file": "package.json",
        "test_framework": "jest",
        "test_command": "npm test",
        "install_command": "npm install",
        "ci_setup_action": "actions/setup-node@v4",
        "ci_version_key": "node-version",
        "ci_version_val": "20",
        "src_folder": "src",
        "placeholder_test": "jest",
    },
    "go": {
        "language": "go",
        "package_manager": "go mod",
        "dependency_file": "go.mod",
        "test_framework": "go test",
        "test_command": "go test ./...",
        "install_command": "go mod download",
        "ci_setup_action": "actions/setup-go@v5",
        "ci_version_key": "go-version",
        "ci_version_val": "1.22",
        "src_folder": "cmd",
        "placeholder_test": "go",
    },
    "java": {
        "language": "java",
        "package_manager": "maven",
        "dependency_file": "pom.xml",
        "test_framework": "junit",
        "test_command": "mvn test",
        "install_command": "mvn install -DskipTests",
        "ci_setup_action": "actions/setup-java@v4",
        "ci_version_key": "java-version",
        "ci_version_val": "21",
        "src_folder": "src/main/java",
        "placeholder_test": "java",
    },
    "ruby": {
        "language": "ruby",
        "package_manager": "bundler",
        "dependency_file": "Gemfile",
        "test_framework": "rspec",
        "test_command": "bundle exec rspec",
        "install_command": "bundle install",
        "ci_setup_action": "ruby/setup-ruby@v1",
        "ci_version_key": "ruby-version",
        "ci_version_val": "3.3",
        "src_folder": "app",
        "placeholder_test": "ruby",
    },
}

_KEYWORDS = {
    "python": {"python", "django", "flask", "fastapi", "celery"},
    "nodejs": {"node", "nodejs", "javascript", "typescript", "react", "vue", "express", "nextjs", "next.js"},
    "go":     {"go", "golang", "gin", "fiber", "echo"},
    "java":   {"java", "spring", "springboot", "maven", "gradle"},
    "ruby":   {"ruby", "rails", "sinatra"},
}


def detect_language_config(intent: dict) -> dict:
    # normalise everything to lowercase so matching isn't fragile
    lang = intent.get("language", "").lower().strip()
    stack = [s.lower().strip() for s in intent.get("stack", [])]

    candidates = [lang] + stack

    for token in candidates:
        for config_key, keywords in _KEYWORDS.items():
            if token in keywords:
                return dict(_CONFIGS[config_key])

    # nothing matched — fall back to Python so callers always get a usable config
    return dict(_CONFIGS["python"])
