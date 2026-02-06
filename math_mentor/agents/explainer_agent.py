
def explain_solution(parsed_problem: dict, solution: dict) -> str:
    steps = solution.get("steps") or []

    if steps:
        lines = []
        for idx, step in enumerate(steps, start=1):
            lines.append(f"Step {idx}: {step}")
        return "\n".join(lines)

    return solution.get("explanation", "No explanation available.")
