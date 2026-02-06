import streamlit as st

from multimodal.text import process_text

from agents.parser_agent import parse_problem
from agents.router_agent import route_problem
from rag.retriever import retrieve_context
from agents.solver_agent import solve_problem
from agents.verifier_agent import verify_solution
from agents.explainer_agent import explain_solution

from hitl.hitl_manager import needs_human_intervention
from memory.memory_store import load_memory, save_to_memory


st.set_page_config(page_title="Math Mentor AI", layout="wide")
st.title("Math Mentor AI (Text Mode)")


for key in [
    "raw_text",
    "parsed",
    "route",
    "context",
    "solution",
    "verification",
]:
    if key not in st.session_state:
        st.session_state[key] = None


st.subheader("Enter Math Problem")

raw_text = st.text_area(
    "Type a math question",
    value=st.session_state.raw_text or "",
)

st.session_state.raw_text = raw_text


if st.button("Parse"):
    clean_text = process_text(st.session_state.raw_text)

    st.session_state.parsed = parse_problem(clean_text)
    st.session_state.route = route_problem(st.session_state.parsed)
    st.session_state.context = retrieve_context(clean_text)

    st.success("Problem parsed successfully")


if st.session_state.parsed:
    st.subheader("Parsed Output")
    st.json(st.session_state.parsed)

    st.subheader("Routing")
    st.json(st.session_state.route)


if st.session_state.parsed:
    memory = load_memory()
    similar = [
        m for m in memory
        if m["topic"] == st.session_state.parsed["topic"]
    ]

    if similar:
        st.info(f"Found {len(similar)} similar solved problems in memory")


if st.session_state.parsed and st.session_state.context:
    if st.button("Solve"):
        st.session_state.solution = solve_problem(
            st.session_state.parsed,
            st.session_state.context,
        )

        st.subheader("Solution")
        st.json(st.session_state.solution)


if st.session_state.solution:
    st.session_state.verification = verify_solution(
        st.session_state.parsed,
        st.session_state.solution,
    )

    st.subheader("Verification")
    st.json(st.session_state.verification)


if st.session_state.solution and st.session_state.verification:
    save_to_memory({
        "problem": st.session_state.parsed["problem_text"],
        "topic": st.session_state.parsed["topic"],
        "answer": st.session_state.solution.get("answer"),
        "confidence": st.session_state.verification.get("confidence", 0.5),
        "feedback": None,
    })


if st.session_state.parsed and st.session_state.verification:
    hitl_required, reason = needs_human_intervention(
        st.session_state.parsed,
        st.session_state.verification,
    )

    if hitl_required:
        st.warning(f"Human Review Required: {reason}")

        corrected_text = st.text_area(
            "Please correct or clarify the problem:",
            value=st.session_state.parsed["problem_text"],
        )

        if st.button("Approve & Continue"):
            st.session_state.parsed["problem_text"] = corrected_text
            st.success("Human input accepted")


if st.session_state.solution:
    explanation_text = explain_solution(
        st.session_state.parsed,
        st.session_state.solution,
    )

    st.subheader("Step-by-Step Explanation")
    st.write(explanation_text)


if st.button("Retrieve Context"):
    ctx = retrieve_context(st.session_state.raw_text)

    st.subheader("Retrieved Knowledge")
    for c in ctx:
        st.write(c)
