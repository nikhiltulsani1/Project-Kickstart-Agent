import os
import json
import time
from typing import Optional

import requests
from dotenv import load_dotenv


load_dotenv()


class CopilotClient:
    ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"

    def __init__(self, token: Optional[str] = None, model: str = "gpt-4o", timeout: int = 30, retries: int = 2):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise EnvironmentError("GITHUB_TOKEN is not set in environment")
        self.model = model
        self.timeout = timeout
        self.retries = int(retries)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not system_prompt and not user_prompt:
            raise ValueError("Both system_prompt and user_prompt are empty")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                resp = requests.post(self.ENDPOINT, json=payload, headers=headers, timeout=self.timeout)
                # Raise for HTTP errors
                if resp.status_code != 200:
                    # Attempt to include server message but avoid leaking sensitive data
                    try:
                        err_json = resp.json()
                    except Exception:
                        err_json = None
                    msg = f"API request failed with status {resp.status_code}"
                    if err_json:
                        msg += f": {err_json}"
                    raise RuntimeError(msg)

                data = resp.json()

                # Common response shapes: choices[0].message.content or choices[0].text
                choices = data.get("choices") if isinstance(data, dict) else None
                if choices and len(choices) > 0:
                    first = choices[0]
                    # Try message.content
                    message = first.get("message") if isinstance(first, dict) else None
                    if message and isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str) and content.strip():
                            return content.strip()

                    # Try text
                    text = first.get("text")
                    if isinstance(text, str) and text.strip():
                        return text.strip()

                # Fallback: try a top-level "reply" or stringifying JSON
                if isinstance(data, dict):
                    if "reply" in data and isinstance(data["reply"], str) and data["reply"].strip():
                        return data["reply"].strip()
                # As last resort, return the JSON as a string
                return json.dumps(data)

            except Exception as exc:
                last_exc = exc
                # brief backoff
                if attempt < self.retries:
                    time.sleep(1)
                    continue
                # no more retries
                raise RuntimeError(f"Copilot API request failed after {self.retries} attempts: {exc}")
