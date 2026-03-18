---
name: python-clean-code
description: Proactive Python clean code enforcer. Apply when writing or modifying any Python code — functions, classes, modules, or scripts. Implements 23 code smells and 70 refactoring techniques as active constraints that prevent bad code from being written in the first place. Use this whenever you're about to write Python code, not just when reviewing existing code. The skill should trigger proactively for any code generation task, including implementing new features, fixing bugs, adding tests, or refactoring. If you're writing Python, use this skill.
---

# Python Clean Code — Proactive Rules

**CRITICAL**: Apply every rule below *as you write code*. Do not wait to be asked to refactor. If generating code would violate a rule, apply the correct technique immediately.

This skill provides a comprehensive, Python-first clean-code catalog, covering:
- **23 Code Smells**: patterns that indicate poor design
- **70 Refactoring Techniques**: transformations that eliminate smells

When you write code, think about which smells you're preventing and which techniques you're applying. The goal is zero technical debt on first write.

---

## Quick Reference

Before writing any code, scan for these smells:
- **Bloaters**: Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps
- **OO Abusers**: Switch Statements, Temporary Field, Refused Bequest, Alternative Classes with Different Interfaces
- **Change Preventers**: Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies
- **Dispensables**: Comments (explaining what), Duplicate Code, Lazy Class, Data Class, Dead Code, Speculative Generality
- **Couplers**: Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man, Incomplete Library Class

Full smell catalog and technique mappings in `references/refactoring-catalog.md`.

---

## When Writing Functions

**Size and structure (prevents: Long Method, Duplicate Code)**
- Maximum ~10 lines per function. If you exceed this, stop and **Extract Method** before continuing.
- One level of abstraction per function. Orchestration functions call other functions only — no inline detail. Detail functions contain only detail — no orchestration.
- If you feel the urge to write a comment explaining what a block does, that block is a function that hasn't been written yet. **Extract Method** and name it after what it does.
- Never copy-paste code blocks. **Extract Method** immediately.

**Naming (prevents: Comments)**
- `snake_case`. Names describe *what*, not *how*. `calculate_tax()` not `do_loop()`.
- Booleans: `is_`, `has_`, `can_`, `should_` prefix. `is_expired()`, `has_permission()`.
- Commands (state-changing): imperative verbs. `save()`, `send()`, `archive()`.
- Queries (return value, no side effects): nouns or noun phrases. `total()`, `active_users()`.
- Never: `process()`, `handle()`, `do_stuff()`, `manage()`, `run()` — always be specific.
- If a name is vague, the function's responsibility is unclear. **Rename Method** or **Extract Method**.

**Parameters (prevents: Long Parameter List, Data Clumps)**
- Maximum 3 parameters. More than 3 → **Introduce Parameter Object** using `@dataclass`.
- Parameters that always travel together across multiple functions → **Introduce Parameter Object** immediately.
- Never pass a boolean flag to control branching. **Replace Parameter with Explicit Methods** — split into two named functions.
- Never pass a parameter just to branch on it with `if` inside. **Replace Parameter with Explicit Methods**.
- If extracting multiple attributes from an object to pass them, **Preserve Whole Object** — pass the whole object.
- If a parameter can be computed by a method the function already has access to, **Replace Parameter with Method Call**.

**Return values and side effects (prevents: confusion, bugs)**
- A function either changes state OR returns a value — never both. **Separate Query from Modifier** if needed.
- Never return sentinel error values (`-1`, `None` meaning "error", `False` meaning failure). **Replace Error Code with Exception** — raise a named exception.
- Never use exceptions for predictable control flow. **Replace Exception with Test** — test the condition first.

**Guard clauses (prevents: nested conditionals)**
- All `None` checks, precondition failures, and edge cases go at the top as early returns. **Replace Nested Conditional with Guard Clauses**.
- Never bury the main logic inside `else` after a guard. Return/raise in the guard, then continue with flat happy path.

**Temporary variables (prevents: Temporary Field)**
- Each variable has one purpose. Never reuse a variable name for different meanings. **Split Temporary Variable**.
- Never reassign a parameter. **Remove Assignments to Parameters** — create a local variable if you need to transform it.
- If a temp variable just holds the result of an expression used once, **Inline Temp**.
- If a computed value is used in multiple functions, **Replace Temp with Query** — extract to a `@property` or method.

**When a function is too tangled to extract**
- If local variables are so intertwined that extraction would require passing too many parameters, **Replace Method with Method Object** — convert the function to a class where locals become attributes and the function body becomes `compute()`.

**Algorithms (prevents: reinventing the wheel)**
- Before writing a custom algorithm, check Python's `itertools`, `functools`, `collections`, and builtins. If a stdlib equivalent exists, **Substitute Algorithm**.

---

## When Writing Classes

**Responsibility (prevents: Large Class, Divergent Change)**
- One class, one reason to change. State the responsibility in one sentence without "and" or "or". If you cannot, **Extract Class**.
- Do not mix business logic, persistence, and presentation in one class. **Separate Domain from Presentation**. Each concern is its own class.
- A class getting long (>150 lines) almost always has more than one responsibility. Find the seam and **Extract Class**.
- If a group of methods only uses a subset of the class's attributes, **Extract Class** — those methods belong in a separate class.

**Attributes (prevents: Data Class, Inappropriate Intimacy)**
- All internal attributes use `_` prefix. No public mutable attributes on a class that has behavior.
- Attributes set once in `__init__` and never changed → no setter. Use `@dataclass(frozen=True)` for full value objects.
- An attribute that is `None` most of the time signals the class needs to be split, or a Null Object is needed (**Temporary Field** smell, **Introduce Null Object**).
- Collection attributes are never exposed as mutable references. **Encapsulate Collection** — return `tuple(self._items)` or `types.MappingProxyType`. Provide `add_item()` / `remove_item()` methods.
- If providing access to an attribute, **Self Encapsulate Field** — use `@property` if you need lazy initialization, validation, or polymorphic override. Direct attribute access is fine for simple cases.

**Construction (prevents: complex initialization)**
- `__init__` must produce a valid object. Validate in `__init__` or `__post_init__`. An object must never exist in an invalid state.
- Complex construction or subtype selection → **Replace Constructor with Factory Method** using `@classmethod` factory (`Customer.from_dict()`, `Config.from_env()`).
- Common `__init__` code shared across subclasses → **Pull Up Constructor Body** — move to superclass `__init__`, call `super().__init__()`.

**Inheritance (prevents: Refused Bequest, Parallel Inheritance Hierarchies)**
- Only inherit when a genuine `is-a` relationship exists and Liskov Substitution holds.
- If a subclass uses only part of the parent's methods, **Replace Inheritance with Delegation** — use composition with delegation instead.
- If a subclass overrides methods with `raise NotImplementedError` or `pass`, the hierarchy is wrong (**Refused Bequest**). Fix with composition or extract a proper ABC.
- If subclasses differ only in constant-returning methods, **Replace Subclass with Fields** — collapse the hierarchy into fields on the parent.
- If two classes share common fields and methods, **Extract Superclass**.
- If a subclass is practically identical to its superclass after prior refactoring, **Collapse Hierarchy** — merge them.
- Use `typing.Protocol` instead of ABC when you do not control the implementing classes or when `isinstance` checks are not needed (**Extract Interface**).
- If adding a subclass to hierarchy A always requires adding a corresponding subclass to hierarchy B, eliminate **Parallel Inheritance Hierarchies** using **Move Method** and **Move Field**.

**When classes grow too entangled (prevents: Inappropriate Intimacy)**
- If two classes access each other's internals excessively, **Move Method** and **Move Field** to consolidate behavior where data lives.
- If a class provides too many tiny forwarding methods, **Remove Middle Man** or **Inline Class**.
- If a class does nothing but delegate, **Inline Class** entirely.

---

## When Modelling Data

**No primitive obsession (prevents: Primitive Obsession)**
- Raw `str`/`int`/`float` for domain concepts (money, email, phone, postal code, percentage, identifier) → **Replace Data Value with Object** — wrap in a `@dataclass(frozen=True)` with validation in `__post_init__`.
- A value class is small, immutable, and carries its own validation and formatting.

**No raw collections as interfaces (prevents: Primitive Obsession)**
- A `list[str]` or `dict[str, Any]` passed between functions is an unnamed class. **Replace Array with Object** — create a typed `@dataclass` or `NamedTuple`.
- A list where position 0 means one thing and position 1 means another → `@dataclass` or `NamedTuple` immediately.

**No type codes (prevents: Switch Statements)**
- No integer or string type codes (`role == 1`, `status == "PREMIUM"`).
- Closed set of named values with no behavior → **Replace Type Code with Class** using `enum.Enum`.
- Type code controls behavior and does not change after creation → **Replace Type Code with Subclasses** + `@classmethod` factory.
- Type code controls behavior and can change at runtime → **Replace Type Code with State/Strategy** — State/Strategy pattern with swappable objects.

**No magic values (prevents: confusion)**
- Every literal with non-obvious domain meaning gets a module-level `UPPER_SNAKE_CASE` constant. **Replace Magic Number with Symbolic Constant**.
- A constant's name explains *why* the value matters: `SESSION_TIMEOUT_SECONDS = 86_400`, not `EIGHTY_SIX_THOUSAND`.
- Use `enum.Enum` when constants form a closed set.

**Object identity vs value (prevents: bugs)**
- Many identical instances that should be the same object → registry + `@classmethod` factory (**Change Value to Reference**).
- A small reference object that doesn't change → `@dataclass(frozen=True)` with `__eq__`/`__hash__` (**Change Reference to Value**).

---

## When Writing Conditionals

**Simplify complex conditions (prevents: complex conditional logic)**
- A condition requiring reading to understand → **Decompose Conditional** — extract to a named function: `if is_eligible_for_discount(order):`.
- Multiple conditions leading to the same outcome → **Consolidate Conditional Expression** with `or`/`and`, extract to a named function.
- Identical code in every branch → **Consolidate Duplicate Conditional Fragments** — move it outside the conditional.
- Boolean control flags (`found = False`, `done = True`) → **Remove Control Flag** — replace with `break`, `continue`, or `return`.

**Polymorphism over conditionals (prevents: Switch Statements)**
- `if/elif` chain discriminating on object type or a type attribute → **Replace Conditional with Polymorphism**. Create subclasses, override the method, call directly.
- Type changes at runtime → **Replace Type Code with State/Strategy** — State pattern (swap the state object).
- Reserve `if/elif` for: guard clauses, simple two-outcome decisions, and purely algorithmic code.

**None handling (prevents: scattered None checks)**
- Avoid returning `None` when callers will forget to check. **Introduce Null Object** — return a Null Object, an empty collection, or annotate `Optional[T]` explicitly.
- `if x is None` scattered everywhere for the same type → Null Object subclass with safe default behavior.

**Assertions (prevents: assumption violations)**
- If a code section assumes a condition that must be true for correctness, **Introduce Assertion** with a message. Never use `assert` for input validation — use `if not condition: raise ValueError(...)`.

---

## When Managing Dependencies and Coupling

**Law of Demeter (prevents: Message Chains, Feature Envy)**
- A function calls methods only on: `self`, parameters, objects it creates, or direct component attributes.
- Never chain through intermediates: `order.customer.address.city`. **Hide Delegate** — ask the first object for what you need; let it navigate internally.

**Feature Envy (prevents: Feature Envy)**
- If a function reads or calls another object's attributes more than its own, **Move Method** to that class.

**Inappropriate Intimacy (prevents: Inappropriate Intimacy)**
- If a class accesses another's `_` or `__` attributes directly, **Move Method** or **Move Field** — move the behavior to where the data lives.

**Middle Man (prevents: Middle Man)**
- If a class does nothing but delegate every call to another object, **Remove Middle Man** or **Inline Class**.

**Shotgun Surgery (prevents: Shotgun Surgery)**
- If one logical change requires touching many unrelated classes, consolidate responsibility using **Move Method**, **Move Field**, **Inline Class**.

**Divergent Change (prevents: Divergent Change)**
- If one class must be changed for multiple unrelated reasons, **Extract Class**.

**Parallel Hierarchies (prevents: Parallel Inheritance Hierarchies)**
- If adding a subclass to A always requires a new subclass of B, consolidate using **Move Method** and **Move Field**.

**Third-party gaps (prevents: Incomplete Library Class)**
- One missing method on a third-party class → **Introduce Foreign Method** — module-level foreign function accepting the object as first parameter.
- Multiple missing methods → **Introduce Local Extension** — subclass or wrapper class with `__getattr__` delegation.

**Dependencies flow one way**
- Business logic does not import infrastructure (databases, HTTP, filesystem). Infrastructure depends on domain interfaces (Protocols or ABCs).

---

## When Dealing with Class Hierarchies

**Moving members up and down (prevents: duplication, wrong abstractions)**
- Same attribute in two subclasses → **Pull Up Attribute** to superclass.
- Same method in two subclasses → align signatures, **Pull Up Method** to superclass.
- Same `__init__` code at the start of all subclasses → **Pull Up Constructor Body** to superclass, call `super()`.
- Superclass method used by only one subclass → **Push Down Method**.
- Superclass attribute used by only some subclasses → **Push Down Attribute**.

**Template Method (prevents: duplication in algorithms)**
- Two subclasses implement the same algorithm steps in the same order, but with different details → **Form Template Method** — extract each step, pull up identical steps to the base, declare non-identical steps as `@abstractmethod`, pull up the main algorithm.

**Hierarchy manipulation**
- If you need a new subclass that varies only in a few attributes, check if **Extract Subclass** is appropriate.
- If two classes share structure but no inheritance, **Extract Superclass**.
- If you need just the interface without implementation, **Extract Interface** (use `typing.Protocol` or ABC).
- If inheritance is used for code reuse but "is-a" doesn't hold, **Replace Inheritance with Delegation**.
- If delegation is overly complex and "is-a" does hold, **Replace Delegation with Inheritance**.
- If the hierarchy has become too complex, consider **Tease Apart Inheritance** or **Extract Hierarchy**.

---

## When Handling Errors

- Use exceptions for unexpected, unrecoverable-at-this-level conditions. Use return values for expected failure cases the caller handles normally.
- Exception names describe the condition: `InsufficientFundsError` not `WithdrawError`.
- Exception messages include enough context to diagnose without reading source code.
- Catch at the layer that can meaningfully handle. Never bare `except: pass`. Never catch `Exception` at low levels.
- Every resource (file, DB connection, socket) is opened in a `with` block. No manual `close()` (**Replace Error Code with Exception**).

---

## Dispensables — Always Eliminate

- **Dead Code**: unused imports, variables, parameters, functions, classes. Delete immediately. Use `vulture` or `ruff` to find.
- **Duplicate Code**: same logic in three or more places → **Extract Method** to a single function or method. Rule of three.
- **Comments explaining what**: rewrite the code until it explains itself. Comments are for *why*, not *what*.
- **Speculative Generality**: `**kwargs` for unused extension points, abstract base hooks for unplanned features, parameters added "for future use" → YAGNI. **Remove Parameter**, **Inline Class**, **Collapse Hierarchy**.
- **Lazy Class**: a class that does too little to justify existence → **Inline Class**.
- **Data Class**: a class with only public attributes and no behavior signals missing abstractions. **Move Method** to bring behavior to the data, or accept it as a legitimate DTO if crossing boundaries.

---

## Dispensables — Comments Policy

- `# TODO(TICKET-123): reason` — acceptable with a ticket reference.
- `# TODO:` with no reference — dead weight, do not write.
- Docstrings (`"""..."""`) on public functions and classes — document what it does, what parameters mean, what it returns, what it raises. Not how it works internally.
- Never commit commented-out code.

---

## Naming Variables

- Names reveal intent. `d` → `elapsed_days`. `s` → `customer_email`. `res` → `matching_orders`.
- Single letters only for loop counters (`i`, `j`) and obvious short lambdas.
- Avoid noise words: `data_object`, `info_list`, `the_manager`. Strip the noise — what remains is the name.
- Booleans: `is_active`, `has_error`, `was_processed`. Never `flag`, `status`, `check`, `b`.

---

## Python Patterns Reference

### Immutable Value Objects
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
```
Use for domain concepts that should be immutable (money, email, coordinates, etc.).

### Interfaces and Protocols

**Use `typing.Protocol`** for structural typing (duck typing with type hints):
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
```
Best when you don't control all implementations or don't need `isinstance` checks.

**Use `ABC`** for nominal typing (explicit inheritance):
```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: float) -> bool: ...
```
Best when you need `isinstance` checks or explicit contracts.

### Factory Methods
```python
class Config:
    @classmethod
    def from_env(cls) -> 'Config':
        return cls(api_key=os.getenv('API_KEY'))

    @classmethod
    def from_file(cls, path: str) -> 'Config':
        data = json.loads(Path(path).read_text())
        return cls(**data)
```
Use for complex construction or when you need to return different subtypes.

### Enums for Type Codes
```python
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    def can_cancel(self) -> bool:
        return self in (OrderStatus.PENDING, OrderStatus.SHIPPED)
```
Enums can have methods. Never use string or int type codes.

### Properties for Encapsulation
```python
class Account:
    def __init__(self, balance: float):
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value
```
Use `@property` when you need validation, computation, or lazy loading. For simple data, direct attribute access is fine.

### Read-Only Collections
```python
from types import MappingProxyType

class Course:
    def __init__(self):
        self._students = []

    def students(self) -> tuple:
        return tuple(self._students)  # Returns immutable view

    def add_student(self, student) -> None:
        self._students.append(student)

class Registry:
    def __init__(self):
        self._items = {}

    def items(self):
        return MappingProxyType(self._items)  # Read-only dict view
```
Never expose mutable collections directly. Provide add/remove methods.

### Context Managers
```python
# Always use 'with' for resources
with open('file.txt') as f:
    data = f.read()

# Custom context manager
from contextlib import contextmanager

@contextmanager
def database_transaction():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
```
Every resource (file, connection, lock) uses `with`. No manual `close()`.

### Common Patterns

**Null Object**:
```python
class NullCustomer:
    @property
    def name(self) -> str:
        return "Guest"

    @property
    def discount(self) -> float:
        return 0.0
```
Use instead of `None` when you want safe default behavior.

**Strategy Pattern**:
```python
class PricingStrategy(Protocol):
    def calculate(self, base: float) -> float: ...

class RegularPricing:
    def calculate(self, base: float) -> float:
        return base

class PremiumPricing:
    def calculate(self, base: float) -> float:
        return base * 0.9

class Order:
    def __init__(self, pricing: PricingStrategy):
        self._pricing = pricing
```
Use Protocol for strategy interfaces. Can also use functions as strategies.

**Singleton Pattern**:
```python
# Best way: module-level instance
# database.py
class _Database:
    def __init__(self):
        self.connection = None

database = _Database()  # Singleton

# Usage: from database import database
```
Python modules are singletons. Avoid complex singleton implementations.

### Anti-Patterns to Avoid

- ❌ **Builder pattern**: Use `@dataclass` with defaults instead
- ❌ **Getter/setter everywhere**: Use direct attributes or `@property` only when needed
- ❌ **Abstract base classes for everything**: Use Protocol for most cases
- ❌ **Manual resource management**: Always use `with` statement
- ❌ **Singleton __new__ magic**: Use module-level instances

---

## Tests

- Every piece of behavior testable in isolation should be tested. Hard-to-test code is a design signal.
- Test function names describe the scenario: `test_calculate_tax_returns_zero_for_tax_exempt_customers`.
- One logical assertion per test. Testing multiple unrelated things in one test hides failures.
- Test observable behavior, not implementation details.
- Tests are code — apply all the same naming, size, and clarity rules. Use `pytest` fixtures for shared setup.

---

## General Principles

- **Rule of three**: once — fine. Twice — tolerate. Three times — **Extract Method**.
- **Leave it better**: if touching a file reveals a nearby violation of these rules, fix it.
- **YAGNI**: do not write abstractions, hooks, or parameters for requirements that do not exist yet.
- **Type annotations on all public functions**: parameters and return types. Use `from __future__ import annotations` for forward references.
- **Command-Query Separation**: a method either returns a value OR modifies state, never both.

---

## When to Consult References

For detailed explanations and code examples:
- **All smells and techniques catalog**: `references/refactoring-catalog.md`

---

## Enforcement Strategy

When writing code:
1. **Think smell-first**: Which smells am I about to create?
2. **Apply technique immediately**: Use the named refactoring to prevent it
3. **Name the technique**: Mentally note or comment which technique you applied
4. **Check the result**: Does the code still smell? If yes, apply another technique

This is not about writing perfect code on first try — it's about applying transformations consciously as you write, so the output has zero technical debt.
