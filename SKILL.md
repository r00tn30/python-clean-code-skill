---
name: python-clean-code
description: >-
  Writes and reviews Python in a clean, idiomatic, modern (3.10+) style while
  keeping changes proportional to the task. Use when writing, modifying, or
  reviewing Python code, or when the user mentions clean code, code smells,
  refactoring, or readability in Python. Defers to the project's own conventions
  and linter config; applies lightly to throwaway scripts and notebooks.
---

# Python Clean Code

## Precedence

When rules conflict, the higher item wins:

1. The user's explicit instructions.
2. The project's conventions: existing code style, `pyproject.toml`, ruff / mypy config, framework idioms (Django, FastAPI, pandas, etc.).
3. The rules in this skill.

Read nearby code before writing. Match its patterns even when this skill would choose differently.

## Keep changes proportional

Over-engineering is the most common way clean-code guidance makes output worse. Before finishing, check the change against these limits:

- **Stay in scope.** Change only what the task requires. Do not rename, restructure, or "improve" surrounding code; mention problems you noticed in your reply instead.
- **No unrequested features.** No extra CLI flags, options, config, or abstractions the user did not ask for.
- **Tests follow the project.** Add or update tests when the project already has tests for that code, or when asked. Do not create new test suites or frameworks unprompted.
- **Scale to context.** Libraries and services get the full rules. Scripts, notebooks, and spikes need clear names and correct error handling, and nothing more: no custom exception classes, value objects, or class hierarchies.
- **Don't fragment.** Extract a function when it names an idea or removes duplication, not to shorten a function that already reads clearly top to bottom. A short function with two `if` statements does not need four helpers.
- **One lightweight construct.** For branching, prefer a `match` or a dict of functions over a class hierarchy; for data, a dataclass over a custom type system. Add abstraction only when a second real use exists.

## Defaults for new code

Apply these where the project has no convention of its own:

- Names say what, not how. Booleans read as predicates (`is_active`). Avoid vague verbs (`process`, `handle`) unless the domain uses them precisely.
- Guard clauses for preconditions; keep the main path flat.
- More than ~4 parameters, or a group passed around together, signals a missing dataclass. Options go after `*` as keyword-only.
- Money is `Decimal` (constructed from strings), never `float`.
- Literals with domain meaning become `UPPER_SNAKE_CASE` constants; closed sets of values become `Enum` / `StrEnum`.
- Fixed-shape dicts crossing function boundaries become a `dataclass`, `NamedTuple`, or `TypedDict`.
- Annotate public functions; use `X | None` and built-in generics. Public functions and classes get a docstring that lists raised exceptions.
- Errors: EAFP (`try` the operation, catch the specific exception) rather than pre-checking, e.g. `except FileNotFoundError` instead of `if path.exists()`. Raise specific exceptions, chain with `raise ... from err`, never return sentinels (`-1`, `False`) for failure. No bare `except:` or silent `except Exception`.
- Every resource goes in a `with`.
- Prefer functions and modules; use a class when state and behavior belong together. Composition over inheritance; `typing.Protocol` for interfaces.
- Keep domain logic free of infrastructure imports; pass dependencies in.
- Comments explain why, never what. Never add comments naming refactorings you applied.

## Reviewing code

When asked to review Python code:

1. Read [references/smells.md](references/smells.md) and identify smells by name.
2. For each finding give the location, the smell, why it matters in this code, and the fix (mechanics in [references/refactorings.md](references/refactorings.md)).
3. Order by impact: security and correctness first, then error handling, then design, then naming and style.
4. Skip what the project's linters already enforce and patterns the project uses consistently.
5. Keep it tight: one short paragraph per finding. A suggested rewrite is optional; include it only when it clarifies several findings at once.

Use this format:

```markdown
### <file>:<line> — <smell>
**Why it matters:** <one or two sentences, specific to this code>
**Fix:** <refactoring name> — <concrete change, with a short snippet if helpful>
```

## Refactoring on request

When the user asks to refactor or clean up code (not merely to change it):

1. Identify smells with [references/smells.md](references/smells.md); fix the highest-impact ones first.
2. Apply refactorings from [references/refactorings.md](references/refactorings.md) in small, behavior-preserving steps.
3. Run the existing tests before and after. If there are none, say so and suggest adding characterization tests first.

## Before finishing

- [ ] The diff contains only what the task needs: no unrequested features, flags, tests, or refactors.
- [ ] Matches the surrounding code's conventions.
- [ ] No sentinel error returns, bare excepts, unmanaged resources, or `float` money.
- [ ] If ruff / mypy are configured, the changed code passes them.

## References

Read these only when needed:

- [references/smells.md](references/smells.md): code smells with Python-specific signs and "not a problem when" notes. Read when reviewing or refactoring.
- [references/refactorings.md](references/refactorings.md): refactoring mechanics with modern Python examples. Read when applying a fix.
- [references/python-idioms.md](references/python-idioms.md): modelling patterns (value objects, protocols, factories, dispatch, null objects, context managers). Read when choosing how to model something non-trivial.
