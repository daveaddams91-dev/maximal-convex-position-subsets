"""Regression test: no Markdown math span may use a macro GitHub rejects.

GitHub renders math in Markdown with a hardened KaTeX configuration that rejects
a set of macros with the message

    "The following macros are not allowed: operatorname"

Stock KaTeX accepts these, so the failure only appears on github.com -- which is
how this bug reached the published README.  This test guards against it.

The test is deliberately strict and dependency-free: it greps for the forbidden
macros rather than shelling out to node, so it runs in any environment.  The
thorough KaTeX-based check lives in ``experiments/check_github_math.py``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = [
    ROOT / "README.md",
    ROOT / "RELEASE_NOTES.md",
    ROOT / "docs" / "methodology.md",
    ROOT / "docs" / "mathematical_notes.md",
]

FORBIDDEN = [
    "operatorname",
    "href",
    "url",
    "includegraphics",
]

# Custom macros defined only in paper/main.tex; they do not exist for KaTeX, so a
# README that uses them renders as an error.
UNDEFINED_CUSTOM = ["M", "CP", "HP", "conv", "hull", "vtx"]


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def strip_fenced_code(text: str) -> str:
    """Blank out ``` fenced code blocks, where ``$`` is a shell variable."""
    out = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def math_spans(text: str):
    for lineno, line in enumerate(text.splitlines(), 1):
        s = strip_inline_code(line)
        i = 0
        while i < len(s):
            if s[i] == "$":
                j = s.find("$", i + 1)
                if j < 0:
                    break
                if s[i + 1 : j].strip():
                    yield lineno, s[i + 1 : j]
                i = j + 1
            else:
                i += 1


def test_no_github_forbidden_macros() -> None:
    problems = []
    for path in MARKDOWN:
        if not path.exists():
            continue
        for lineno, math in math_spans(path.read_text(encoding="utf-8")):
            for macro in FORBIDDEN:
                if re.search(r"\\" + macro + r"\b", math):
                    problems.append(f"{path.name}:{lineno}: \\{macro} is rejected by GitHub")
    assert not problems, "GitHub would reject these math spans:\n  " + "\n  ".join(problems)


def test_no_undefined_custom_macros() -> None:
    """Macros defined only in the .tex file must not appear in Markdown."""
    problems = []
    for path in MARKDOWN:
        if not path.exists():
            continue
        for lineno, math in math_spans(path.read_text(encoding="utf-8")):
            for macro in UNDEFINED_CUSTOM:
                # \\M(P) style: a backslash, the macro, then a non-letter.
                if re.search(r"\\" + macro + r"(?![A-Za-z])", math):
                    problems.append(
                        f"{path.name}:{lineno}: \\{macro} is not defined for KaTeX"
                    )
    assert not problems, "undefined macros in Markdown math:\n  " + "\n  ".join(problems)


def test_inline_math_does_not_span_lines() -> None:
    """Inline ``$...$`` must not wrap across lines; display ``$$`` may.

    A line with an odd number of ``$`` *outside* a ``$$`` display block means an
    inline span was opened on one line and closed on another, which GitHub
    renders as literal ``$`` characters rather than as maths.
    """
    problems = []
    for path in MARKDOWN:
        if not path.exists():
            continue
        in_display = False
        for lineno, line in enumerate(
            strip_fenced_code(path.read_text(encoding="utf-8")).splitlines(), 1
        ):
            s = strip_inline_code(line).strip()
            if s.startswith("$$") and s.endswith("$$") and len(s) > 3:
                continue  # a complete display block on one line
            if s.startswith("$$"):
                in_display = not in_display
                continue
            if in_display:
                continue
            if s.count("$") % 2 != 0:
                problems.append(
                    f"{path.name}:{lineno}: odd number of '$' (inline math spans lines?)"
                )
    assert not problems, "unbalanced inline math:\n  " + "\n  ".join(problems)


if __name__ == "__main__":
    test_no_github_forbidden_macros()
    print("no GitHub-forbidden macros in Markdown math")
    test_no_undefined_custom_macros()
    print("no undefined custom macros in Markdown math")
    test_inline_math_does_not_span_lines()
    print("inline math is balanced on every line")