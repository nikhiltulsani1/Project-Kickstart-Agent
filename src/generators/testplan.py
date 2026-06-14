import re


def generate_test_plan(intent: dict, patterns: list, copilot_client) -> str:
    # have the model put together a real test plan someone could actually hand off
    system = (
        "You are a senior QA engineer with 10 years of experience.\n"
        "Generate a concrete, detailed TESTPLAN.md for a software project.\n"
        "Include these sections:\n\n"
        "1. Test Strategy — testing approach for this specific stack\n"
        "2. Test Levels\n"
        "   - Unit Tests: specific functions/methods to test with examples\n"
        "   - Integration Tests: specific API endpoints or DB operations to test\n"
        "   - E2E Tests: specific user flows to test end to end\n"
        "3. Test Cases Table — markdown table with columns:\n"
        "   ID | Test Case | Type | Priority | Expected Result\n"
        "   Include minimum 10 specific test cases relevant to the actual stack\n"
        "4. Edge Cases — minimum 5 specific edge cases for this project type\n"
        "5. Test Data Requirements — what seed data or fixtures are needed\n"
        "6. Tools & Setup — specific testing tools for the stack with setup commands\n\n"
        "Rules:\n"
        "- NO generic statements\n"
        "- Every test case must reference actual endpoints, models, or functions\n"
        "  inferred from the project type and stack\n"
        "- Use real HTTP methods, real field names, real status codes\n"
        "- Write as if you are handing this to a junior developer to implement\n"
        "Return markdown only. No explanation. No code fences."
    )
    user = (
        f"Project: {intent}\n"
        f"Architecture patterns: {patterns}"
    )
    result = copilot_client.generate(system, user)
    result = re.sub(r"^```[^\n]*\n", "", result.strip(), flags=re.MULTILINE)
    result = re.sub(r"\n```\s*$", "", result.strip())
    return result.strip()
