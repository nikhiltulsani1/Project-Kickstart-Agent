import re


def generate_architecture_doc(intent: dict, patterns: list, copilot_client) -> str:
    # get the model to write a proper architecture doc based on what we know about the project
    system = (
        "You are a senior software architect documenting a real project.\n"
        "Generate a concrete, specific ARCHITECTURE.md document.\n"
        "Rules:\n"
        "- NO generic statements like 'the system is designed to be scalable'\n"
        "- Every section must reference the actual tech stack provided\n"
        "- ASCII diagram must show real component names from the stack\n"
        "- Technology decisions must explain WHY that specific tool was chosen\n"
        "  over alternatives (e.g. 'FastAPI over Flask because of native async support')\n"
        "- Data flow must show actual HTTP methods, real endpoint examples,\n"
        "  real database table names inferred from the project type\n"
        "- Be specific, not generic. Write as if documenting a real production system.\n"
        "Return markdown only. No explanation. No code fences."
    )
    user = (
        f"Project: {intent}\n"
        f"Architecture patterns to follow: {patterns}"
    )
    result = copilot_client.generate(system, user)
    # clean up code fences if the model wrapped it anyway
    result = re.sub(r"^```[^\n]*\n", "", result.strip(), flags=re.MULTILINE)
    result = re.sub(r"\n```\s*$", "", result.strip())
    return result.strip()
