import re

from sympy import simplify, symbols
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


def _build_symbols(text: str):
    vars_found = sorted(set(re.findall(r"[a-zA-Z]", text)))
    return {v: symbols(v) for v in vars_found}


def verify_solution(parsed_problem: dict, solution: dict) -> dict:
    confidence = solution.get("confidence", 0.5)
    issues = []
    needs_human_review = False

    if solution.get("answer") in ["Error", "N/A", "Not supported"]:
        issues.append("Solver could not produce a valid answer")
        needs_human_review = True

    task = parsed_problem.get("task")
    problem_text = parsed_problem.get("problem_text", "")

    if task == "equation" and "=" in problem_text:
        lhs_str, rhs_str = problem_text.split("=", 1)
        local_dict = _build_symbols(problem_text)

        try:
            lhs = parse_expr(lhs_str, transformations=TRANSFORMS, local_dict=local_dict)
            rhs = parse_expr(rhs_str, transformations=TRANSFORMS, local_dict=local_dict)

            solution_var = solution.get("solution_var")
            solutions = solution.get("solutions") or []

            if solution_var and solutions:
                var = local_dict.get(solution_var, symbols(solution_var))
                for sol in solutions:
                    value = parse_expr(str(sol), transformations=TRANSFORMS, local_dict=local_dict)
                    check = simplify(lhs.subs(var, value) - rhs.subs(var, value))
                    if check != 0:
                        issues.append(f"Solution {sol} does not satisfy the equation")
                        needs_human_review = True
                        break
            else:
                issues.append("Could not verify equation solution")
                needs_human_review = True
        except Exception as e:
            issues.append(f"Verification error: {e}")
            needs_human_review = True

    if confidence < 0.7:
        issues.append("Low confidence in solution")
        needs_human_review = True

    return {
        "verified": not needs_human_review,
        "issues": issues,
        "needs_human_review": needs_human_review,
        "confidence": confidence,
    }
