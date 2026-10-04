"""Validate the LaTeX math in Markdown files against GitHub's supported subset.

GitHub renders math in Markdown with a restricted KaTeX configuration.  In
particular ``\\operatorname`` is rejected with

    "The following macros are not allowed: operatorname"

which breaks the rendering of the whole block.  This script extracts every math
span from the Markdown files, lists the macros used, and checks them against an
allowlist of commands known to be accepted by GitHub.  It also flags inline math
spanning a line break, which renders badly.

Run:  python experiments/check_markdown_math.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Commands GitHub's Markdown math renderer accepts (KaTeX subset).
ALLOWED = {
    # structure
    "frac", "dfrac", "tfrac", "binom", "dbinom", "tbinom", "sqrt", "cfrac",
    "begin", "end", "left", "right", "big", "Big", "bigg", "Bigg",
    "bigl", "bigr", "Bigl", "Bigr", "displaystyle", "limits", "substack",
    "overline", "underline", "widehat", "widetilde", "hat", "bar", "vec",
    "mathrm", "mathbf", "mathcal", "mathbb", "mathfrak", "mathsf", "mathtt",
    "mathcal", "boldsymbol", "pmb",
    # relations / logic
    "leq", "le", "geq", "ge", "neq", "ne", "approx", "sim", "simeq", "cong",
    "equiv", "propto", "prec", "preceq", "succ", "succeq", "subset", "subseteq",
    "supset", "supseteq", "in", "ni", "notin", "cup", "cap", "setminus",
    "times", "div", "pm", "mp", "cdot", "ast", "star", "circ", "bullet",
    "oplus", "otimes", "odot", "perp", "mid", "parallel", "vdash", "dashv",
    "asymp", "doteq", "ll", "gg", "bigcup", "bigcap", "bigsqcup", "bigsqcap",
    # arrows
    "to", "rightarrow", "leftarrow", "leftrightarrow", "Rightarrow", "Leftarrow",
    "Leftrightarrow", "mapsto", "longrightarrow", "longleftarrow", "Longrightarrow",
    "Longleftarrow", "Longleftrightarrow", "iff", "implies", "uparrow",
    "downarrow", "hookrightarrow", "rightharpoonup", "rightharpoondown",
    # big operators
    "sum", "prod", "coprod", "int", "iint", "iiint", "oint", "bigcup", "bigcap",
    "lim", "limsup", "liminf", "max", "min", "sup", "inf", "det", "dim", "ker",
    "deg", "gcd", "hom", "arg", "exp", "log", "ln", "sin", "cos", "tan", "cot",
    "sec", "csc", "sinh", "cosh", "tanh", "bmod",
    # delimiters / symbols
    "langle", "rangle", "lceil", "rceil", "lfloor", "rfloor", "lvert", "rvert",
    "lVert", "rVert", "vert", "Vert", "quad", "qquad", "cdots", "ldots", "dots",
    "dotsb", "dotsc", "dotsi", "dotsm", "vdots", "ddots", "ddots", "square",
    "blacksquare", "diamond", "Diamond", "triangle", "triangle", "circ", "S",
    # greek
    "alpha", "beta", "gamma", "delta", "epsilon", "varepsilon", "zeta", "eta",
    "theta", "vartheta", "iota", "kappa", "lambda", "Lambda", "mu", "nu", "xi",
    "pi", "Pi", "rho", "sigma", "Sigma", "tau", "upsilon", "phi", "varphi",
    "Phi", "chi", "psi", "Psi", "omega", "Omega", "varepsilon", "varnothing",
    "Theta", "Gamma", "Delta", "Xi", "Epsilon", "Zeta", "Eta", "Iota",
    "Kappa", "Mu", "Nu", "Rho", "Tau", "Upsilon", "Chi",
    "emptyset", "epsilon", "zeta", "aleph", "hbar", "ell", "Re", "Im", "wp",
    # text
    "text", "textbf", "textit", "textrm", "mathrm", "mathbf", "operatorname",
    "mathbb", "mathcal", "mathsf", "mathtt", "mathfrak", "mathscr", "pounds",
    "colon", "quad", "qquad", "hspace", "vspace", "newline", "linebreak",
    # spacing / misc
    "nonumber", "notag", "displaystyle", "limits", "substack", "not", "ne",
    "leavesdot", "ldotp", "cdotp", "colon", "vert", "Vert", "backslash",
}

# Commands GitHub explicitly rejects (kept separate so the message is clear).
KNOWN_REJECTED = {
    "operatorname": "KaTeX `trust`-restricted; GitHub reports 'macros are not allowed'",
    "href": "disabled by GitHub for security",
    "url": "disabled by GitHub for security",
    "includegraphics": "disabled by GitHub",
    "label": "not supported in Markdown math",
    "ref": "not supported in Markdown math",
    "cite": "not supported in Markdown math",
}

MACRO_RE = re.compile(r"\\([A-Za-z]+)")


def extract_math(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, kind, content) for each math span.  kind in {inline, display}."""
    spans: list[tuple[int, str, str]] = []
    lines = text.splitlines()
    in_display = False
    display_start = 0
    buf: list[str] = []

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if in_display:
            buf.append(line)
            if stripped.endswith("$$"):
                in_display = False
                spans.append((display_start, "display", "\n".join(buf)))
                buf = []
            continue
        # strip inline code before looking for math
        no_code = re.sub(r"`[^`]*`", "", line)
        if "$$" in no_code:
            head, _, tail = no_code.partition("$$")
            if tail.strip():
                spans.append((lineno, "display", "$$" + tail.split("$$")[0]))
            # multi-line display starting here
            rest = tail.split("$$", 1)[1] if "$$" in tail else ""
            if rest.strip() and not rest.strip().startswith("$"):
                in_display = True
                display_start = lineno
                buf = [line]
            continue
        for m in re.finditer(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", no_code):
            spans.append((lineno, "inline", m.group(1)))
    return spans


def main() -> int:
    files = sorted(
        [ROOT / "README.md", ROOT / "RELEASE_NOTES.md"]
        + list((ROOT / "docs").glob("*.md"))
    )
    files = [f for f in files if f.exists()]
    if not files:
        print("no Markdown files found")
        return 0

    problems: list[str] = []
    used: dict[str, int] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        for lineno, kind, content in extract_math(text):
            for macro in MACRO_RE.findall(content):
                used[macro] = used.get(macro, 0) + 1
                if macro in KNOWN_REJECTED:
                    problems.append(
                        f"{path.name}:{lineno}: \\{macro} is rejected by GitHub "
                        f"({KNOWN_REJECTED[macro]})"
                    )
                elif macro not in ALLOWED:
                    problems.append(
                        f"{path.name}:{lineno}: \\{macro} is not in the allowlist"
                    )
            if kind == "inline" and "\n" in content:
                problems.append(f"{path.name}:{lineno}: inline math spans a line break")

    print("macros used in Markdown math:")
    for m in sorted(used):
        print(f"  \\{m}  ({used[m]})")
    print()
    if problems:
        print("PROBLEMS:")
        seen = set()
        for p in problems:
            if p not in seen:
                print("  -", p)
                seen.add(p)
        print(f"\n{len(set(problems))} distinct problems")
        return 1
    print("no problems found: all macros are accepted by GitHub and no inline math "
          "spans a line break")
    return 0


if __name__ == "__main__":
    sys.exit(main())