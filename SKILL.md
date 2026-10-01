---
name: python-clean-code
description: >-
  Writes and reviews Python in a clean, idiomatic, modern (3.10+) style: clear
  names, small focused functions, domain types instead of loose primitives,
  explicit error handling, and minimal coupling. Use when writing, modifying, or
  reviewing Python code, or when the user mentions clean code, code smells,
  refactoring, or readability in Python. Defers to the project's own conventions
  and linter config; applies lightly to throwaway scripts and notebooks.
---

# Python Clean Code

## Precedence

When rules conflict, the higher item wins:

1. The user's explicit instructions.
2. The project's conventions: existing code style, `pyproject.toml`, ruff / mypy / pylint config, framework idioms (Django, FastAPI, pandas, etc.).
3. The rules in this skill.

Read nearby code before writing. Match its patterns even when this skill would choose differently.

## Scope

- Change only what the task requires. Do not refactor unrelated code; mention smells you notice instead.
- Scale rigor to context. Libraries and long-lived services get the full rules. One-off scripts, notebooks, and spikes need readable names and correct error handling, not new classes.
- Never add comments naming the refactoring you applied. Technique names belong in review feedback, not code.

## Functions

- One job per function, at one level of abstraction. If a name needs "and", split it.
- Extract a block when it has a nameable purpose or is reused, not to hit a line count. Long functions (~25+ lines) and deep nesting (3+ levels) are signals to look for seams, not hard limits.
- Do not extract single-use helpers that only move code around without naming an idea.
- Use guard clauses for preconditions and edge cases; keep the main path flat.
- More than ~4 parameters, or the same group of parameters passed around together, signals a missing type. Group related values in a dataclass; use keyword-only parameters (`*,`) for options.
- Replace a boolean flag that switches between two behaviors with two functions.
- Do not reassign parameters; bind a new name.
- Prefer stdlib (`itertools`, `functools`, `collections`, `pathlib`) and builtins over hand-rolled loops for the same job.
- Prefer functions that either return a value or change state. Python's own idioms (`list.pop`, `dict.setdefault`, iterators) are fine exceptions.

## Naming

- Names say what, not how: `overdue_invoices`, not `filtered_list`.
- Booleans read as predicates: `is_active`, `has_access`, `should_retry`.
- Functions that act are verbs (`send_invoice`); functions that compute and return may be nouns (`total_price`) or `get_`/`compute_` when it reads better.
- Avoid vague verbs (`process`, `handle`, `manage`, `do`) unless the domain uses them precisely (a request handler, a payment processor).
- Single letters only for short loop indices and trivial lambdas.
- No noise words: `data`, `info`, `obj`, `manager`, `_list` suffixes.

## Modelling data

- Domain values with rules (money, email, IDs, percentages) get a small frozen dataclass with validation in `__post_init__`. Do not wrap values that carry no rules.
- Money is `Decimal`, never `float`.
- A `dict` or `tuple` with a fixed shape that crosses function boundaries becomes a `dataclass`, `NamedTuple`, or `TypedDict` (for JSON-like data).
- Closed sets of values use `enum.Enum` / `enum.StrEnum`, not bare strings or ints.
- Literals with domain meaning become `UPPER_SNAKE_CASE` constants named for why they matter: `SESSION_TIMEOUT_SECONDS = 86_400`.
- Prefer immutable data (`frozen=True`, tuples) unless mutation is the point.
- Annotate public functions and methods. Use `X | None`, built-in generics (`list[str]`), and `typing.Self`.

## Control flow

- Name complex conditions: `if is_eligible_for_refund(order):`.
- Replace control flags (`found = False`) with `return`, `break`, or `any()` / `next()`.
- Branching on a value: use `match` or a dict of callables for simple dispatch; `functools.singledispatch` for dispatch on type; polymorphism when each variant carries its own behavior and data. Pick the lightest that fits.
- Return empty collections rather than `None` for "no results".

## Errors and resources

- Follow EAFP where it is idiomatic: `try` the operation and catch the specific exception, rather than pre-checking (`dict[key]` with `except KeyError`, opening a file with `except FileNotFoundError`).
- Raise specific exceptions for failures; define domain exceptions named for the condition (`InsufficientFundsError`).
- Never signal failure with sentinel returns (`-1`, `False`, `""`). For a normal "not found" outcome, return `T | None` and annotate it.
- Catch only what you can handle, where you can handle it. No bare `except:`; no `except Exception: pass`. Chain with `raise ... from err`.
- `assert` only for internal invariants, never for validating input.
- Every resource (file, connection, lock, temp dir) is managed with `with`.

## Classes and design

- Start with functions and modules. Introduce a class when state and behavior belong together or you need multiple implementations of one interface.
- A class has one reason to change. If methods cluster around different attributes, split it.
- Objects are valid from construction: validate in `__init__` / `__post_init__`; use `@classmethod` factories (`from_dict`, `from_env`) for alternate construction.
- Prefix internal attributes with `_`. Expose read access with plain attributes or `@property`; never return internal mutable collections (return a `tuple` or copy).
- Prefer composition over inheritance. Inherit only for a genuine is-a relationship where subclasses honor the parent's contract. A subclass that stubs out parent methods means the hierarchy is wrong.
- Use `typing.Protocol` for interfaces; use `abc.ABC` when you need shared implementation or runtime `isinstance` checks.
- A method that mostly uses another object's data belongs on that object.
- Avoid reaching through chains of internals (`a._b._c`). Chaining through public attributes of plain data objects is fine.
- Domain logic does not import infrastructure (DB, HTTP, filesystem). Pass dependencies in.
- No speculative generality: no hooks, parameters, or base classes for requirements that do not exist yet.

## Duplication, dead code, comments

- Duplicated knowledge (a business rule, formula, or validation) gets a single source immediately. Code that merely looks similar can wait until a third occurrence shows the real abstraction.
- Delete dead code: unused imports, variables, parameters, functions. Never leave commented-out code.
- Comments explain why (constraints, trade-offs, non-obvious decisions). If a comment explains what, improve the names instead.
- Public functions and classes get docstrings covering purpose, parameters, return value, and raised exceptions, in the project's docstring style.
- `TODO` only with an owner or ticket reference.

## Tests

- Test names describe the scenario and expectation: `test_refund_rejected_after_30_days`.
- Test behavior through the public interface, not private details.
- One behavior per test; use `pytest` fixtures and `parametrize` for setup and variants.
- Hard-to-test code is a design signal: usually hidden dependencies or mixed concerns.

## Reviewing code

When asked to review Python code:

1. Read [references/smells.md](references/smells.md) and identify smells by name.
2. For each finding, give the location, the smell, why it matters here, and the refactoring to apply (see [references/refactorings.md](references/refactorings.md)).
3. Order findings by impact: correctness and error handling first, then design, then naming and style.
4. Skip findings the project's linters already enforce, and do not flag patterns the project uses consistently.

Use this format:

```markdown
### <file>:<line> — <smell>
**Why it matters:** <one or two sentences, specific to this code>
**Fix:** <refactoring name> — <concrete change, with a short snippet if helpful>
```

## Before finishing

- [ ] Change stays within the task's scope.
- [ ] Matches the surrounding code's conventions.
- [ ] No sentinel error returns, bare excepts, or unmanaged resources.
- [ ] No `float` for money; no magic literals with domain meaning.
- [ ] Public APIs are annotated and documented.
- [ ] If the project has ruff / mypy configured, the changed code passes them.

## References

Read these only when needed:

- [references/smells.md](references/smells.md): catalog of code smells with Python-specific signs. Read when reviewing code or when unsure whether something is a problem.
- [references/refactorings.md](references/refactorings.md): refactoring techniques with modern Python examples. Read when you have identified a smell and need the mechanics of fixing it.
- [references/python-idioms.md](references/python-idioms.md): idiomatic patterns (value objects, protocols, factories, dispatch, context managers, null objects). Read when choosing how to model something.
