import pytest

from src.copilot import CopilotClient


def test_generate_hello():
    client = CopilotClient()
    resp = client.generate("You are a helpful assistant", "Say hello in one sentence")
    print("Copilot response:", resp)
    assert isinstance(resp, str) and resp.strip() != ""


def test_generate_empty_raises():
    client = CopilotClient()
    with pytest.raises(ValueError):
        client.generate("", "")
