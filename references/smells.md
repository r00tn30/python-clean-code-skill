# Code Smells — Python Catalog

A smell is a hint, not a verdict. Each entry lists how it shows up in Python, when it is *not* a problem, and the refactorings that usually fix it (mechanics in [refactorings.md](refactorings.md)).

## Contents

- Bloaters: Long Function, Large Class, Primitive Obsession, Long Parameter List, Data Clumps
- Misused abstractions: Repeated Type Switching, Temporary Field, Refused Bequest, Alternative Classes with Different Interfaces
- Change preventers: Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies
- Dispensables: What-Comments, Duplicate Knowledge, Lazy Class, Behaviorless Data Class, Dead Code, Speculative Generality
- Couplers: Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man, Incomplete Library Class
- Python-specific: Mutable Default Argument, Broad Exception Handling, Sentinel Returns, Stringly-Typed Code

---

## Bloaters

### Long Function
- **Signs:** several distinct steps separated by blank lines or what-comments; nesting 3+ deep; many local variables; hard to name without "and".
- **Not a problem when:** it is a flat, linear sequence (a CLI `main`, a data pipeline) that reads top to bottom.
- **Fix:** Extract Function, Decompose Conditional, Replace Nested Conditional with Guard Clauses, Replace Function with Command Object.

### Large Class
- **Signs:** many attributes used by disjoint subsets of methods; groups of attributes sharing a prefix (`billing_*`, `shipping_*`); hard to state its purpose in one sentence.
- **Not a problem when:** it is a framework-mandated aggregate (a Django model with many fields but little logic).
- **Fix:** Extract Class, Extract Subclass, Separate Domain from Presentation.

### Primitive Obsession
- **Signs:** `str` for emails / IDs / currency codes; `float` for money; `dict[str, Any]` passed between layers; validation of the same primitive repeated in several places.
- **Not a problem when:** the value has no rules or behavior (a display label).
- **Fix:** Replace Primitive with Value Object, Replace Type Code with Enum, Replace Dict with Dataclass.

### Long Parameter List
- **Signs:** more than ~4 positional parameters; callers passing `None` for unused positions; boolean flags.
- **Not a problem when:** parameters are keyword-only options with sensible defaults (common in public library APIs).
- **Fix:** Introduce Parameter Object, Preserve Whole Object, Make Options Keyword-Only, Replace Flag Argument with Explicit Functions.

### Data Clumps
- **Signs:** the same 2–4 values travel together through many signatures (`start, end`; `lat, lon`; `host, port, user`).
- **Fix:** Introduce Parameter Object (a frozen dataclass), then move behavior that uses the group onto it.

---

## Misused abstractions

### Repeated Type Switching
- **Signs:** the same `if/elif` or `match` on a type field (`kind == "pdf"`) appears in several functions; adding a variant means editing all of them.
- **Not a problem when:** there is one switch, in one place (a factory or a parser). A single `match` is idiomatic Python.
- **Fix:** Replace Conditional with Polymorphism, Replace Type Code with Enum + dispatch table, `functools.singledispatch`.

### Temporary Field
- **Signs:** an attribute that is `None` except during one operation; methods that check `if self._x is not None` before working.
- **Fix:** Extract Class for the operation's state, pass the value as a parameter, or Introduce Null Object.

### Refused Bequest
- **Signs:** a subclass overrides inherited methods with `raise NotImplementedError` or `pass`; it inherits to reuse code, not because it is a kind of the parent.
- **Fix:** Replace Inheritance with Delegation, Push Down Method, Extract a narrower Protocol.

### Alternative Classes with Different Interfaces
- **Signs:** two classes do the same job with different method names (`send_email` vs `dispatch_mail`), so callers cannot swap them.
- **Fix:** Rename Method to align, Extract Interface (a `Protocol`), then merge duplicated logic.

---

## Change preventers

### Divergent Change
- **Signs:** one module or class is edited for unrelated reasons (schema changes, pricing changes, UI changes all touch `order.py`).
- **Fix:** Extract Class / extract module along the axis of change.

### Shotgun Surgery
- **Signs:** one logical change requires small edits in many files (adding a field means touching serializer, validator, view, and three helpers).
- **Fix:** Move Function, Move Field, Inline Class to gather the scattered knowledge in one place.

### Parallel Inheritance Hierarchies
- **Signs:** adding a subclass to one hierarchy always requires adding one to another (`PdfExporter` ↔ `PdfRenderer`).
- **Fix:** Move Function / Move Field so one hierarchy references the other, then collapse it.

---

## Dispensables

### What-Comments
- **Signs:** comments that restate the code (`# loop over users`) or label blocks that should be functions.
- **Not a problem when:** the comment explains why: a constraint, workaround, or non-obvious decision.
- **Fix:** Extract Function named after the comment, Rename, Extract Variable.

### Duplicate Knowledge
- **Signs:** the same business rule, formula, regex, or validation in two or more places; fixing a bug requires remembering every copy.
- **Not a problem when:** code looks similar but represents independent decisions likely to diverge.
- **Fix:** Extract Function, Pull Up Method, Form Template Method, Substitute Algorithm.

### Lazy Class
- **Signs:** a class with one trivial method, or a wrapper that adds nothing; a class that only exists "for future flexibility".
- **Fix:** Inline Class (a module-level function is often enough), Collapse Hierarchy.

### Behaviorless Data Class
- **Signs:** a dataclass whose fields are manipulated by logic scattered elsewhere (`compute_total(order)`, `validate_order(order)` in other modules).
- **Not a problem when:** it is a DTO crossing a boundary (API schema, DB row, message payload).
- **Fix:** Move Function onto the class, Encapsulate Collection, make it frozen.

### Dead Code
- **Signs:** unused imports, variables, parameters, functions, branches that can never run, commented-out code.
- **Fix:** Delete it. Tools: `ruff` (F401, F841), `vulture`.

### Speculative Generality
- **Signs:** abstract base classes with one implementation; `**kwargs` or parameters nobody passes; plugin hooks without plugins.
- **Fix:** Collapse Hierarchy, Inline Class, Remove Parameter.

---

## Couplers

### Feature Envy
- **Signs:** a function mostly reads another object's attributes and calls its methods.
- **Fix:** Move Function to the object whose data it uses; Extract Function first if only part of it is envious.

### Inappropriate Intimacy
- **Signs:** code accessing another class's `_private` attributes; two classes that reach into each other constantly.
- **Fix:** Move Function, Move Field, Hide Delegate, Replace Inheritance with Delegation.

### Message Chains
- **Signs:** `order.customer._account.billing.address.city` where each hop is a behavior-rich object whose internals the caller should not know.
- **Not a problem when:** traversing plain data objects (dataclasses, parsed JSON, ORM relations used as data).
- **Fix:** Hide Delegate: ask the first object for what you need.

### Middle Man
- **Signs:** a class where most methods just forward to another object.
- **Fix:** Remove Middle Man (let callers use the delegate), or Inline Class.

### Incomplete Library Class
- **Signs:** repeated helper code around a third-party type to fill a missing feature.
- **Fix:** Introduce Foreign Function (a module-level helper taking the object first), or a small wrapper class.

---

## Python-specific

### Mutable Default Argument
- **Signs:** `def f(items=[])` or `def f(opts={})`; state leaks between calls.
- **Fix:** default to `None` and create inside, or use `dataclasses.field(default_factory=list)`.

### Broad Exception Handling
- **Signs:** bare `except:`; `except Exception: pass`; catching at a low level and returning a default that hides the failure; re-raising without `from`.
- **Fix:** catch the specific exception where it can be handled; let others propagate; `raise DomainError(...) from err`.

### Sentinel Returns
- **Signs:** returning `-1`, `False`, `""`, or `None` to mean "error"; callers forgetting to check.
- **Fix:** Replace Error Code with Exception. For a legitimate "not found", return `T | None` with an explicit annotation, or an empty collection.

### Stringly-Typed Code
- **Signs:** status, role, or mode passed as free-form strings and compared with `==` throughout; typos fail silently.
- **Fix:** Replace Type Code with Enum (`StrEnum` keeps string compatibility for serialization).
