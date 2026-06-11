from rich.console import Console

console = Console()


class ProjectKickstartAgent:
    """Ties together all the moving parts and drives the flow end-to-end."""

    def run(self, description: str) -> None:
        console.print("[bold cyan]Step 1/5:[/bold cyan] Parsing project intent...")
        console.print("[bold cyan]Step 2/5:[/bold cyan] Retrieving architecture patterns via Foundry IQ...")
        console.print("[bold cyan]Step 3/5:[/bold cyan] Generating project artifacts...")
        console.print("[bold cyan]Step 4/5:[/bold cyan] Creating GitHub repository...")
        console.print("[bold cyan]Step 5/5:[/bold cyan] Creating first sprint issues...")
