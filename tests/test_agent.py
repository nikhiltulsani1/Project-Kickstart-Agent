"""Tests for ProjectKickstartAgent."""

from src.agent import ProjectKickstartAgent


def test_agent_run_completes(capsys):
    agent = ProjectKickstartAgent()
    agent.run("A simple todo app")
