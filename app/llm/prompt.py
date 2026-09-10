"""
DebugPilot prompt builder.
"""

SYSTEM_PROMPT = """
You are DebugPilot.

Answer the user's question using ONLY the repository code provided below.

Read the code carefully.

If the answer is present in the code, answer it directly.
Do not say information is missing when the code contains the answer.
Do not invent behavior that is not shown in the code.

Use the exact names of files, classes, functions, variables, and models
from the code.

Explain the code clearly and directly.
"""


def build_prompt(query: str, context: str) -> str:
    return f"""
{SYSTEM_PROMPT}

REPOSITORY CODE:
{context}

USER QUESTION:
{query}

ANSWER:
"""


def build_low_confidence_prompt(query: str) -> str:
    return (
        "The repository code does not contain enough information to answer "
        f"this question: {query}"
    )