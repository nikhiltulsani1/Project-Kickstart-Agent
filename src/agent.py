from rich.console import Console
import json
import re
import sys
from typing import Dict, List

from src.copilot import CopilotClient
from src.github_client import GitHubClient
from src.generators.ci import generate_ci_workflow


console = Console()


class ProjectKickstartAgent:
    """Ties together all the moving parts and drives the flow end-to-end."""

    def __init__(self):
        self.copilot = CopilotClient()

    def run(self, description: str) -> None:
        # STEP 1: Parse intent
        try:
            intent = self.parse_intent(description)
            stack_items = ", ".join(intent.get("stack", []))
            console.print(f"✓ Parsed: {intent.get('project_name')} ({stack_items})")
        except Exception as e:
            console.print(f"[bold red]✗ Step 1 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 2: Retrieve architecture patterns (hardcoded for now)
        try:
            patterns = [
                "Use layered architecture: separate concerns into routes, services, models",
                "Write tests first: include pytest setup in initial scaffold",
                "Use environment variables for all secrets and config",
                "Add a Makefile for common dev commands",
                "Document the API with docstrings and a README",
            ]
            console.print(f"✓ Retrieved {len(patterns)} architecture patterns")
        except Exception as e:
            console.print(f"[bold red]✗ Step 2 failed: {e}[/bold red]")
            sys.exit(1)

        def _strip_fences(text: str) -> str:
            # remove ```json or ``` blocks
            if text is None:
                return ""
            return re.sub(r"^```.*?\n|\n```$", "", text, flags=re.DOTALL)

        def _safe_load_json(text: str):
            t = text.strip()
            t = _strip_fences(t)
            try:
                return json.loads(t)
            except json.JSONDecodeError:
                # attempt to extract the first JSON object/array
                start_obj = t.find("{")
                end_obj = t.rfind("}")
                start_arr = t.find("[")
                end_arr = t.rfind("]")
                # prefer object if present
                if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
                    snippet = t[start_obj : end_obj + 1]
                    return json.loads(snippet)
                if start_arr != -1 and end_arr != -1 and end_arr > start_arr:
                    snippet = t[start_arr : end_arr + 1]
                    return json.loads(snippet)
                raise

        # STEP 3: Generate README
        try:
            readme_system = (
                "You are an expert technical writer and software architect.\n"
                "Generate a professional README.md for a software project.\n"
                "Include these sections: title, description, tech stack, \n"
                "folder structure, how to run locally, environment variables, \n"
                "contributing, and license.\n"
                "Return markdown only. No explanation. No code fences."
            )
            readme_user = f"Project details: {intent}\nArchitecture patterns to follow: {patterns}"
            readme_md = self.copilot.generate(readme_system, readme_user)
            console.print("✓ Generated README.md")
        except Exception as e:
            console.print(f"[bold red]✗ Step 3 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 4: Generate folder structure
        try:
            fs_system = (
                "You are a software architect. Return ONLY a JSON object where \n"
                "keys are file paths and values are minimal file contents or empty strings.\n"
                "Include: src/__init__.py, src/main.py, src/models.py, src/routes.py,\n"
                "tests/__init__.py, tests/test_main.py, .env.example, Makefile.\n"
                "Tailor contents to the project stack. Return valid JSON only, no markdown."
            )
            fs_user = f"Project: {intent}"
            fs_resp = self.copilot.generate(fs_system, fs_user)
            fs_json = _safe_load_json(fs_resp)
            if not isinstance(fs_json, dict):
                raise ValueError("Folder structure response is not a JSON object")
            console.print(f"✓ Generated folder structure ({len(fs_json)} files)")
        except Exception as e:
            console.print(f"[bold red]✗ Step 4 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 5: Generate CI workflow
        try:
            ci_yaml = generate_ci_workflow(intent, self.copilot)
            console.print("✓ Generated CI workflow")
        except Exception as e:
            console.print(f"[bold red]✗ Step 5 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 6: Create GitHub repo
        try:
            gh = GitHubClient()
            repo = gh.create_repo(intent["project_name"], intent["description"])
            console.print(f"✓ Created repo: {repo.html_url}")
        except Exception as e:
            console.print(f"[bold red]✗ Step 6 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 7: Push all files
        try:
            gh.push_file(repo, "README.md", readme_md, "Add README.md")
            gh.create_folder_structure(repo, fs_json)
            total_files = 1 + len(fs_json)
            console.print(f"✓ Pushed {total_files} files to repo")
        except Exception as e:
            console.print(f"[bold red]✗ Step 7 failed: {e}[/bold red]")
            sys.exit(1)

        # Push CI workflow separately — requires 'workflow' scope on the PAT
        try:
            gh.push_file(repo, ".github/workflows/ci.yml", ci_yaml, "Add CI workflow")
            console.print("✓ Added CI workflow (.github/workflows/ci.yml)")
        except Exception:
            console.print("[yellow]⚠ Skipped CI workflow push — add 'workflow' scope to your PAT to enable this[/yellow]")

        # STEP 8: Create 5 sprint issues
        try:
            issues_system = (
                "You are a senior engineer creating a sprint backlog.\n"
                "Return ONLY a JSON array of exactly 5 objects.\n"
                "Each object has: title (string), body (string with acceptance criteria).\n"
                "Tailor issues to the project stack and type.\n"
                "Return valid JSON array only, no markdown."
            )
            issues_user = f"Project: {intent}"
            issues_resp = self.copilot.generate(issues_system, issues_user)
            issues_json = _safe_load_json(issues_resp)
            if not isinstance(issues_json, list) or len(issues_json) != 5:
                raise ValueError("Issues response must be a JSON array of exactly 5 objects")

            created = 0
            for issue in issues_json:
                title = issue.get("title")
                body = issue.get("body")
                if not title or not body:
                    raise ValueError("Each issue must have title and body")
                gh.create_issue(repo, title, body)
                created += 1

            if created != 5:
                raise RuntimeError("Did not create 5 issues")

            console.print("✓ Created 5 sprint issues")
        except Exception as e:
            console.print(f"[bold red]✗ Step 8 failed: {e}[/bold red]")
            sys.exit(1)

        # Final output
        console.print("")
        console.print("[bold green]✓ Done! Your repo is ready:[/bold green]")
        console.print(f"[bold blue]{repo.html_url}[/bold blue]")
        console.print(f"[dim]Created: README.md + {len(fs_json)} files + CI workflow + 5 issues[/dim]")

    def parse_intent(self, description: str) -> Dict:
        """Extract structured project intent from a freeform description.

        Uses `CopilotClient.generate()` to request a JSON object with the
        exact keys: project_name, project_type, stack, description, language.
        Returns the parsed and validated dict.
        """
        if not isinstance(description, str) or not description.strip():
            raise ValueError("description must be a non-empty string")

        system_prompt = (
            "You are a project analyzer. Extract project details from the user description.\n"
            "Return ONLY valid JSON with exactly these keys:\n"
            "- project_name: slug format, lowercase, hyphens only, no spaces\n"
            "- project_type: e.g. web api, cli tool, data pipeline, web app\n"
            "- stack: list of technologies mentioned or implied\n"
            "- description: one clear sentence describing the project\n"
            "- language: primary programming language"
        )

        resp_text = self.copilot.generate(system_prompt, description)

        # Attempt to safely extract JSON from the response
        try:
            parsed = json.loads(resp_text)
        except json.JSONDecodeError:
            # Try to locate a JSON object inside the text
            start = resp_text.find("{")
            end = resp_text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise ValueError("Could not parse JSON from Copilot response")
            snippet = resp_text[start : end + 1]
            try:
                parsed = json.loads(snippet)
            except json.JSONDecodeError as e:
                raise ValueError("Could not parse JSON from Copilot response") from e

        # Validate exact keys
        expected_keys = {"project_name", "project_type", "stack", "description", "language"}
        if set(parsed.keys()) != expected_keys:
            raise ValueError(f"Response JSON must contain exactly keys: {sorted(expected_keys)}")

        # Validate project_name slug
        project_name = parsed["project_name"]
        if not isinstance(project_name, str) or not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", project_name):
            raise ValueError("project_name must be a slug (lowercase letters, numbers and hyphens only)")

        # Validate project_type
        if not isinstance(parsed["project_type"], str) or not parsed["project_type"].strip():
            raise ValueError("project_type must be a non-empty string")

        # Validate stack
        stack = parsed["stack"]
        if not isinstance(stack, list) or not all(isinstance(s, str) and s.strip() for s in stack):
            raise ValueError("stack must be a list of non-empty strings")

        # Validate description (single sentence, no newlines)
        desc = parsed["description"]
        if not isinstance(desc, str) or not desc.strip() or "\n" in desc:
            raise ValueError("description must be a single sentence string")

        # Validate language
        if not isinstance(parsed["language"], str) or not parsed["language"].strip():
            raise ValueError("language must be a non-empty string")

        # Normalize values
        parsed["project_name"] = project_name.strip()
        parsed["project_type"] = parsed["project_type"].strip()
        parsed["stack"] = [s.strip() for s in stack]
        parsed["description"] = desc.strip()
        parsed["language"] = parsed["language"].strip()

        return parsed
