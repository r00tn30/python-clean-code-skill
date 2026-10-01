# Evals

Prompts for checking that the skill improves agent output without over-engineering it. Run each prompt twice in a fresh chat, once with the skill enabled and once without, and compare against the expectations.

A change to `SKILL.md` should not make any of these worse.

---

## 1. New feature in a library-style module

**Prompt:** "Add a function that calculates the total price of a shopping cart, applying a 10% discount for orders over $100 and adding $5 shipping for orders under $50."

**Expect:**
- `Decimal` for money, not `float`.
- Named constants for `100`, `10%`, `50`, `5`.
- Guard clauses or a flat structure; no nesting deeper than two levels.
- Type annotations and a docstring on the public function.

**Must not:**
- Introduce class hierarchies or strategy objects for two simple rules.
- Split two simple rules into a cluster of tiny helper functions.
- Create a test file nobody asked for.
- Add comments naming refactoring techniques.

## 2. Bug fix in existing code with its own style

**Setup:** a module using `camelCase` method names, `typing.Optional`, and no dataclasses, with an off-by-one bug in a loop.

**Prompt:** "Fix the bug where the last item is skipped."

**Expect:**
- Minimal diff that fixes the bug.
- Matches the module's existing conventions (`camelCase`, `Optional`).

**Must not:**
- Rename existing functions, convert to dataclasses, or refactor unrelated code. (It may *mention* smells it noticed.)
- Add type hints or test files beyond the fix.

## 3. Throwaway script

**Prompt:** "Write a quick script that renames all .jpeg files in a folder to .jpg."

**Expect:**
- A short, readable script using `pathlib`.
- Clear names; handles the case of a missing folder with a clear error.

**Must not:**
- Add classes, custom exceptions, protocols, value objects, or parameter objects.
- Add unrequested features such as `--dry-run` or recursion flags.
- Split the logic into more than two or three functions.

## 4. Code review

**Prompt:** "Review this code." with:

```python
def get_user(id, db, cache, log, retry=True, verbose=False):
    try:
        if id in cache:
            return cache[id]
        u = db.query("SELECT * FROM users WHERE id = %s" % id)
        if u == None:
            return -1
        cache[id] = u
        return u
    except:
        if verbose:
            log.write("error")
        return None
```

**Expect findings (roughly in this priority):**
- SQL injection via string formatting (correctness and security first).
- Bare `except` that swallows every error.
- Sentinel returns: `-1` and `None` both mean failure.
- Long Parameter List and flag arguments (`retry` is unused: Dead Code).
- Naming: `id` shadows a builtin; `u` is unclear; `== None` should be `is None`.

**Expect format:** location, smell name, why it matters, concrete fix, as specified in `SKILL.md`.

## 5. Branching on a type code

**Prompt:** "Write a function that exports a report as CSV, JSON, or PDF depending on a format argument."

**Expect:**
- An `Enum` / `StrEnum` for the format.
- A `match` statement or a dict of export functions; one function per format.

**Must not:**
- Build an abstract base class hierarchy for a single dispatch point.

## 6. Error handling around I/O

**Prompt:** "Write a function that loads a JSON config file and returns defaults if the file doesn't exist."

**Expect:**
- EAFP: `try` reading, `except FileNotFoundError` for defaults.
- Other errors (invalid JSON, permission denied) propagate or are re-raised with context (`raise ... from err`).
- Resource handled with `with` or `Path.read_text`.

**Must not:**
- `os.path.exists` pre-check followed by open (race condition).
- Catch `Exception` and silently return defaults.

## 7. Modelling a domain concept

**Prompt:** "Create a model for a bank account that supports deposits, withdrawals, and doesn't allow overdrafts."

**Expect:**
- Balance as `Decimal`; internal state prefixed with `_`, exposed read-only.
- Withdrawal raises a specific exception (e.g. `InsufficientFundsError`) with context.
- Validation of non-positive amounts.
- Tests (if asked) named by scenario and testing behavior via public methods.

## 8. Framework code

**Setup:** a FastAPI or Django project.

**Prompt:** "Add an endpoint that returns a user's orders."

**Expect:**
- Follows the framework's idioms (pydantic models / Django serializers, dependency injection, ORM querysets) over this skill's generic patterns.
- Keeps business logic out of the route handler if the project already separates it.

**Must not:**
- Change existing endpoints, error handling, or schemas beyond what the new endpoint needs (for example, converting an existing `status: str` to an enum). It may suggest these in the reply.
- Add a test suite when the project has none.

## 9. Explicit refactoring request

**Prompt:** "Refactor this to be cleaner." with:

```python
def report(orders, kind):
    out = []
    for o in orders:
        if kind == "csv":
            out.append(",".join([str(o["id"]), o["customer"], str(o["total"])]))
        elif kind == "tsv":
            out.append("\t".join([str(o["id"]), o["customer"], str(o["total"])]))
        else:
            return -1
    if kind == "csv":
        return "id,customer,total\n" + "\n".join(out)
    return "id\tcustomer\ttotal\n" + "\n".join(out)
```

**Expect:**
- Unknown format raises an exception instead of returning `-1`.
- Duplicated row-building collapsed into one place; the format becomes a separator lookup or `StrEnum`.
- Uses the `csv` module or an equivalent single code path.
- Notes that there are no tests and suggests characterization tests before or alongside the change.

**Must not:**
- Build a class hierarchy or strategy objects for two separators.
