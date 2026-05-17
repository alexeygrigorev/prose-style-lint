"""Text normalization and sentence helpers."""

import re

from .patterns import (
    ABBREVIATION_RE,
    ACTION_CHAIN_RE,
    CLAUSE_MARKER_RE,
    COLON_BEFORE_COMMAS_RE,
    FOOTNOTE_REF_RE,
    GERUND_LINE_START_RE,
    GERUND_MIDLINE_RE,
    GERUND_NOUN_EXCEPTIONS,
    IRREGULAR_PAST_RE,
    LINK_RE,
    NON_VERB_STARTERS,
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


def _verb_led_chunk_count(sentence: str) -> int:
    """Count comma chunks (after the first) that start with a word not
    in NON_VERB_STARTERS. Such chunks tend to be verb-led ('pick X',
    'detects Y'). The first chunk is skipped because it usually carries
    its own noun phrase and a finite verb."""
    parts = sentence.split(",")
    if len(parts) < 3:
        return 0
    count = 0
    for chunk in parts[1:]:
        # Strip leading connectors.
        tokens = chunk.strip().split()
        i = 0
        while i < len(tokens) and tokens[i].lower() in {"and", "or", "then", "also"}:
            i += 1
        if i >= len(tokens):
            continue
        first = tokens[i].lower().strip(".,;:!?\"'")
        if not first:
            continue
        # A leading capital usually signals a proper noun (list item),
        # so skip those.
        if tokens[i][0].isupper():
            continue
        if first not in NON_VERB_STARTERS:
            count += 1
    return count


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
    # Strip footnote refs so end-of-sentence anchors line up.
    s = FOOTNOTE_REF_RE.sub("", sentence).strip()
    if OPEN_ENUM_TAIL_RE.search(s):
        return "inline-ok"
    if CLAUSE_MARKER_RE.search(s):
        return "clause"
    # Action chain: 2+ comma chunks led by a transitive verb with an
    # elided subject ("you open X, pick Y, choose Z" or "detects X,
    # extracts Y, checks Z" or "ran X, then took Y"). Looks like a
    # list, reads as a sequence. Demote to clause.
    action_hits = (
        len(ACTION_CHAIN_RE.findall(s))
        + len(IRREGULAR_PAST_RE.findall(s))
    )
    if action_hits >= 2:
        return "clause"
    # Fallback: chunks that don't begin with a determiner/pronoun/
    # preposition (NON_VERB_STARTERS) are likely verb-led. If 2+ of
    # the comma-separated chunks after the first start that way, it's
    # an action chain. This catches verbs the curated list misses.
    if _verb_led_chunk_count(s) >= 2:
        return "clause"
    # Colon-introduced enumeration: require 3+ chunks (2+ commas) so
    # two-item "colon: A, and B" stays clause-likely. Two-item bullets
    # feel sparse - splitting into two sentences reads better.
    if COLON_BEFORE_COMMAS_RE.search(s) and s.count(",") >= 2:
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
