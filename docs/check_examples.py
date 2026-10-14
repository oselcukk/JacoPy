#!/usr/bin/env python3
"""Run every Python example in the documentation.

Every fenced block whose info string is ``python`` (or ``py``) in
``docs/**/*.md`` is executed. Blocks on the same page share one
namespace and run in order, each page in a fresh interpreter, so state
never leaks from one page into another. ``text``, ``console`` and other
blocks are not run. A Python block directly preceded by the line
``<!-- no-run -->`` (blank lines in between are allowed) is skipped.

With ``--outputs``, a Python block that is directly followed by a
``text`` block must print exactly that text (trailing whitespace on
each line is ignored).

The script stops at the first failing block and exits with status 1,
naming the page and the block index (1-based, counting the page's
Python blocks, skipped ones included).

Usage::

    python docs/check_examples.py              # all pages
    python docs/check_examples.py --outputs    # also compare printed output
    python docs/check_examples.py docs/index.md docs/tutorials
"""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path

DOCS = Path(__file__).resolve().parent
ROOT = DOCS.parent

RUN_LANGS = {"python", "py"}
NO_RUN = "<!-- no-run -->"
# Paths (relative to docs/) that are never scanned.
EXCLUDE = ["_build/*", "ARCHITECTURE.md", "TESTING.md", "CITATIONS.md"]

_FENCE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


@dataclass
class Block:
    index: int  # 1-based among the page's Python blocks
    line: int  # 1-based line of the opening fence
    code: str
    skip: bool
    expected: str | None  # the following ```text block, if any


def parse_blocks(text: str) -> list[Block]:
    """Return the Python blocks of a Markdown page, in order."""
    lines = text.splitlines()
    fences: list[tuple[str, int, int, str]] = []  # (lang, open line, close line, body)
    i = 0
    while i < len(lines):
        m = _FENCE.match(lines[i])
        if not m:
            i += 1
            continue
        fence = m.group("fence")
        info = m.group("info").strip()
        lang = info.split()[0].lower() if info else ""
        start = i
        body: list[str] = []
        i += 1
        while i < len(lines):
            close = lines[i].strip()
            if close.startswith(fence[0] * len(fence)) and set(close) <= {fence[0]}:
                break
            body.append(lines[i])
            i += 1
        fences.append((lang, start, i, "\n".join(body) + "\n"))
        i += 1

    blocks: list[Block] = []
    for n, (lang, start, close, body) in enumerate(fences):
        if lang not in RUN_LANGS:
            continue
        j = start - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        skip = j >= 0 and lines[j].strip() == NO_RUN
        expected = None
        if n + 1 < len(fences) and fences[n + 1][0] == "text":
            between = lines[close + 1:fences[n + 1][1]]
            if all(not ln.strip() for ln in between):
                expected = fences[n + 1][3]
        blocks.append(Block(len(blocks) + 1, start + 1, body, skip, expected))
    return blocks


def _normalise(output: str) -> str:
    return "\n".join(ln.rstrip() for ln in output.strip("\n").splitlines())


def run_page(path: Path, compare_outputs: bool) -> dict:
    """Execute one page's blocks in this interpreter; return a result dict."""
    blocks = parse_blocks(path.read_text(encoding="utf-8"))
    namespace: dict = {"__name__": "__main__"}
    ran = skipped = 0
    for block in blocks:
        if block.skip:
            skipped += 1
            continue
        buffer = io.StringIO()
        try:
            code = compile(block.code, f"{path}:block{block.index}", "exec")
            with contextlib.redirect_stdout(buffer):
                exec(code, namespace)
        except BaseException:  # noqa: BLE001 - report everything, incl. SystemExit
            return {
                "ok": False,
                "block": block.index,
                "line": block.line,
                "error": traceback.format_exc(),
                "ran": ran,
                "skipped": skipped,
            }
        ran += 1
        if compare_outputs and block.expected is not None:
            got, want = _normalise(buffer.getvalue()), _normalise(block.expected)
            if got != want:
                return {
                    "ok": False,
                    "block": block.index,
                    "line": block.line,
                    "error": "printed output differs from the following text block\n"
                    f"--- expected\n{want}\n--- got\n{got}\n",
                    "ran": ran,
                    "skipped": skipped,
                }
    return {"ok": True, "ran": ran, "skipped": skipped}


def collect(targets: list[str]) -> list[Path]:
    paths: list[Path] = []
    for target in targets or [str(DOCS)]:
        p = Path(target).resolve()
        found = sorted(p.rglob("*.md")) if p.is_dir() else [p]
        paths.extend(found)
    result = []
    for p in paths:
        try:
            rel = p.relative_to(DOCS).as_posix()
        except ValueError:
            rel = p.name
        if any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDE):
            continue
        result.append(p)
    return list(dict.fromkeys(result))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="*", help="pages or directories (default: docs/)")
    parser.add_argument("--outputs", action="store_true",
                        help="compare printed output with a following text block")
    parser.add_argument("--timeout", type=float, default=600.0,
                        help="seconds allowed per page (default 600)")
    parser.add_argument("--_page", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args._page:  # child process: run one page, print a JSON result
        result = run_page(Path(args._page), args.outputs)
        sys.__stdout__.write("\n@@CHECK_EXAMPLES@@" + json.dumps(result) + "\n")
        return 0

    pages = collect(args.paths)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), env.get("PYTHONPATH")]))
    env.setdefault("MPLBACKEND", "Agg")
    total_ran = total_skipped = 0
    for page in pages:
        rel = page.relative_to(ROOT) if page.is_relative_to(ROOT) else page
        if not any(not b.skip for b in parse_blocks(page.read_text(encoding="utf-8"))):
            continue
        cmd = [sys.executable, str(Path(__file__).resolve()), "--_page", str(page)]
        if args.outputs:
            cmd.append("--outputs")
        with tempfile.TemporaryDirectory() as tmp:
            try:
                proc = subprocess.run(cmd, cwd=tmp, env=env, capture_output=True,
                                      text=True, timeout=args.timeout)
            except subprocess.TimeoutExpired:
                print(f"FAIL {rel}: timed out after {args.timeout:.0f} s", file=sys.stderr)
                return 1
        marker = proc.stdout.rfind("@@CHECK_EXAMPLES@@")
        if marker < 0:
            print(f"FAIL {rel}: the page runner crashed (exit {proc.returncode})\n"
                  f"{proc.stderr}", file=sys.stderr)
            return 1
        result = json.loads(proc.stdout[marker + len("@@CHECK_EXAMPLES@@"):].strip())
        if not result["ok"]:
            print(f"FAIL {rel}, block {result['block']} (line {result['line']})\n"
                  f"{result['error']}", file=sys.stderr)
            return 1
        total_ran += result["ran"]
        total_skipped += result["skipped"]
        print(f"ok   {rel}: {result['ran']} block(s) run, {result['skipped']} skipped")
    print(f"All examples passed: {total_ran} block(s) run, {total_skipped} skipped, "
          f"{len(pages)} page(s) scanned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
