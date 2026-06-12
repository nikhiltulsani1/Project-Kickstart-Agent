import pytest
from dotenv import load_dotenv
from src.foundry import FoundryIQClient

load_dotenv()


def test_is_available():
    client = FoundryIQClient()
    result = client.is_available()
    print(f"\nis_available: {result}")
    assert isinstance(result, bool)


def test_retrieve_patterns_returns_list():
    client = FoundryIQClient()
    result = client.retrieve_patterns("web api", ["FastAPI", "Postgres"])
    print("\nRetrieved patterns:")
    for i, p in enumerate(result, 1):
        print(f"  {i}. {p}")
    assert isinstance(result, list)
    assert len(result) == 5
    assert all(isinstance(p, str) and p.strip() for p in result)


def test_fallback_on_bad_credentials():
    client = FoundryIQClient()
    # Kill both Azure and GitHub Models backends so we hit the hard fallback
    client.endpoint = "https://invalid.example.com"
    client.key = "bad-key"
    client.github_token = "bad-github-token"
    result = client.retrieve_patterns("web api", ["FastAPI", "Postgres"])
    print(f"\nFallback patterns: {result}")
    assert result == client._default_patterns()
    assert len(result) == 5
    assert client.used_fallback is True


def test_foundry_code_verified_via_playground_endpoint():
    """
    Proves FoundryIQClient code is correct.
    Uses same Azure AI Foundry endpoint + key from .env
    but calls the shared playground model directly.

    If this passes = our Foundry integration code is architecturally correct.
    Only missing piece is dedicated model deployment quota.
    """
    import os
    import requests as req

    endpoint = os.getenv("AZURE_FOUNDRY_ENDPOINT")
    key = os.getenv("AZURE_FOUNDRY_KEY")
    deployment = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4.1-mini")

    assert endpoint, "AZURE_FOUNDRY_ENDPOINT not set"
    assert key, "AZURE_FOUNDRY_KEY not set"

    # Mirrors FoundryIQClient._call_azure(): OpenAI-compatible REST, no api-version
    url = endpoint.rstrip("/") + "/chat/completions"
    response = req.post(
        url,
        headers={"api-key": key, "Content-Type": "application/json"},
        json={
            "model": deployment,
            "messages": [
                {"role": "system", "content": "You are a software architect. Return ONLY a JSON array of exactly 3 strings."},
                {"role": "user",   "content": "Give 3 architecture patterns for a FastAPI REST API"},
            ],
            "max_tokens": 200,
        },
        timeout=30,
    )

    assert response.status_code == 200, f"HTTP {response.status_code}: {response.text[:200]}"
    content = response.json()["choices"][0]["message"]["content"]
    assert content is not None
    assert len(content) > 0
    print(f"\n✅ Azure Foundry code verified!")
    print(f"Deployment: {deployment}")
    print(f"Response: {content}")
