import re


def _detect_task(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["derivative", "differentiate", "d/dx", "dy/dx"]):
        return "derivative"
    if any(k in lower for k in ["integral", "integrate"]):
        return "integral"
    if "limit" in lower or "lim" in lower:
        return "limit"
    if "=" in text:
        return "equation"
    return "expression"


def _detect_topic(task: str, text: str) -> str:
    lower = text.lower()
    if task in ["derivative", "integral", "limit"]:
        return "calculus"
    if "probability" in lower or "chance" in lower:
        return "probability"
    if task in ["equation", "expression"]:
        return "algebra"
    return "unknown"


def _extract_variables(text: str):
    return sorted(set(re.findall(r"[a-zA-Z]", text)))


def parse_problem(text: str) -> dict:
    task = _detect_task(text)
    topic = _detect_topic(task, text)
    variables = _extract_variables(text)

    needs_clarification = (
        len(text.strip()) < 3
        or (not variables and not re.search(r"\d", text))
    )

    return {
        "problem_text": text,
        "topic": topic,
        "task": task,
        "variables": variables,
        "constraints": [],
        "needs_clarification": needs_clarification,
    }
