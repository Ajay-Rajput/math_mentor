# Math Mentor

Multimodal math tutor built with a multi-agent architecture, RAG, and human-in-the-loop feedback.

## Quickstart
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run math_mentor/app.py`

## Project Layout
- `math_mentor/app.py` — Streamlit entry point.
- `math_mentor/agents/` — parser, solver, verifier, and explainer agents.
- `math_mentor/rag/` — retrieval components and documents.
- `math_mentor/memory/` — lightweight memory store.

## Notes
- RAG source docs live in `math_mentor/rag/documents/`.
- Uses FAISS CPU for vector search.
