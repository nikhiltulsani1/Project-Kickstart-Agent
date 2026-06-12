import json
import pytest
from unittest.mock import patch, MagicMock

from src.copilot import CopilotClient, PRIMARY_MODEL, FALLBACK_MODEL


def _ok_response(content="Hello!"):
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return mock


def _429_response():
    mock = MagicMock()
    mock.status_code = 429
    mock.json.return_value = {
        "error": {
            "code": "RateLimitReached",
            "message": "Rate limit of 50 per 86400s exceeded.",
        }
    }
    return mock


def test_normal_uses_primary():
    client = CopilotClient()
    with patch("src.copilot.requests.post", return_value=_ok_response("hi")) as mock_post:
        result = client.generate("system", "user")
    assert result == "hi"
    assert client.model == PRIMARY_MODEL
    assert client.using_fallback is False
    print(f"\nModel used: {client.current_model}")


def test_fallback_on_429():
    client = CopilotClient()
    responses = [_429_response(), _ok_response("fallback response")]
    with patch("src.copilot.requests.post", side_effect=responses):
        result = client.generate("system", "user")
    assert result == "fallback response"
    assert client.model == FALLBACK_MODEL
    assert client.using_fallback is True
    print(f"\nSwitched to fallback model: {client.current_model}")


def test_fallback_used_for_subsequent_calls():
    client = CopilotClient()
    # first call: 429 then success on fallback
    # second call: direct success (already on fallback model)
    responses = [_429_response(), _ok_response("first"), _ok_response("second")]
    with patch("src.copilot.requests.post", side_effect=responses):
        r1 = client.generate("system", "user1")
        r2 = client.generate("system", "user2")
    assert r1 == "first"
    assert r2 == "second"
    assert client.using_fallback is True
    print(f"\nBoth calls used fallback: {client.current_model}")


def test_both_models_limited():
    client = CopilotClient()
    client.using_fallback = True  # simulate already switched to fallback
    client.model = FALLBACK_MODEL
    with patch("src.copilot.requests.post", return_value=_429_response()):
        with pytest.raises(RuntimeError) as exc_info:
            client.generate("system", "user")
    assert PRIMARY_MODEL in str(exc_info.value)
    assert FALLBACK_MODEL in str(exc_info.value)
    print(f"\nError: {exc_info.value}")


def test_generate_empty_raises():
    client = CopilotClient()
    with pytest.raises(ValueError):
        client.generate("", "")
