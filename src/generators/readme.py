import re


def generate_readme(intent: dict, patterns: list, copilot_client) -> str:
    # ask the model to write a proper README based on the project details
    system = (
        "You are an expert technical writer and software architect.\n"
        "Generate a professional README.md for a software project.\n"
        "Include these sections: title, description, tech stack, \n"
        "folder structure, how to run locally, environment variables, \n"
        "contributing, and license.\n"
        "Return markdown only. No explanation. No code fences."
    )
    user = f"Project details: {intent}\nArchitecture patterns to follow: {patterns}"
    result = copilot_client.generate(system, user)
    result = re.sub(r"^```[^\n]*\n", "", result.strip(), flags=re.MULTILINE)
    result = re.sub(r"\n```\s*$", "", result.strip())
    return result.strip()
