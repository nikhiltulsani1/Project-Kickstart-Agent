import re


def generate_readme(intent: dict, patterns: list, copilot_client) -> str:
    # ask the model to write a proper README based on the project details
    system = (
        "You are an expert technical writer and software architect.\n"
        "Generate a professional README.md for a software project.\n"
        "Include these sections: title, description, tech stack, \n"
        "folder structure, how to run locally, environment variables, \n"
        "contributing, and license.\n"
        "The Folder Structure section must always be wrapped in a "
        "fenced code block using triple backticks with 'bash' language tag. "
        "Never output folder structure as inline text.\n"
        "Do NOT include any hyperlinks to the LICENSE file. "
        "Do NOT use markdown link syntax for license like [MIT License](LICENSE). "
        "If mentioning license, write plain text only: Licensed under the MIT License.\n"
        "Return markdown only. No explanation. No code fences."
    )
    user = f"Project details: {intent}\nArchitecture patterns to follow: {patterns}"
    result = copilot_client.generate(system, user)
    # Strip only an outer wrapping code fence (model sometimes wraps the whole
    # response in ```markdown ... ```), not internal fences like ```bash blocks.
    stripped = result.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        # Remove the first line (opening fence) and last line (closing fence)
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1])
    return stripped.strip()
