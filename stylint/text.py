"""Text normalization and sentence helpers."""

import re

from .patterns import (
    ABBREVIATION_RE,
    CLAUSE_MARKER_RE,
    COLON_BEFORE_COMMAS_RE,
    GERUND_LINE_START_RE,
    GERUND_MIDLINE_RE,
    GERUND_NOUN_EXCEPTIONS,
    LINK_RE,
    OPEN_ENUM_TAIL_RE,
    SENTENCE_END_RE,
    TERMINAL_AND_OR_RE,
)


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text

    parts = text.split("---\n", 2)
    if len(parts) == 3:
        return parts[2]
    return text


def strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def strip_link_urls(line: str) -> str:
    return LINK_RE.sub(lambda match: match.group(1), line)


def strip_double_quoted(line: str) -> str:
    return re.sub(r'"[^"]*"', "", line)


def count_sentences(text: str) -> int:
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return len(SENTENCE_END_RE.findall(text))


def split_sentences(text: str) -> list[str]:
    """Split prose into individual sentences (ignoring abbreviations and code)."""
    text = re.sub(r"`[^`]*`", " ", text)
    text = ABBREVIATION_RE.sub("", text)
    return [s.strip() for s in SENTENCE_END_RE.split(text) if s.strip()]


def count_words(text: str) -> int:
    """Count whitespace-delimited tokens that contain at least one word char."""
    return sum(1 for token in text.split() if re.search(r"\w", token))


def classify_long_with_commas(sentence: str) -> str:
    """Classify a long sentence containing commas.

    Returns one of:
      - 'inline-ok' when the sentence ends in an open enumeration
        ('..., and others' / 'etc.') and the writer intentionally
        left the list open. Don't flag at all in that case.
      - 'list' when the commas separate items: a colon precedes the
        commas, OR the sentence closes with 'and X' / 'or X' over a
        run of 3+ chunks.
      - 'clause' when the commas separate clauses: a subordinating /
        coordinating conjunction follows a comma (which, that, while,
        because, but, however, so, when, if, then, ...).
      - 'clause' is also the safe default when none of the above match,
        because splitting into shorter sentences never destroys meaning
        but bulleting a clause chain does.

    The user-facing rule (in error messages) is the parallel-completion
    test: can you write a single lead-in line that all items finish
    without re-introducing the subject or verb? This classifier is just
    a hint about which side the sentence likely lands on.
    """
    s = sentence.strip()
    if OPEN_ENUM_TAIL_RE.search(s):
        return "inline-ok"
    if CLAUSE_MARKER_RE.search(s):
        return "clause"
    if COLON_BEFORE_COMMAS_RE.search(s):
        return "list"
    if TERMINAL_AND_OR_RE.search(s) and s.count(",") >= 2:
        return "list"
    return "clause"


def find_gerund_starts(plain: str) -> list[str]:
    flagged: list[str] = []
    line_match = GERUND_LINE_START_RE.match(plain.lstrip())
    if line_match and line_match.group(1).lower() not in GERUND_NOUN_EXCEPTIONS:
        flagged.append(line_match.group(1))
    for match in GERUND_MIDLINE_RE.finditer(plain):
        word = match.group(1)
        if word.lower() not in GERUND_NOUN_EXCEPTIONS:
            flagged.append(word)
    return flagged
