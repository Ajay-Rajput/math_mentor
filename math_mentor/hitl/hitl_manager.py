
def needs_human_intervention(parser_output, verifier_output=None):
    if parser_output.get("needs_clarification"):
        return True, "Parser detected ambiguity"

    if verifier_output and verifier_output.get("needs_human_review"):
        return True, "Verifier flagged a potential issue"

    return False, None
