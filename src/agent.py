from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import json
import re
import sys
import time
import threading
import concurrent.futures
from typing import Dict

from src.copilot import CopilotClient
from src.github_client import GitHubClient
from src.generators.ci import generate_ci_workflow
from src.generators.architecture import generate_architecture_doc
from src.generators.readme import generate_readme
from src.generators.testplan import generate_test_plan


console = Console()


class ProjectKickstartAgent:
    """Ties together all the moving parts and drives the flow end-to-end."""

    def __init__(self):
        self.copilot = CopilotClient()

    def run(self, description: str) -> None:
        console.print(f"[dim]Using model: {self.copilot.current_model}[/dim]")
        start_time = time.time()

        def _lap():
            return round(time.time() - _lap.last, 1)
        _lap.last = start_time

        def _tick():
            elapsed = _lap()
            _lap.last = time.time()
            return elapsed

        # STEP 1: Parse intent
        try:
            intent = self.parse_intent(description)
            stack_items = ", ".join(intent.get("stack", []))
            console.print(f"✓ Parsed: {intent.get('project_name')} ({stack_items}) [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Step 1 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 2: Retrieve architecture patterns via Foundry IQ, fallback to defaults
        try:
            from src.foundry import FoundryIQClient
            foundry = FoundryIQClient()
            if foundry.is_available():
                patterns = foundry.retrieve_patterns(
                    intent["project_type"],
                    intent["stack"],
                )
                if foundry.used_fallback:
                    pattern_source = "default"
                elif foundry.backend == "github-models":
                    pattern_source = "GitHub Models (Foundry IQ fallback)"
                else:
                    pattern_source = "Foundry IQ"
            else:
                patterns = [
                    "Use layered architecture: separate concerns into routes, services, models",
                    "Write tests first: include pytest setup in initial scaffold",
                    "Use environment variables for all secrets and config",
                    "Add a Makefile for common dev commands",
                    "Document the API with docstrings and a README",
                ]
                pattern_source = "default"
            console.print(f"✓ Retrieved {len(patterns)} architecture patterns ({pattern_source}) [dim]({_tick()}s)[/dim]")
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

        # STEP 3: Generate docs — API has a 2-request concurrency limit,
        # so we run README + ARCHITECTURE together, then TESTPLAN after
        readme_result = [None, None]  # [content, error]
        arch_result = [None, None]

        def _gen_readme():
            try:
                readme_result[0] = generate_readme(intent, patterns, self.copilot)
            except Exception as e:
                readme_result[1] = e

        def _gen_arch():
            try:
                arch_result[0] = generate_architecture_doc(intent, patterns, self.copilot)
            except Exception as e:
                arch_result[1] = e

        t1 = threading.Thread(target=_gen_readme)
        t2 = threading.Thread(target=_gen_arch)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        if readme_result[1]:
            console.print(f"[bold red]✗ README generation failed: {readme_result[1]}[/bold red]")
            sys.exit(1)
        if arch_result[1]:
            console.print(f"[bold red]✗ Architecture doc failed: {arch_result[1]}[/bold red]")
            sys.exit(1)

        readme_md = readme_result[0]
        arch_md = arch_result[0]
        console.print(f"✓ Generated README.md + ARCHITECTURE.md (parallel) [dim]({_tick()}s)[/dim]")

        # TESTPLAN runs after since we'd hit the concurrency cap otherwise
        try:
            testplan_md = generate_test_plan(intent, patterns, self.copilot)
            console.print(f"✓ Generated TESTPLAN.md [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Test plan failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 4: Build folder structure — language template as the base,
        # then ask the LLM to tailor the 3 core files to the actual stack
        try:
            from src.language_config import detect_language_config, get_placeholder_test
            lang_config = detect_language_config(intent)
            base_files = lang_config["folder_structure"].copy()

            test_path, test_content = get_placeholder_test(intent, intent["project_name"])
            base_files[test_path] = test_content

            # for Go, use just the project name as the module (no github.com prefix)
            # so internal import paths in LLM-generated files match go.mod exactly
            go_module = intent["project_name"]
            if lang_config["language"] == "go" and "go.mod" in base_files:
                base_files["go.mod"] = f"module {go_module}\n\ngo 1.22"

            entry_files = lang_config.get("llm_entry_files", ["src/main.py", "src/models.py", "src/routes.py"])
            if entry_files:
                fs_system = (
                    "You are a software engineer. Generate starter content for specific files.\n"
                    "Return ONLY valid JSON where keys are filenames and values are file contents.\n"
                    "Tailor every file to the exact project description and stack.\n"
                    "No markdown, no code fences, valid JSON only.\n"
                )
                go_note = (
                    f" The Go module name is '{go_module}' — all internal imports must use "
                    f"'{go_module}/internal/...' as the prefix. Do NOT use 'github.com/...' prefixes."
                    if lang_config["language"] == "go" else ""
                )
                fs_user = (
                    f"Project: {intent}\n"
                    f"Generate content ONLY for these exact file paths: {entry_files}\n"
                    f"Use real imports and starter code for {intent['stack']}."
                    f"{go_note}\n"
                    f"Return a JSON object with exactly those keys."
                )
                fs_resp = self.copilot.generate(fs_system, fs_user)
                llm_files = _safe_load_json(fs_resp)
                if isinstance(llm_files, dict):
                    base_files.update(llm_files)

            fs_json = base_files
            console.print(
                f"✓ Generated folder structure ({len(fs_json)} files)"
                f" — {lang_config['language']} template [dim]({_tick()}s)[/dim]"
            )
        except Exception as e:
            console.print(f"[bold red]✗ Step 4 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 5: Generate CI workflow
        try:
            ci_yaml = generate_ci_workflow(intent, self.copilot)
            console.print(f"✓ Generated CI workflow [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Step 5 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 6: Create GitHub repo
        try:
            gh = GitHubClient()
            repo = gh.create_repo(intent["project_name"], intent["description"])
            console.print(f"✓ Created repo: {repo.html_url} [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Step 6 failed: {e}[/bold red]")
            sys.exit(1)

        # STEP 7: Push everything in a single commit
        try:
            def _redact_secrets(files: dict) -> dict:
                # GitHub secret scanning blocks pushes when generated code contains
                # tokens that match real secret patterns (e.g. sk_test_... for Stripe).
                # Replace common realistic-looking placeholders with safe dummy values.
                import re
                patterns = [
                    # Stripe secret/publishable keys
                    (r'sk_(test|live)_[A-Za-z0-9]{20,}', 'sk_test_PLACEHOLDER'),
                    (r'pk_(test|live)_[A-Za-z0-9]{20,}', 'pk_test_PLACEHOLDER'),
                    # Generic bearer tokens / API keys that look real (long base64-ish strings)
                    (r'Bearer [A-Za-z0-9+/=]{40,}', 'Bearer PLACEHOLDER_TOKEN'),
                    # AWS access keys
                    (r'AKIA[0-9A-Z]{16}', 'AKIAPLACEHOLDER00000'),
                    # Generic private key headers
                    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END (RSA |EC )?PRIVATE KEY-----',
                     '-----BEGIN PRIVATE KEY-----\nPLACEHOLDER\n-----END PRIVATE KEY-----'),
                ]
                clean = {}
                for path, content in files.items():
                    for pat, replacement in patterns:
                        content = re.sub(pat, replacement, content)
                    clean[path] = content
                return clean

            # bundle all generated files together
            all_files = {
                "README.md": readme_md,
                "ARCHITECTURE.md": arch_md,
                "TESTPLAN.md": testplan_md,
                ".github/workflows/ci.yml": ci_yaml,
                # always provide a requirements.txt so CI pip install never errors
                "requirements.txt": "pytest\n",
            }
            all_files.update(fs_json)
            total_files = len(all_files)

            gh.create_folder_structure(
                repo,
                _redact_secrets(all_files),
                commit_message="feat: initial project setup by Project Kickstart Agent",
            )
            console.print(f"✓ Pushed {total_files} files in a single commit [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Step 7 failed: {e}[/bold red]")
            sys.exit(1)

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

            for issue in issues_json:
                if not issue.get("title") or not issue.get("body"):
                    raise ValueError("Each issue must have title and body")

            def _create_single_issue(issue):
                return gh.create_issue(repo, issue["title"], issue["body"])

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
                futures = [pool.submit(_create_single_issue, i) for i in issues_json]
                results = [f.result() for f in futures]

            console.print(f"✓ Created {len(results)} sprint issues [dim]({_tick()}s)[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Step 8 failed: {e}[/bold red]")
            sys.exit(1)

        # wrap it up with a summary panel
        elapsed = round(time.time() - start_time, 1)
        repo_url = repo.html_url
        file_count = total_files
        project_name = intent["project_name"]

        summary = Table(show_header=False, box=None, padding=(0, 2))
        summary.add_row("📁 Repo", project_name)
        summary.add_row("📄 Files pushed", f"{file_count} files")
        summary.add_row("✅ CI Workflow", ".github/workflows/ci.yml")
        summary.add_row("🎯 Sprint Issues", "5 issues created")
        summary.add_row("🏗️ Patterns", f"5 patterns via {pattern_source}")
        summary.add_row("🤖 Model", self.copilot.current_model)
        summary.add_row("⏱️  Time", f"{elapsed}s")

        panel = Panel(
            summary,
            title=f"[bold green]✓ {project_name} is ready[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            subtitle=f"[dim]{repo_url}[/dim]",
        )
        console.print()
        console.print(panel, width=100)
        console.print()

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
