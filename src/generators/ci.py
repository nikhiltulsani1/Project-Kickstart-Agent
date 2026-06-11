import re


def generate_ci_workflow(intent: dict, copilot_client) -> str:
    # Ask the model to write a GitHub Actions CI workflow tailored to the project's stack.
    system = (
        "You are a DevOps engineer. Generate a GitHub Actions CI workflow YAML file.\n"
        "Return ONLY valid YAML. No explanation. No code fences. No markdown.\n"
        "Requirements:\n"
        "- Trigger on push and pull_request to main branch\n"
        "- Run on ubuntu-latest\n"
        "- Set up Python using the correct version for the stack\n"
        "- Install dependencies with: pip install -r requirements.txt\n"
        "- Run tests with: pytest\n"
        "- Name the workflow CI\n"
        "Tailor the Python version and any extra steps to the project stack."
    )
    user = f"Project details: {intent}"
    result = copilot_client.generate(system, user)
    # strip any code fences the model snuck in anyway
    result = re.sub(r"^```[^\n]*\n", "", result.strip(), flags=re.MULTILINE)
    result = re.sub(r"\n```\s*$", "", result.strip())
    return result.strip()
