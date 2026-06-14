import os
import json
import time
from typing import Optional

import requests
from dotenv import load_dotenv
from rich.console import Console


load_dotenv()

PRIMARY_MODEL = "gpt-4o"
FALLBACK_MODEL = "gpt-4.1-nano"

_console = Console()


class CopilotClient:
    ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"

    def __init__(self, token: Optional[str] = None, timeout: int = 30, retries: int = 2):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise EnvironmentError("GITHUB_TOKEN is not set in environment")
        self.model = PRIMARY_MODEL
        self.using_fallback = False
        self.timeout = timeout
        self.retries = int(retries)

    @property
    def current_model(self) -> str:
        return self.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not system_prompt and not user_prompt:
            raise ValueError("Both system_prompt and user_prompt are empty")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                }

                resp = requests.post(self.ENDPOINT, json=payload, headers=headers, timeout=self.timeout)

                if resp.status_code == 429:
                    try:
                        error_data = resp.json()
                    except Exception:
                        error_data = {}
                    error_code = error_data.get("error", {}).get("code", "")

                    if "RateLimitReached" in error_code and not self.using_fallback:
                        # primary model is rate-limited — switch to fallback for rest of session
                        self.model = FALLBACK_MODEL
                        self.using_fallback = True
                        _console.print(
                            f"[yellow]⚠  {PRIMARY_MODEL} rate limited. "
                            f"Switching to {FALLBACK_MODEL}...[/yellow]"
                        )
                        fallback_payload = {**payload, "model": FALLBACK_MODEL}
                        resp = requests.post(
                            self.ENDPOINT, json=fallback_payload, headers=headers, timeout=self.timeout
                        )
                        # fall through to normal response handling below
                    elif "RateLimitReached" in error_code and self.using_fallback:
                        wait_msg = error_data.get("error", {}).get("message", "")
                        raise RuntimeError(
                            f"Both {PRIMARY_MODEL} and {FALLBACK_MODEL} are rate limited.\n"
                            f"{wait_msg}\n"
                            f"Switch to a different GitHub token or wait for reset."
                        )

                if resp.status_code != 200:
                    try:
                        err_json = resp.json()
                    except Exception:
                        err_json = None
                    msg = f"API request failed with status {resp.status_code}"
                    if err_json:
                        msg += f": {err_json}"
                    raise RuntimeError(msg)

                data = resp.json()

                choices = data.get("choices") if isinstance(data, dict) else None
                if choices and len(choices) > 0:
                    first = choices[0]
                    message = first.get("message") if isinstance(first, dict) else None
                    if message and isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()

                    text = first.get("text")
                    if isinstance(text, str) and text.strip():
                        return text.strip()

                if isinstance(data, dict):
                    if "reply" in data and isinstance(data["reply"], str) and data["reply"].strip():
                        return data["reply"].strip()
                return json.dumps(data)

            except Exception as exc:
                last_exc = exc
                if attempt < self.retries:
                    time.sleep(1)
                    continue
                raise RuntimeError(f"Copilot API request failed after {self.retries} attempts: {exc}")
