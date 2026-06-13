import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

import click
from rich.console import Console
from src.agent import ProjectKickstartAgent

console = Console()


@click.command()
@click.argument("description")
@click.option('--name', default=None,
              help='Override the generated project name (used as GitHub repo name)')
def kickstart(description: str, name: str):
    """Turn a plain-English description into a ready-to-go GitHub repo."""
    agent = ProjectKickstartAgent()
    agent.run(description, name_override=name)


if __name__ == "__main__":
    kickstart()
