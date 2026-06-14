import os
import json
import requests

from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

_SYSTEM_PROMPT = (
    "You are an expert software architect.\n"
    "Return ONLY a JSON array of exactly 5 architecture pattern strings.\n"
    "Each pattern must be specific and actionable, not generic.\n"
    "Tailor patterns to the exact project type and tech stack provided.\n"
    "Return valid JSON array only. No explanation. No markdown."
)

_GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
_AZURE_INFERENCE_MODEL = "gpt-4o"
_GITHUB_FALLBACK_MODEL = "gpt-4.1-nano"


def _parse_patterns(content: str) -> list:
    """Extract a 5-item list from a JSON string, stripping code fences if present."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    patterns = json.loads(content)
    if not isinstance(patterns, list) or len(patterns) != 5:
        raise ValueError(f"Expected 5 patterns, got {len(patterns) if isinstance(patterns, list) else type(patterns)}")
    return patterns


class FoundryIQClient:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
        self.key = os.getenv("AZURE_FOUNDRY_KEY", "")
        self.deployment = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.used_fallback = False
        self.backend: str = "default"  # "azure", "github-models", or "default"

    def is_available(self) -> bool:
        return bool((self.endpoint and self.key) or self.github_token)

    def retrieve_patterns(self, project_type: str, stack: list) -> list:
        if not self.is_available():
            self.used_fallback = True
            return self._default_patterns()

        user_prompt = f"Project type: {project_type}\nStack: {', '.join(stack)}"

        # --- Try Azure AI Foundry (direct inference endpoint) ---
        if self.endpoint and self.key:
            try:
                patterns = self._call_azure(user_prompt)
                self.used_fallback = False
                self.backend = "azure"
                return patterns
            except Exception as e:
                first_line = str(e).split("\n")[0]
                console.print(f"[dim]Azure Foundry inference unavailable: {first_line}. Trying GitHub Models.[/dim]")

        # --- Fall back to GitHub Models (same Azure-backed inference, different auth) ---
        if self.github_token:
            try:
                patterns = self._call_github_models(user_prompt)
                self.used_fallback = False
                self.backend = "github-models"
                return patterns
            except Exception as e:
                first_line = str(e).split("\n")[0]
                console.print(f"[dim]GitHub Models unavailable: {first_line}. Using default patterns.[/dim]")

        self.used_fallback = True
        self.backend = "default"
        return self._default_patterns()

    def _call_azure(self, user_prompt: str) -> list:
        """Call Azure AI Foundry endpoint via OpenAI-compatible REST (no api-version).

        The endpoint is expected to be the /openai/v1 base URL; we append
        /chat/completions and send api-key auth with the model name in the body.
        azure-ai-inference ChatCompletionsClient is intentionally NOT used here
        because it always appends ?api-version=... which this endpoint rejects.
        """
        url = self.endpoint.rstrip("/") + "/chat/completions"
        response = requests.post(
            url,
            headers={"api-key": self.key, "Content-Type": "application/json"},
            json={
                "model": self.deployment,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 500,
            },
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_patterns(content)

    def _call_github_models(self, user_prompt: str) -> list:
        """Call GitHub Models (Azure-backed) using the GITHUB_TOKEN.

        Tries gpt-4o first; on 429 immediately switches to gpt-4.1-nano (no sleep),
        mirroring the CopilotClient fallback strategy.
        """
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }

        for model in (_AZURE_INFERENCE_MODEL, _GITHUB_FALLBACK_MODEL):
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 500,
            }
            response = requests.post(_GITHUB_MODELS_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 429 and model == _AZURE_INFERENCE_MODEL:
                console.print(f"[dim]Foundry IQ: gpt-4o rate-limited, switching to {_GITHUB_FALLBACK_MODEL}[/dim]")
                continue
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return _parse_patterns(content)

        raise RuntimeError(f"Both {_AZURE_INFERENCE_MODEL} and {_GITHUB_FALLBACK_MODEL} rate-limited on GitHub Models")

    def _default_patterns(self) -> list:
        return [
            "Use layered architecture: separate concerns into routes, services, models",
            "Write tests first: include pytest setup in initial scaffold",
            "Use environment variables for all secrets and config",
            "Add a Makefile for common dev commands",
            "Document the API with docstrings and a README",
        ]
