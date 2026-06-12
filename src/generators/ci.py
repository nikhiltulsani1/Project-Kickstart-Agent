import re
from src.language_config import detect_language_config


def generate_ci_workflow(intent: dict, copilot_client=None) -> str:
    """Generate language-appropriate GitHub Actions CI workflow."""

    config = detect_language_config(intent)

    # build the YAML straight from config — no LLM round-trip needed here
    yaml_template = f"""name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up {config['language'].title()}
        uses: {config['ci_setup_action']}
        with:
          {config['ci_version_key']}: '{config['ci_version_val']}'

      - name: Install dependencies
        run: {config['install_command']}

      - name: Run tests
        run: {config['test_command']}
"""
    return yaml_template.strip()
