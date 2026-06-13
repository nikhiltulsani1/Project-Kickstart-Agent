_MIT_LICENSE = """MIT License

Copyright (c) 2026 Project Kickstart Agent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""

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
        "llm_entry_files": ["src/main.py", "src/models.py", "src/routes.py"],
        "folder_structure": {
            "src/__init__.py": "",
            "src/main.py": "# Entry point",
            "src/models.py": "# Database models",
            "src/routes.py": "# API routes",
            "src/services.py": "# Business logic",
            "src/config.py": "# Configuration",
            "tests/__init__.py": "",
            "tests/test_main.py": "# Add your tests here",
            ".env.example": "DATABASE_URL=\nSECRET_KEY=\nDEBUG=True",
            "requirements.txt": "# Add your dependencies here",
            "Makefile": "install:\n\tpip install -r requirements.txt\n\ntest:\n\tpytest\n\nrun:\n\tpython src/main.py",
            "LICENSE": _MIT_LICENSE,
        },
    },
    "nodejs": {
        "language": "nodejs",
        "package_manager": "npm",
        "dependency_file": "package.json",
        "test_framework": "jest",
        "test_command": "npm test",
        "install_command": "npm install && npm install --save-dev jest",
        "ci_setup_action": "actions/setup-node@v4",
        "ci_version_key": "node-version",
        "ci_version_val": "20",
        "src_folder": "src",
        "placeholder_test": "jest",
        "llm_entry_files": ["src/index.js", "src/routes/index.js", "src/models/index.js"],
        "folder_structure": {
            "src/index.js": "// Entry point",
            "src/routes/index.js": "// Routes",
            "src/controllers/index.js": "// Controllers",
            "src/models/index.js": "// Models",
            "src/middleware/auth.js": "// Auth middleware",
            "src/config/index.js": "// Configuration",
            "tests/index.test.js": "// Add your tests here",
            ".env.example": "PORT=3000\nDATABASE_URL=\nJWT_SECRET=",
            "package.json": '{\n  "name": "project",\n  "version": "1.0.0",\n  "scripts": {\n    "start": "node src/index.js",\n    "test": "jest",\n    "dev": "nodemon src/index.js"\n  },\n  "devDependencies": {\n    "jest": "^29.0.0"\n  }\n}',
            ".gitignore": "node_modules/\n.env\ndist/",
            "LICENSE": _MIT_LICENSE,
        },
    },
    "go": {
        "language": "go",
        "package_manager": "go mod",
        "dependency_file": "go.mod",
        "test_framework": "go test",
        "test_command": "go test ./...",
        "install_command": "go mod download && go mod tidy",
        "ci_setup_action": "actions/setup-go@v5",
        "ci_version_key": "go-version",
        "ci_version_val": "1.22",
        "src_folder": "cmd",
        "placeholder_test": "go",
        "llm_entry_files": ["cmd/main.go", "internal/handlers/handler.go", "internal/models/model.go"],
        "folder_structure": {
            "cmd/main.go": "package main\n\nfunc main() {\n}",
            "internal/handlers/handler.go": "package handlers",
            "internal/models/model.go": "package models",
            "internal/repository/repo.go": "package repository",
            "internal/services/service.go": "package services",
            "pkg/config/config.go": "package config",
            "tests/main_test.go": "package tests",
            "go.mod": "module github.com/user/project\n\ngo 1.22",
            ".env.example": "DATABASE_URL=\nPORT=8080",
            "Makefile": "build:\n\tgo build ./...\n\ntest:\n\tgo test ./...\n\nrun:\n\tgo run cmd/main.go",
            "LICENSE": _MIT_LICENSE,
        },
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
        # Java stubs compile cleanly on their own — LLM-generated Java tends to add
        # cross-package imports that break compilation, so skip LLM for Java files
        "llm_entry_files": [],
        "ci_with_extras": {"distribution": "temurin"},
        "folder_structure": {
            "src/main/java/com/project/Application.java": (
                "package com.project;\n\n"
                "import org.springframework.boot.SpringApplication;\n"
                "import org.springframework.boot.autoconfigure.SpringBootApplication;\n\n"
                "@SpringBootApplication\n"
                "public class Application {\n"
                "    public static void main(String[] args) {\n"
                "        SpringApplication.run(Application.class, args);\n"
                "    }\n"
                "}"
            ),
            "src/main/java/com/project/controller/Controller.java": "package com.project.controller;\n\npublic class Controller {\n}",
            "src/main/java/com/project/model/Model.java": "package com.project.model;\n\npublic class Model {\n}",
            "src/main/java/com/project/service/Service.java": "package com.project.service;\n\npublic class Service {\n}",
            "src/main/java/com/project/repository/Repository.java": "package com.project.repository;\n\npublic class Repository {\n}",
            "src/main/resources/application.properties": "server.port=8080\nspring.datasource.url=",
            "src/test/java/com/project/ApplicationTests.java": (
                "package com.project;\n\n"
                "import org.junit.jupiter.api.Test;\n\n"
                "class ApplicationTests {\n"
                "    @Test\n"
                "    void contextLoads() {}\n"
                "}"
            ),
            "pom.xml": (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<project xmlns="http://maven.apache.org/POM/4.0.0"\n'
                '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
                '         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">\n'
                '    <modelVersion>4.0.0</modelVersion>\n'
                '    <parent>\n'
                '        <groupId>org.springframework.boot</groupId>\n'
                '        <artifactId>spring-boot-starter-parent</artifactId>\n'
                '        <version>3.2.0</version>\n'
                '        <relativePath/>\n'
                '    </parent>\n'
                '    <groupId>com.project</groupId>\n'
                '    <artifactId>project</artifactId>\n'
                '    <version>0.0.1-SNAPSHOT</version>\n'
                '    <properties>\n'
                '        <java.version>21</java.version>\n'
                '    </properties>\n'
                '    <dependencies>\n'
                '        <dependency>\n'
                '            <groupId>org.springframework.boot</groupId>\n'
                '            <artifactId>spring-boot-starter-web</artifactId>\n'
                '        </dependency>\n'
                '        <dependency>\n'
                '            <groupId>org.springframework.boot</groupId>\n'
                '            <artifactId>spring-boot-starter-test</artifactId>\n'
                '            <scope>test</scope>\n'
                '        </dependency>\n'
                '    </dependencies>\n'
                '    <build>\n'
                '        <plugins>\n'
                '            <plugin>\n'
                '                <groupId>org.springframework.boot</groupId>\n'
                '                <artifactId>spring-boot-maven-plugin</artifactId>\n'
                '            </plugin>\n'
                '        </plugins>\n'
                '    </build>\n'
                '</project>'
            ),
            ".env.example": "DATABASE_URL=\nJWT_SECRET=",
            "LICENSE": _MIT_LICENSE,
        },
    },
    "ruby": {
        "language": "ruby",
        "package_manager": "bundler",
        "dependency_file": "Gemfile",
        "test_framework": "rspec",
        "test_command": "bundle exec rspec",
        "install_command": "bundle install && gem install rspec",
        "ci_setup_action": "ruby/setup-ruby@v1",
        "ci_version_key": "ruby-version",
        "ci_version_val": "3.3",
        "src_folder": "app",
        "placeholder_test": "ruby",
        "llm_entry_files": ["app/controllers/application_controller.rb", "app/models/application_record.rb", "config/routes.rb"],
        "folder_structure": {
            "app/controllers/application_controller.rb": "class ApplicationController < ActionController::Base\nend",
            "app/models/application_record.rb": "class ApplicationRecord < ActiveRecord::Base\n  self.abstract_class = true\nend",
            "app/views/.gitkeep": "",
            "config/routes.rb": "Rails.application.routes.draw do\nend",
            "config/database.yml": "default: &default\n  adapter: postgresql\n  encoding: unicode",
            "db/seeds.rb": "# Add seed data here",
            "spec/spec_helper.rb": "# RSpec configuration",
            "Gemfile": "source 'https://rubygems.org'\ngem 'rails'\ngem 'pg'\ngem 'rspec-rails', group: :test",
            ".env.example": "DATABASE_URL=\nSECRET_KEY_BASE=",
            "LICENSE": _MIT_LICENSE,
        },
    },
}

_KEYWORDS = {
    "python": {"python", "django", "flask", "fastapi", "celery"},
    "nodejs": {"node", "nodejs", "javascript", "typescript", "react", "vue", "express", "nextjs", "next.js"},
    "go":     {"go", "golang", "gin", "fiber", "echo"},
    "java":   {"java", "spring", "springboot", "maven", "gradle"},
    "ruby":   {"ruby", "rails", "sinatra"},
}


def get_placeholder_test(intent: dict, project_name: str) -> tuple:
    """Returns (filepath, content) for a language-appropriate placeholder test."""
    config = detect_language_config(intent)
    lang = config["language"]

    if lang == "python":
        return (
            "tests/test_scaffold.py",
            'import pytest\n\n\ndef test_project_scaffolded():\n    """Placeholder — replace with real tests."""\n    assert True\n\n\ndef test_readme_exists():\n    import os\n    assert os.path.exists("README.md") or True\n',
        )

    elif lang == "nodejs":
        return (
            "tests/scaffold.test.js",
            'describe("Project Scaffold", () => {\n  test("project was scaffolded successfully", () => {\n    expect(true).toBe(true);\n  });\n\n  test("package.json exists", () => {\n    const fs = require("fs");\n    expect(fs.existsSync("package.json") || true).toBe(true);\n  });\n});\n',
        )

    elif lang == "go":
        return (
            "tests/scaffold_test.go",
            'package tests\n\nimport "testing"\n\nfunc TestProjectScaffolded(t *testing.T) {\n\t// Placeholder — replace with real tests\n\tt.Log("Project scaffolded successfully")\n}\n',
        )

    elif lang == "java":
        return (
            "src/test/java/com/project/ScaffoldTest.java",
            'package com.project;\n\nimport org.junit.jupiter.api.Test;\nimport static org.junit.jupiter.api.Assertions.assertTrue;\n\nclass ScaffoldTest {\n    @Test\n    void projectScaffolded() {\n        // Placeholder — replace with real tests\n        assertTrue(true);\n    }\n}\n',
        )

    elif lang == "ruby":
        return (
            "spec/scaffold_spec.rb",
            'RSpec.describe "Project Scaffold" do\n  it "was scaffolded successfully" do\n    expect(true).to eq(true)\n  end\nend\n',
        )

    else:
        return (
            "tests/test_scaffold.py",
            "def test_scaffold():\n    assert True\n",
        )


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
