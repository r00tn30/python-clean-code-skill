# Python Idioms for Clean Design

Patterns to reach for when modelling. Each one is the lightest construct that does the job. Prefer the simpler option when in doubt.

## Contents

- [Value objects](#value-objects)
- [Choosing a data container](#choosing-a-data-container)
- [Interfaces: Protocol vs ABC](#interfaces-protocol-vs-abc)
- [Factory methods](#factory-methods)
- [Enums with behavior](#enums-with-behavior)
- [Strategy](#strategy)
- [Null object](#null-object)
- [Context managers](#context-managers)
- [Dependency injection without a framework](#dependency-injection-without-a-framework)
- [Module-level singletons](#module-level-singletons)
- [Patterns to avoid in Python](#patterns-to-avoid-in-python)

---

## Value objects

Small, immutable, self-validating. Equality and hashing come from the fields.

```python
import re
from dataclasses import dataclass

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if not EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email address: {self.value!r}")

    @property
    def domain(self) -> str:
        return self.value.split("@", 1)[1]
```

To normalize a field in a frozen dataclass, use `object.__setattr__(self, "value", self.value.lower())` inside `__post_init__`, or normalize in a `@classmethod` factory before construction.

## Choosing a data container

| Need | Use |
|---|---|
| Immutable record with behavior or validation | `@dataclass(frozen=True)` |
| Mutable record | `@dataclass` |
| Record that must also unpack like a tuple | `typing.NamedTuple` |
| Dict-shaped data (JSON, kwargs) that must stay a dict | `typing.TypedDict` |
| Parsing and validating untrusted external input | the project's validation library (e.g. pydantic) if it has one |
| Closed set of named values | `enum.Enum` / `enum.StrEnum` |

Add `slots=True` for memory and attribute-typo protection when you do not need `cached_property` or dynamic attributes. Add `kw_only=True` when a record has many fields of the same type.

## Interfaces: Protocol vs ABC

Use `Protocol` by default: implementations need not inherit, so it works with third-party classes and test fakes.

```python
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...
```

Use `abc.ABC` when the base class provides shared implementation, or you need `isinstance` checks against the base.

```python
from abc import ABC, abstractmethod


class Importer(ABC):
    def run(self, path: Path) -> list[Record]:
        raw = path.read_bytes()
        return [self._parse_row(row) for row in self._split_rows(raw)]

    @abstractmethod
    def _split_rows(self, raw: bytes) -> list[bytes]: ...

    @abstractmethod
    def _parse_row(self, row: bytes) -> Record: ...
```

## Factory methods

`@classmethod` constructors for alternate inputs. The primary `__init__` stays simple and always yields a valid object.

```python
@dataclass(frozen=True)
class Temperature:
    kelvin: Decimal

    def __post_init__(self) -> None:
        if self.kelvin < 0:
            raise ValueError(f"Temperature below absolute zero: {self.kelvin} K")

    @classmethod
    def from_celsius(cls, celsius: Decimal) -> "Temperature":
        return cls(kelvin=celsius + KELVIN_OFFSET)
```

## Enums with behavior

Enums can carry methods and properties, which keeps per-value rules next to the values.

```python
from decimal import Decimal
from enum import Enum


class Plan(Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"

    @property
    def monthly_price(self) -> Decimal:
        return PLAN_PRICES[self]

    @property
    def seat_limit(self) -> int | None:
        return None if self is Plan.TEAM else 1


PLAN_PRICES = {Plan.FREE: Decimal("0"), Plan.PRO: Decimal("12"), Plan.TEAM: Decimal("40")}
```

## Strategy

Behavior that varies by case, especially if it can change at runtime, goes behind a `Protocol`. For a single operation, a plain function is the simplest strategy.

```python
from decimal import Decimal
from typing import Protocol


class PricingRule(Protocol):
    def price(self, base: Decimal) -> Decimal: ...


class StandardPricing:
    def price(self, base: Decimal) -> Decimal:
        return base


class MemberPricing:
    def __init__(self, discount_rate: Decimal) -> None:
        self._discount_rate = discount_rate

    def price(self, base: Decimal) -> Decimal:
        return base * (1 - self._discount_rate)


class Checkout:
    def __init__(self, pricing: PricingRule) -> None:
        self._pricing = pricing

    def total(self, base: Decimal) -> Decimal:
        return self._pricing.price(base)
```

Function-based equivalent: `Checkout(pricing=lambda base: base * Decimal("0.9"))` with `pricing: Callable[[Decimal], Decimal]`.

## Null object

A stand-in with safe default behavior, so callers do not branch on `None`. Implement the same interface as the real object.

```python
from decimal import Decimal


class GuestCustomer:
    name = "Guest"

    def discount_rate(self) -> Decimal:
        return Decimal("0")

    def can_use_saved_cards(self) -> bool:
        return False
```

Use it only when the default really is correct for every caller. If some callers must treat "missing" differently, return `Customer | None` instead.

## Context managers

Every resource gets a `with`. Write your own with `contextlib.contextmanager` when setup and teardown belong together.

```python
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def transaction(connection: Connection) -> Iterator[Connection]:
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
```

Other stdlib helpers: `contextlib.suppress(FileNotFoundError)` for an intentionally ignored error, `ExitStack` for a variable number of resources, `tempfile.TemporaryDirectory()`.

## Dependency injection without a framework

Pass collaborators in through the constructor or as parameters; build the real ones at the edge (`main`, app factory).

```python
class ReportService:
    def __init__(self, repository: ReportRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    def generate_daily(self) -> Report:
        today = self._clock.now().date()
        return Report.from_rows(self._repository.rows_for(today))
```

Tests pass fakes that satisfy the same `Protocol`; no mocking of module globals needed.

## Module-level singletons

A module is already a singleton. When one shared instance is genuinely needed, create it lazily behind a function so tests can replace it.

```python
from functools import cache


@cache
def get_settings() -> Settings:
    return Settings.from_env()
```

Tests can call `get_settings.cache_clear()` and patch the environment.

## Patterns to avoid in Python

- **Getter/setter pairs:** use attributes; switch to `@property` when needed.
- **Builder classes:** use a dataclass with defaults and keyword-only arguments.
- **`__new__`-based singletons:** use a module or a cached factory function.
- **Deep inheritance trees:** prefer composition and Protocols.
- **Interfaces for everything:** add a Protocol when there are two implementations (counting test fakes), not before.
- **`__getattr__` proxies:** they hide the interface from type checkers and IDEs; write explicit forwarding methods.
