"""Compile and lint every ```python block in the skill's markdown files.

Usage: uv run tools/check_examples.py

Snippets reference names defined elsewhere in the docs (Order, Decimal, ...),
so undefined-name errors are ignored; everything else ruff reports is a failure.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
PYTHON_BLOCK = re.compile(r"^```python\n(.*?)^```", re.DOTALL | re.MULTILINE)
RUFF_ARGS = [
    "uvx", "ruff", "check",
    "--target-version", "py310",
    "--select", "E,F,W,B,UP,SIM",
    "--ignore", "F821,E501,E701",
    "--no-cache", "--quiet",
]


def extract_snippets(markdown_file: Path) -> list[tuple[int, str]]:
    text = markdown_file.read_text(encoding="utf-8")
    return [
        (text.count("\n", 0, match.start()) + 1, match.group(1))
        for match in PYTHON_BLOCK.finditer(text)
    ]


def syntax_errors(snippets: dict[Path, tuple[Path, int]]) -> list[str]:
    errors = []
    for snippet_file, (source, line) in snippets.items():
        try:
            compile(snippet_file.read_text(encoding="utf-8"), str(snippet_file), "exec")
        except SyntaxError as err:
            errors.append(f"{source.relative_to(SKILL_ROOT)}:{line}: {err.msg}")
    return errors


def _colorless_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in {"FORCE_COLOR", "CLICOLOR_FORCE"}}
    return {**env, "NO_COLOR": "1"}


def lint_errors(snippet_dir: Path, snippets: dict[Path, tuple[Path, int]]) -> list[str]:
    result = subprocess.run(
        [*RUFF_ARGS, "--output-format", "concise", str(snippet_dir)],
        capture_output=True, text=True, check=False, env=_colorless_env(),
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"ruff failed to run:\n{result.stderr}")
    errors = []
    for report in result.stdout.splitlines():
        snippet_path, _, detail = report.partition(":")
        source, line = snippets.get(Path(snippet_path), (None, 0))
        if source is not None:
            errors.append(f"{source.relative_to(SKILL_ROOT)}:{line} (block): {detail.strip()}")
    return errors


def main() -> int:
    markdown_files = sorted(SKILL_ROOT.glob("*.md")) + sorted(SKILL_ROOT.glob("references/*.md"))
    with tempfile.TemporaryDirectory() as tmp:
        snippet_dir = Path(tmp)
        snippets: dict[Path, tuple[Path, int]] = {}
        for markdown_file in markdown_files:
            for line, code in extract_snippets(markdown_file):
                snippet_file = snippet_dir / f"snippet_{len(snippets):03d}.py"
                snippet_file.write_text(code, encoding="utf-8")
                snippets[snippet_file] = (markdown_file, line)

        errors = syntax_errors(snippets) + lint_errors(snippet_dir, snippets)

    for error in errors:
        print(error)
    print(f"{len(snippets)} snippets checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
