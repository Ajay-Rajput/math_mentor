import re

SUPERSCRIPT_MAP = str.maketrans({
    "\u2070": "0",
    "\u00b9": "1",
    "\u00b2": "2",
    "\u00b3": "3",
    "\u2074": "4",
    "\u2075": "5",
    "\u2076": "6",
    "\u2077": "7",
    "\u2078": "8",
    "\u2079": "9",
})


def _normalize_superscripts(text: str) -> str:
    def repl(match):
        base = match.group(1)
        sup = match.group(2).translate(SUPERSCRIPT_MAP)
        return f"{base}**{sup}"

    return re.sub(
        r"([A-Za-z0-9\)])([\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079]+)",
        repl,
        text,
    )


def process_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()
    text = text.replace("Ã—", "*")
    text = text.replace("âˆ’", "-")
    text = text.replace("\u2212", "-")
    text = text.replace("\u00d7", "*")
    text = text.replace("^", "**")
    text = text.replace("\u221a", "sqrt")
    text = _normalize_superscripts(text)
    text = re.sub(r"\s+", " ", text)
    return text
