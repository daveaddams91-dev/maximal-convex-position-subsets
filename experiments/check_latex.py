"""Static checks on paper/main.tex.

No LaTeX toolchain is available in this environment, so we check the things that
would break a build or that are easy to get wrong: brace/environment balance,
\\ref and \\cite targets that are never defined, \\label that is never
referenced or never defined, and stray non-ASCII characters.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TEX = Path(__file__).resolve().parents[1] / "paper" / "main.tex"


def main() -> int:
    """Entry point — parse arguments and run the main computation.
    
    Returns:
        int: Result of type int
    
    """
    src = TEX.read_text(encoding="utf-8")
    # Strip verbatim/comment content for the checks that care about structure.
    body = re.sub(r"(?m)%.*$", "", src)

    errors: list[str] = []

    # 1. Brace balance (ignoring escaped braces).
    depth = 0
    for i, ch in enumerate(body):
        if ch == "{" and (i == 0 or body[i - 1] != "\\"):
            depth += 1
        elif ch == "}" and (i == 0 or body[i - 1] != "\\"):
            depth -= 1
            if depth < 0:
                line = body[:i].count("\n") + 1
                errors.append(f"unbalanced '}}' at line ~{line}")
                break
    if depth != 0:
        errors.append(f"unbalanced braces: final depth {depth}")

    # 2. \begin/\end balance.
    begins = re.findall(r"\\begin\{([^}]+)\}", body)
    ends = re.findall(r"\\end\{([^}]+)\}", body)
    from collections import Counter

    cb, ce = Counter(begins), Counter(ends)
    for env in sorted(set(begins) | set(ends)):
        if cb[env] != ce[env]:
            errors.append(f"environment {env}: {cb[env]} begin vs {ce[env]} end")

    # 3. References and citations resolve.
    labels = set(re.findall(r"\\label\{([^}]+)\}", body))
    refs = set(re.findall(r"\\ref\{([^}]+)\}", body))
    for r in sorted(refs - labels):
        errors.append(f"\\ref{{{r}}} has no \\label")
    bibitems = set(re.findall(r"\\bibitem\{([^}]+)\}", body))
    cites: set[str] = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", body):
        cites.update(c.strip() for c in group.split(","))
    for c in sorted(cites - bibitems):
        errors.append(f"\\cite{{{c}}} has no \\bibitem")

    # 4. Non-ASCII: allowed only for the small set we declare support for.
    #    `inputenc` is set to utf8 and we list these explicitly in main.tex.
    allowed = {
        "‘", "’", "“", "”",  # quotes
        "–", "—", "…",           # dashes, ellipsis
        "é", "ö", "ü", "ñ",      # latin letters used in names
        "ć", "č", "š", "ž",
        "Č", "Š", "Ž",
    }
    for i, line in enumerate(src.splitlines(), 1):
        for ch in line:
            if ord(ch) > 127 and ch not in allowed:
                errors.append(f"unexpected non-ASCII U+{ord(ch):04X} at line {i}")

    # 5. Any cite inside a comment line would not resolve; crude check.
    if "\\bibliography{" in body:
        errors.append("uses \\bibliography but the file has an inline thebibliography")

    print(f"checked {TEX}")
    print(f"  {len(labels)} labels, {len(refs)} refs, {len(bibitems)} bibitems, {len(cites)} cites")
    if errors:
        print("\nPROBLEMS:")
        for e in errors:
            print("  -", e)
        return 1
    print("  no structural problems found")
    return 0


if __name__ == "__main__":
    sys.exit(main())