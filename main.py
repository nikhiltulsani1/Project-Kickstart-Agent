import click
from rich.console import Console
from src.agent import ProjectKickstartAgent

console = Console()


@click.command()
@click.argument("description")
def kickstart(description: str):
    """Turn a plain-English description into a ready-to-go GitHub repo."""
    agent = ProjectKickstartAgent()
    agent.run(description)


if __name__ == "__main__":
    kickstart()
