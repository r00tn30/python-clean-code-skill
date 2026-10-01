# Refactorings — Python Mechanics

Techniques for removing the smells in [smells.md](smells.md). Examples target Python 3.10+. Each refactoring should keep behavior identical. Run the tests before and after.

## Contents

- Composing functions
- Moving features between objects
- Organizing data
- Simplifying conditionals
- Simplifying calls
- Dealing with inheritance
- Large-scale refactorings
- Rarely needed (one-line summaries)

---

## Composing functions

### Extract Function
Move a block with a nameable purpose into its own function. Name it for *what* it achieves.

Before:

```python
def print_invoice(invoice):
    print(f"Invoice {invoice.number}")
    print("-" * 40)
    total = sum(line.amount for line in invoice.lines)
    print(f"Total: {total}")
```

After:

```python
def print_invoice(invoice):
    _print_header(invoice)
    print(f"Total: {invoice_total(invoice)}")


def _print_header(invoice):
    print(f"Invoice {invoice.number}")
    print("-" * 40)


def invoice_total(invoice):
    return sum(line.amount for line in invoice.lines)
```

Do not extract a block that has no better name than the code itself.

### Inline Function
The reverse: when a function's body is as clear as its name, or it only forwards a call, replace calls with the body and delete it.

### Extract Variable
Name a complex sub-expression.

```python
is_bulk_order = order.quantity >= BULK_THRESHOLD
is_returning_customer = order.customer.order_count > 0
if is_bulk_order and is_returning_customer:
    apply_loyalty_discount(order)
```

### Inline Variable
Remove a temporary that adds no meaning: `return order.total()` instead of `total = order.total(); return total`.

### Replace Temp with Query
When a temporary is computed from object state and needed in several methods, turn it into a method or `@property` (use `functools.cached_property` if it is expensive and the object is immutable).

```python
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property


@dataclass(frozen=True)
class LineItem:
    unit_price: Decimal
    quantity: int

    @cached_property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
```

`cached_property` needs an instance `__dict__`; it does not work with `slots=True`.

### Split Variable
A variable assigned twice for two different meanings gets two names.

```python
perimeter = 2 * (height + width)
area = height * width
```

### Remove Assignments to Parameters
Bind a new name instead of reassigning a parameter.

```python
def discounted(price: Decimal, rate: Decimal) -> Decimal:
    result = price * (1 - rate)
    return result.quantize(Decimal("0.01"))
```

### Replace Function with Command Object
When a long function's locals are so intertwined that extraction would need many parameters, turn it into a class: locals become attributes, the body becomes small methods, and a single public method (`run()` or a domain verb) drives them. Use sparingly; first try Extract Function with a dataclass holding the shared state.

### Substitute Algorithm
Replace a hand-written algorithm with a clearer one, usually from the stdlib.

Before:

```python
def most_common_word(words):
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    best, best_count = None, 0
    for word, count in counts.items():
        if count > best_count:
            best, best_count = word, count
    return best
```

After:

```python
from collections import Counter


def most_common_word(words: list[str]) -> str | None:
    most_common = Counter(words).most_common(1)
    return most_common[0][0] if most_common else None
```

---

## Moving features between objects

### Move Function
Move a function or method to the class or module whose data it uses most. Leave a forwarding call only if external callers depend on the old location.

Before (`Invoice` reaches into `Customer`):

```python
class Invoice:
    def late_fee(self) -> Decimal:
        if self.customer.tier is Tier.GOLD and self.customer.years_active > 5:
            return Decimal("0")
        return LATE_FEE
```

After:

```python
class Customer:
    def is_exempt_from_late_fees(self) -> bool:
        return self.tier is Tier.GOLD and self.years_active > LOYALTY_YEARS


class Invoice:
    def late_fee(self) -> Decimal:
        return Decimal("0") if self.customer.is_exempt_from_late_fees() else LATE_FEE
```

### Move Field
Move an attribute to the class that uses it most, updating access through the new owner.

### Extract Class
Split out a cohesive group of attributes and the methods that use them.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    number: str

    def formatted(self) -> str:
        return f"+{self.country_code} {self.number}"


@dataclass
class Person:
    name: str
    phone: PhoneNumber
```

### Inline Class
The reverse: fold a class that no longer earns its keep into its only user, or replace it with a module-level function.

### Hide Delegate
Give the first object a method so callers stop navigating its internals: `person.manager()` instead of `person._department.manager`. Only worth it when the intermediate object is an implementation detail.

### Remove Middle Man
The reverse: when a class only forwards calls, let callers use the delegate directly.

### Introduce Foreign Function
Add a missing operation for a type you cannot modify as a module-level function taking the object first.

```python
from datetime import date, timedelta


def next_business_day(day: date) -> date:
    following = day + timedelta(days=1)
    while following.weekday() >= 5:
        following += timedelta(days=1)
    return following
```

For several missing operations, write a small wrapper class that holds the third-party object. Avoid `__getattr__`-based proxies; they hide the interface from type checkers.

---

## Organizing data

### Replace Primitive with Value Object
Wrap a primitive that carries rules in a small frozen dataclass that validates itself.

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Money amount cannot be negative: {self.amount}")
        if len(self.currency) != 3:
            raise ValueError(f"Currency must be an ISO 4217 code: {self.currency!r}")

    def add(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError(f"Cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)
```

Use `Decimal` for money. Construct from strings (`Decimal("19.99")`), not floats.

### Replace Dict with Dataclass
A fixed-shape `dict` or positional `tuple` passed between functions becomes a named type.

Before:

```python
def make_user(row):
    return {"id": row[0], "email": row[1], "is_admin": row[2] == 1}
```

After:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    email: str
    is_admin: bool

    @classmethod
    def from_row(cls, row: tuple[int, str, int]) -> "User":
        user_id, email, admin_flag = row
        return cls(id=user_id, email=email, is_admin=admin_flag == 1)
```

Use `TypedDict` when the data must stay a dict (JSON payloads, kwargs), and `NamedTuple` when tuple unpacking is part of the interface.

### Replace Type Code with Enum
Replace string or int codes with an enum. `StrEnum` keeps values usable as strings for serialization.

```python
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

    @property
    def is_cancellable(self) -> bool:
        return self is OrderStatus.PENDING
```

### Replace Type Code with Polymorphism / Strategy
When the code drives behavior in several places, give each variant its own object. If the variant can change at runtime, hold it as a swappable strategy attribute rather than a subclass (see [python-idioms.md](python-idioms.md#strategy)).

### Replace Magic Literal with Constant
Give literals with domain meaning a module-level name that explains why the value matters.

```python
MAX_LOGIN_ATTEMPTS = 5
PASSWORD_RESET_TTL = timedelta(hours=1)
```

### Encapsulate Collection
Never hand out the internal mutable collection. Return an immutable copy and provide intent-revealing mutators.

```python
class Course:
    def __init__(self) -> None:
        self._students: list[str] = []

    @property
    def students(self) -> tuple[str, ...]:
        return tuple(self._students)

    def enroll(self, student: str) -> None:
        if student in self._students:
            raise ValueError(f"{student} is already enrolled")
        self._students.append(student)
```

For dicts, `types.MappingProxyType(self._items)` gives a read-only live view.

### Encapsulate Field
Start with a plain attribute. Switch to `@property` only when you need validation, computation, or a read-only view. Callers do not change, so there is no need for getters "just in case".

### Change Value to Reference
When many copies of the same entity must stay in sync (one `Customer` per ID), load instances through a repository or identity map instead of constructing duplicates.

### Change Reference to Value
When a small object is immutable and compared by content (currency, date range), make it a frozen dataclass so equality and hashing are by value.

---

## Simplifying conditionals

### Replace Nested Conditional with Guard Clauses

Before:

```python
def shipping_cost(order):
    if order is not None:
        if order.items:
            if order.total < FREE_SHIPPING_THRESHOLD:
                return STANDARD_SHIPPING
            else:
                return Decimal("0")
        else:
            raise ValueError("Order has no items")
    else:
        raise ValueError("Order is required")
```

After:

```python
def shipping_cost(order: Order) -> Decimal:
    if not order.items:
        raise ValueError("Order has no items")
    if order.total >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0")
    return STANDARD_SHIPPING
```

With a type-annotated, non-optional parameter, the `None` check is unnecessary; the type checker enforces it.

### Decompose Conditional
Extract a complex condition and its branches into named functions: `if is_peak_season(day): rate = peak_rate(...)`.

### Consolidate Conditional Expression
Several checks with the same outcome become one named predicate.

```python
def is_ineligible_for_loan(applicant: Applicant) -> bool:
    return (
        applicant.age < MINIMUM_AGE
        or applicant.credit_score < MINIMUM_CREDIT_SCORE
        or applicant.has_active_default
    )
```

### Consolidate Duplicate Conditional Fragments
Move code repeated in every branch outside the conditional.

### Remove Control Flag
Replace a "found"/"done" flag with `return`, `break`, `any()`, or `next()`.

```python
def has_overdue_invoice(invoices: list[Invoice]) -> bool:
    return any(invoice.is_overdue for invoice in invoices)


def first_admin(users: list[User]) -> User | None:
    return next((user for user in users if user.is_admin), None)
```

### Replace Conditional with Dispatch
Pick the lightest tool that fits:

`match` for a single, local decision on structure or value:

```python
def describe(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at {x},{y}"
        case {"type": "key", "key": key}:
            return f"key {key}"
        case _:
            raise ValueError(f"Unknown event: {event!r}")
```

A dict of callables when variants are data-driven:

```python
EXPORTERS: dict[ExportFormat, Callable[[Report], bytes]] = {
    ExportFormat.CSV: export_csv,
    ExportFormat.PDF: export_pdf,
}


def export(report: Report, fmt: ExportFormat) -> bytes:
    return EXPORTERS[fmt](report)
```

`functools.singledispatch` when behavior depends on the argument's type and you cannot add methods to those types:

```python
from functools import singledispatch


@singledispatch
def to_json(value: object) -> object:
    raise TypeError(f"Cannot serialize {type(value).__name__}")


@to_json.register
def _(value: Decimal) -> str:
    return str(value)


@to_json.register
def _(value: date) -> str:
    return value.isoformat()
```

### Replace Conditional with Polymorphism
When the same switch on a type code repeats across functions and each variant carries its own data and behavior, give each variant a class implementing a shared `Protocol`, and let callers call the method. See [python-idioms.md](python-idioms.md#strategy).

### Introduce Null Object
When callers repeatedly check `if x is None` and then fall back to the same default, return an object with that default behavior instead. See [python-idioms.md](python-idioms.md#null-object). Only do this when the default is genuinely safe; otherwise keep `T | None` and let the type checker force the check.

### Introduce Assertion
Document an internal invariant the code relies on: `assert total >= 0, "line totals are never negative"`. Never use `assert` to validate input. It is stripped under `python -O`.

---

## Simplifying calls

### Rename Function / Variable
Rename for intent. Update all callers in one change; for public APIs, keep a deprecated alias for a release.

### Introduce Parameter Object
Group parameters that travel together into a frozen dataclass.

```python
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError(f"end {self.end} is before start {self.start}")

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


def revenue_between(orders: list[Order], period: DateRange) -> Decimal:
    return sum(
        (order.total for order in orders if period.contains(order.placed_on)),
        Decimal("0"),
    )
```

### Make Options Keyword-Only
Parameters that tune behavior go after `*`, so call sites are self-describing and the order can change safely.

```python
def fetch(url: str, *, timeout: float = 10.0, retries: int = 3) -> bytes: ...
```

### Replace Flag Argument with Explicit Functions

Before:

```python
def render(report, as_pdf):
    ...
```

After:

```python
def render_html(report: Report) -> str: ...


def render_pdf(report: Report) -> bytes: ...
```

### Preserve Whole Object
Pass the object rather than several values pulled out of it, unless that would couple the callee to a type it should not know about.

### Replace Parameter with Query
Drop a parameter the function can compute from data it already has.

### Separate Query from Modifier
Split a function that both returns a value and changes state into two, unless combining them is the point (atomic `pop`, `get_or_create`, iterator `next`).

### Replace Constructor with Factory Method
Use `@classmethod` constructors for alternate inputs, validation-heavy construction, or choosing a subtype.

```python
import os
from dataclasses import dataclass


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    api_key: str
    timeout_seconds: float

    @classmethod
    def from_env(cls) -> "Config":
        try:
            api_key = os.environ["API_KEY"]
        except KeyError as err:
            raise ConfigError("API_KEY environment variable is not set") from err
        return cls(api_key=api_key, timeout_seconds=float(os.environ.get("TIMEOUT", "10")))
```

### Replace Error Code with Exception

Before:

```python
def withdraw(account, amount):
    if amount > account.balance:
        return -1
    account.balance -= amount
    return 0
```

After:

```python
class InsufficientFundsError(Exception):
    def __init__(self, balance: Decimal, requested: Decimal) -> None:
        super().__init__(f"Requested {requested}, but balance is {balance}")
        self.balance = balance
        self.requested = requested


class Account:
    def __init__(self, balance: Decimal) -> None:
        self._balance = balance

    @property
    def balance(self) -> Decimal:
        return self._balance

    def withdraw(self, amount: Decimal) -> None:
        if amount > self._balance:
            raise InsufficientFundsError(self._balance, amount)
        self._balance -= amount
```

The check and the state change now live together on `Account` (Move Function), so callers cannot bypass the rule.

### Prefer EAFP over Look-Before-You-Leap
Python favors trying the operation and handling the specific failure. It avoids race conditions and double lookups.

```python
def load_settings(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    return json.loads(text)
```

Use a pre-check instead only when the check is cheap, clearly expresses intent, and failure is the common case (`if not items: return`).

### Remove Setter / Hide Method
Make attributes that should not change after construction read-only (frozen dataclass or property without setter). Prefix methods only used internally with `_`.

---

## Dealing with inheritance

### Replace Inheritance with Delegation
When a subclass uses only part of its parent, or inherits just to reuse code, hold an instance instead.

Before:

```python
class Stack(list):
    def push(self, item):
        self.append(item)
```

After:

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        try:
            return self._items.pop()
        except IndexError:
            raise IndexError("pop from empty Stack") from None

    def __len__(self) -> int:
        return len(self._items)
```

### Extract Interface
Define a `Protocol` describing what callers need; implementations do not have to inherit from it.

```python
from typing import Protocol


class Notifier(Protocol):
    def notify(self, recipient: str, message: str) -> None: ...
```

### Pull Up / Push Down
- **Pull Up Method / Field / Constructor Body:** move identical code from sibling subclasses into the parent.
- **Push Down Method / Field:** move parent members used by only one subclass into that subclass.

### Extract Superclass
Two classes with shared fields and behavior get a common parent. Consider composition first, since a shared helper object often fits better.

### Collapse Hierarchy
Merge a subclass that no longer differs meaningfully from its parent.

### Form Template Method
When subclasses run the same steps in the same order with different details, put the sequence in the base class and make the varying steps abstract methods. In Python, passing the varying steps as functions is often simpler.

### Replace Subclass with Fields
Subclasses that differ only in constant values collapse into one class with fields (often an enum field).

---

## Large-scale refactorings

- **Separate Domain from Presentation:** move business rules out of views, CLI handlers, and templates into plain modules the UI calls.
- **Tease Apart Inheritance:** a hierarchy doing two jobs (e.g. format × storage) becomes two hierarchies joined by composition.
- **Convert Procedural Design to Objects:** only when data and the functions operating on it are clearly coupled; well-organized modules of functions are idiomatic Python.
- **Extract Hierarchy:** a class full of conditionals for many special cases becomes a base class plus subclasses (or a dispatch table) per case.

---

## Rarely needed (one-line summaries)

- **Add / Remove Parameter:** change a signature; remove parameters nobody uses.
- **Parameterize Function:** merge near-identical functions that differ only in a literal into one with a parameter.
- **Duplicate Observed Data:** keep domain data out of UI objects and sync via callbacks or events.
- **Change Unidirectional Association to Bidirectional / Bidirectional to Unidirectional:** add or remove a back-reference; prefer unidirectional unless both sides genuinely navigate.
- **Replace Delegation with Inheritance:** only when the class delegates its entire interface and is truly a kind of the delegate.
- **Extract Subclass:** move features used only by some instances into a subclass. Prefer composition or a field when possible.
- **Self Encapsulate Field:** in Python, use direct attribute access and switch to `@property` later if needed.
