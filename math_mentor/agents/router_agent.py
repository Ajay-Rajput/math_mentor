def route_problem(parsed_problem: dict) -> dict:
    topic = parsed_problem.get("topic", "unknown")

    if topic == "algebra":
        route = "algebra_solver"
    elif topic == "probability":
        route = "probability_solver"
    elif topic == "calculus":
        route = "calculus_solver"
    else:
        route = "generic_solver"

    return {
        "route": route,
        "confidence": 0.8 if topic != "unknown" else 0.4
    }
