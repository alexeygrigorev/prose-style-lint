# prose-style

Voice, formatting, and code-style rules for technical write-ups, plus a
mechanical checker that catches the worst offenders. Lifted out of
`aisl-workshops-raw/_docs/` so the rules can apply to any project.

## What's here

- `voice.md` - tone, voice rules, content rules (include/leave out).
- `formatting.md` - markdown mechanics: headings, code blocks, lists,
  links, asides.
- `code-style.md` - educational code style inside example blocks
  (no defensive `try/except`, no chained `.get()`, one blank line
  between definitions).
- `polish.md` - judgment-level prose patterns the script cannot detect
  (plain words over abstractions, banned-but-context-sensitive words).
- `check_style.py` - mechanical checker. Edit `BANNED_WORDS`,
  `BANNED_PHRASES`, `BANNED_OPENERS` at the top to extend the
  enforced list.

## Run the checker

Scan the current directory:

```bash
python3 ~/git/prose-style-lint/check_style.py
```

Scan one file or a specific folder:

```bash
python3 ~/git/prose-style-lint/check_style.py path/to/post.md
python3 ~/git/prose-style-lint/check_style.py docs/
```

To skip files, drop a `.prose-style-ignore` at the scan root, one
fnmatch pattern per line:

```text
# build outputs
_site/*
node_modules/*
# generated docs
docs/api/*
```

## Reading order for a write-up

1. `voice.md` while drafting.
2. `formatting.md` for any markdown syntax question.
3. `code-style.md` for example code blocks.
4. Run `check_style.py` and fix every reported finding.
5. `polish.md` for a final judgment-level pass.

## Hooking it into a project

The simplest setup is a pre-commit hook. From the target project root:

```bash
ln -s ~/git/prose-style-lint/check_style.py .git/hooks/post-add-style-check
```

Or run it from CI:

```yaml
- run: python3 ~/git/prose-style-lint/check_style.py docs/
```

## Notes on what's enforced vs. what's judgment

The script catches: bold/italic/HR/tables, em dashes, smart quotes,
bare URLs, question-word headings, deep headings, code blocks missing
language tags or running over 40 lines, consecutive code blocks, lists
or code blocks placed under a heading with no lead-in, banned tokens
and phrases (~80 entries), banned sentence openers, `-ing` participial
sentence openers, paragraphs over 5 sentences, third-person `Alexey`
references.

Everything else (tone, voice, abstractions, "explain why", source
material handling) is in the reference docs and needs a human or
agent to apply judgment.
