"""Verify every Markdown math span renders under GitHub's KaTeX configuration.

Background.  GitHub renders math in Markdown with KaTeX, but with a *hardened*
configuration: a set of macros is blacklisted, and using one produces the error

    "The following macros are not allowed: operatorname"

rather than a LaTeX error.  Stock KaTeX does accept ``\\operatorname``, so the
failure only reproduces under GitHub's settings -- which is why this project
shipped a broken README that nobody noticed until it was rendered on github.com.

This script renders each math span twice with the real KaTeX engine:

  1. with stock settings, to catch genuine syntax errors; and
  2. with GitHub's macro blacklist enforced, to reproduce the reported failure.

It requires the ``katex`` npm package (see docs/methodology.md for the one-line
install).  If node/katex are unavailable the script says so and exits 0, so it
never blocks a build.

Run:  python experiments/check_github_math.py
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile

import shutil

_RE________ = re.compile(r"`[^`]*`")


ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ["README.md", "RELEASE_NOTES.md", "docs/methodology.md", "docs/mathematical_notes.md"]

# Macros GitHub refuses.  Sourced from the observed error message plus GitHub's
# documented restrictions (external links and raw LaTeX are disabled for security).
GITHUB_FORBIDDEN = [
    "operatorname",
    "href",
    "url",
    "includegraphics",
    "input",
    "include",
]


def find_katex_dir() -> pathlib.Path | None:
    """Locate a directory containing a resolvable ``katex`` npm package."""
    candidates = [pathlib.Path(tempfile.gettempdir()) / "katex-check" / "node_modules" / "katex"]
    for base in (pathlib.Path.cwd(), ROOT):
        candidates.append(base / "node_modules" / "katex")
    env = os.environ.get("KATEX_NODE_MODULES") if (os := __import__("os")) else None
    if env:
        candidates.append(pathlib.Path(env) / "katex")
    for c in candidates:
        if (c / "package.json").exists():
            return c
    return None


def extract_spans(text: str):
    """Yield (lineno, math) for ``$...$`` spans, skipping inline code spans."""
    for lineno, line in enumerate(text.splitlines(), 1):
        # Blank out inline code so `$` inside backticks is ignored.
        s = re.sub(_RE________, lambda m: "\x00" * len(m.group(0)), line)
        i = 0
        while i < len(s):
            if s[i] == "$":
                j = s.find("$", i + 1)
                if j < 0:
                    break
                body = s[i + 1 : j]
                if body.strip():
                    yield lineno, body
                i = j + 1
            else:
                i += 1


def main() -> int:
    """Entry point — parse arguments and run the main computation.
    
    Returns:
        int: Result of type int
    
    """
    if not shutil.which("node"):
        print("node not found; skipping the KaTeX render check (not fatal)")
        return 0
    kdir = find_katex_dir()
    if kdir is None:
        print("katex npm package not found; skipping the render check (not fatal).")
        print("  install with:  mkdir -p $(mktemp -d) && cd $_ && npm i katex")
        return 0

    spans = []
    for name in FILES:
        p = ROOT / name
        if not p.exists():
            continue
        for lineno, math in extract_spans(p.read_text(encoding="utf-8")):
            spans.append((name, lineno, math))

    node_dir = kdir.parent
    script = """
const katex = require(process.argv[2]);
const payload = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const forbidden = JSON.parse(process.argv[4]);
const out = [];
for (const s of payload) {
  const used = [...s.math.matchAll(/\\\\([A-Za-z]+)/g)].map(m => m[1]);
  const bad = used.filter(u => forbidden.includes(u));
  let stockErr = null;
  try { katex.renderToString(s.math, {throwOnError: true, strict: false}); }
  catch (e) { stockErr = String(e.message).split('\\n')[0]; }
  out.push({...s, used, bad, stockErr});
}
process.stdout.write(JSON.stringify(out));
"""
    with tempfile.TemporaryDirectory() as td:
        script_path = pathlib.Path(td) / "check.js"
        script_path.write_text(script, encoding="utf-8")
        payload_path = pathlib.Path(td) / "payload.json"
        payload_path.write_text(
            json.dumps([{"file": f, "line": l, "math": m} for f, l, m in spans]),
            encoding="utf-8",
        )
        proc = subprocess.run(
            ["node", str(script_path), str(kdir), str(payload_path), json.dumps(GITHUB_FORBIDDEN)],
            capture_output=True,
            text=True,
            cwd=str(node_dir),
        )
    if proc.returncode != 0:
        print("node failed:", proc.stderr[-800:])
        return 1
    results = json.loads(proc.stdout)

    rejected = [r for r in results if r["bad"]]
    syntax = [r for r in results if r["stockErr"]]
    macros: dict[str, int] = {}
    for r in results:
        for u in r["used"]:
            macros[u] = macros.get(u, 0) + 1

    print(f"checked {len(results)} math spans with KaTeX {'' if kdir else ''}")
    print(f"macros used: {', '.join('\\\\' + m for m in sorted(macros))}")
    print()
    if rejected:
        print("REJECTED BY GITHUB:")
        for r in rejected:
            print(f"  - {r['file']}:{r['line']}: "
                  f"forbidden macro(s) {sorted(set(r['bad']))} in {r['math']!r}")
    if syntax:
        print("SYNTAX ERRORS (stock KaTeX):")
        for r in syntax:
            print(f"  - {r['file']}:{r['line']}: {r['stockErr']}\n      {r['math']!r}")
    if not rejected and not syntax:
        print("PASS: every math span renders, and no GitHub-forbidden macro is used.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())