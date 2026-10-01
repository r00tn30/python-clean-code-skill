# python-clean-code

An agent skill for writing and reviewing clean, idiomatic, modern Python (3.10+). It works with Cursor, Claude Code, and other tools that support the `SKILL.md` format.

The skill guides the agent toward clear names, focused functions, domain types instead of loose primitives, explicit error handling, and low coupling. It also tells the agent to defer to your project's existing conventions and to keep changes within the task's scope.

## Layout

```
python-clean-code/
├── SKILL.md                    # Core rules, loaded when the skill triggers
├── references/
│   ├── smells.md               # Code smells with Python-specific signs
│   ├── refactorings.md         # Refactoring techniques with examples
│   └── python-idioms.md        # Modelling patterns (value objects, protocols, dispatch...)
├── evals/
│   ├── evals.md                # Prompts and expected behavior for testing changes
│   └── results-2026-10-01.md   # Latest results: original vs rewrite vs no skill
└── tools/
    └── check_examples.py       # Compiles and lints every code example in the docs
```

`SKILL.md` stays short because it is loaded on every Python task. The agent reads the reference files only when it needs them, for example when reviewing code or working out the mechanics of a refactoring.

## Install

Copy or symlink the folder into your skills directory under the name `python-clean-code`:

```bash
# Cursor (personal, all projects)
git clone https://origin.cursor.com/r00tn30/python-clean-code-skill.git ~/.cursor/skills/python-clean-code

# Claude Code
git clone https://origin.cursor.com/r00tn30/python-clean-code-skill.git ~/.claude/skills/python-clean-code

# Shared location read by several agents
git clone https://origin.cursor.com/r00tn30/python-clean-code-skill.git ~/.agents/skills/python-clean-code
```

For a single project, use `.cursor/skills/python-clean-code/` inside the repository instead.

## How it behaves

- **Writing code:** applies the rules without commentary in the code. It scales rigor to context: full rules for libraries and services, a light touch for scripts and notebooks.
- **Editing existing code:** matches the surrounding style and project config (ruff, mypy, framework idioms) over its own preferences, and does not refactor outside the task. It may mention smells it noticed.
- **Reviewing code:** names smells, explains why each matters in context, and proposes a concrete refactoring, ordered by impact.

## Maintaining the skill

Check that every Python example in the docs compiles and passes ruff:

```bash
uv run tools/check_examples.py
```

After changing `SKILL.md`, run the prompts in `evals/evals.md` with and without the skill and confirm nothing got worse, especially the "must not" items that guard against over-engineering. Record each run in a dated `evals/results-*.md` file.

## Credits

Created by [r00tn30](https://github.com/r00tn30), whose idea it was to turn the clean-code and refactoring catalog into an agent skill.

The smell and refactoring vocabulary comes from Martin Fowler's *Refactoring* and Alexander Shvets' *Dive Into Refactoring* (refactoring.guru). The descriptions and examples here are written for modern Python.
