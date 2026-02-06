import re

from sympy import Eq, solve, symbols, diff, integrate, limit, simplify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

TRANSFORMS = standard_transformations + (implicit_multiplication_application,)

SAFE_FUNCS = {
    "sqrt": __import__("sympy").sqrt,
    "sin": __import__("sympy").sin,
    "cos": __import__("sympy").cos,
    "tan": __import__("sympy").tan,
    "log": __import__("sympy").log,
    "ln": __import__("sympy").log,
    "exp": __import__("sympy").exp,
    "pi": __import__("sympy").pi,
    "E": __import__("sympy").E,
    "Abs": __import__("sympy").Abs,
}


def _build_symbols(text: str):
    vars_found = sorted(set(re.findall(r"[a-zA-Z]", text)))
    return {v: symbols(v) for v in vars_found}


def _normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(
        r"square root of\s+([0-9]+(\.[0-9]+)?)",
        r"sqrt(\1)",
        text,
        flags=re.I,
    )
    return text


def _parse_expr(expr_str: str, local_dict: dict):
    return parse_expr(expr_str, transformations=TRANSFORMS, local_dict=local_dict)


def _extract_derivative_expr(text: str):
    match = re.search(r"(?:derivative|differentiate)\s+(?:of\s+)?(.+)", text, flags=re.I)
    if match:
        return match.group(1).strip()
    return text


def _extract_integral_expr(text: str):
    match = re.search(r"(?:integral|integrate)\s+(?:of\s+)?(.+)", text, flags=re.I)
    if match:
        return match.group(1).strip()
    return text


def _extract_limit_parts(text: str):
    match = re.search(
        r"limit\s+of\s+(.+)\s+as\s+([a-zA-Z])\s*->\s*([-\d\.]+)",
        text,
        flags=re.I,
    )
    if match:
        return match.group(1).strip(), match.group(2), match.group(3)
    return None, None, None


def solve_problem(parsed_problem: dict, context: list) -> dict:
    text = _normalize_text(parsed_problem["problem_text"])
    task = parsed_problem.get("task", "expression")

    symbols_dict = _build_symbols(text)
    local_dict = {**SAFE_FUNCS, **symbols_dict}

    steps = []
    confidence = 0.6
    answer = "N/A"
    raw_result = None
    solutions = None
    solution_var = None

    try:
        if task == "derivative":
            expr_str = _extract_derivative_expr(text)
            expr = _parse_expr(expr_str, local_dict)
            var = symbols_dict.get("x") or (list(symbols_dict.values())[0] if symbols_dict else symbols("x"))
            result = diff(expr, var)

            steps.append(f"Differentiate: {expr}")
            steps.append(f"With respect to: {var}")
            steps.append(f"Result: {result}")

            answer = str(result)
            raw_result = result
            confidence = 0.9

        elif task == "integral":
            expr_str = _extract_integral_expr(text)
            expr = _parse_expr(expr_str, local_dict)
            var = symbols_dict.get("x") or (list(symbols_dict.values())[0] if symbols_dict else symbols("x"))
            result = integrate(expr, var)

            steps.append(f"Integrate: {expr}")
            steps.append(f"With respect to: {var}")
            steps.append(f"Result: {result} + C")

            answer = str(result)
            raw_result = result
            confidence = 0.88

        elif task == "limit":
            expr_str, var_name, point = _extract_limit_parts(text)
            if not expr_str:
                raise ValueError("Limit format not recognized. Use 'limit of f(x) as x->a'.")

            expr = _parse_expr(expr_str, local_dict)
            var = symbols(var_name)
            point_expr = _parse_expr(point, local_dict)
            result = limit(expr, var, point_expr)

            steps.append(f"Compute limit of: {expr}")
            steps.append(f"As {var} approaches {point_expr}")
            steps.append(f"Result: {result}")

            answer = str(result)
            raw_result = result
            confidence = 0.85

        elif task == "equation":
            if "=" not in text:
                raise ValueError("Equation missing '=' sign.")

            lhs_str, rhs_str = text.split("=", 1)
            lhs = _parse_expr(lhs_str, local_dict)
            rhs = _parse_expr(rhs_str, local_dict)
            eq = Eq(lhs, rhs)

            vars_list = list(symbols_dict.values())
            steps.append(f"Solve equation: {eq}")

            if not vars_list:
                result = simplify(lhs - rhs)
                answer = "True" if result == 0 else "False"
                raw_result = result
                steps.append(f"Simplify both sides: {result}")
                confidence = 0.75

            elif len(vars_list) == 1:
                var = vars_list[0]
                solution_var = var.name
                sol = solve(eq, var)
                solutions = [str(s) for s in sol]

                answer = str(solutions)
                raw_result = sol
                steps.append(f"Solutions for {var}: {solutions}")
                confidence = 0.9 if solutions else 0.5

            else:
                sol = solve(eq, vars_list, dict=True)
                solutions = [str(s) for s in sol]
                answer = str(solutions)
                raw_result = sol
                steps.append(f"Solutions: {solutions}")
                confidence = 0.75 if solutions else 0.4

        else:
            expr = _parse_expr(text, local_dict)
            result = simplify(expr)

            steps.append(f"Simplify expression: {expr}")
            steps.append(f"Result: {result}")

            answer = str(result)
            raw_result = result
            confidence = 0.85

    except Exception as e:
        answer = "Error"
        steps.append(f"Solver error: {e}")
        confidence = 0.2

    explanation = "\n".join(steps) if steps else "No steps available."

    return {
        "answer": answer,
        "explanation": explanation,
        "confidence": confidence,
        "used_context": context,
        "steps": steps,
        "task": task,
        "raw_result": str(raw_result) if raw_result is not None else None,
        "solutions": solutions,
        "solution_var": solution_var,
    }
