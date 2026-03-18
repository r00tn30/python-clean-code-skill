# Python Clean Code Quick Reference

## 23 Code Smells — Visual Guide

### 🔴 Bloaters
Code elements that have grown too large

| Smell | Signs | Threshold | Quick Fix |
|-------|-------|-----------|-----------|
| **Long Method** | Too many lines | >10 lines | Extract Method |
| **Large Class** | Too many methods/attributes | >150 lines, >10 methods | Extract Class |
| **Primitive Obsession** | Using str/int for domain concepts | Domain data as primitives | Replace Data Value with Object |
| **Long Parameter List** | Too many parameters | >3 parameters | Introduce Parameter Object |
| **Data Clumps** | Same parameters everywhere | 3+ params traveling together | Introduce Parameter Object |

### 🟠 Object-Orientation Abusers
Incorrect application of OOP principles

| Smell | Signs | Quick Fix |
|-------|-------|-----------|
| **Switch Statements** | Type code + if/elif chains | Replace Conditional with Polymorphism |
| **Temporary Field** | Attribute only used sometimes | Extract Class, Introduce Null Object |
| **Refused Bequest** | Subclass rejects parent methods | Replace Inheritance with Delegation |
| **Alternative Classes with Different Interfaces** | Similar classes, different names | Rename Method, Extract Interface |

### 🟡 Change Preventers
Making changes requires touching many places

| Smell | Signs | Quick Fix |
|-------|-------|-----------|
| **Divergent Change** | One class changes for multiple reasons | Extract Class |
| **Shotgun Surgery** | One change touches many classes | Move Method, Inline Class |
| **Parallel Inheritance Hierarchies** | Adding subclass A requires subclass B | Move Method, Move Field |

### 🟢 Dispensables
Something unnecessary that should be removed

| Smell | Signs | Quick Fix |
|-------|-------|-----------|
| **Comments** | Explaining *what*, not *why* | Extract Method, Rename |
| **Duplicate Code** | Same logic in 3+ places | Extract Method |
| **Lazy Class** | Class does too little | Inline Class |
| **Data Class** | Only attributes, no behavior | Move Method |
| **Dead Code** | Unused code | Delete it |
| **Speculative Generality** | Hooks for future features | Remove Parameter, Collapse Hierarchy |

### 🔵 Couplers
Excessive coupling between classes

| Smell | Signs | Quick Fix |
|-------|-------|-----------|
| **Feature Envy** | Method uses another class's data more | Move Method |
| **Inappropriate Intimacy** | Class accesses another's internals | Move Method, Hide Delegate |
| **Message Chains** | `a.b.c.d.e` | Hide Delegate |
| **Middle Man** | Class just forwards calls | Remove Middle Man, Inline Class |
| **Incomplete Library Class** | Third-party missing methods | Introduce Foreign Method |

---

## 70 Refactoring Techniques — Cheat Sheet

### 🔨 Composing Methods (9)

```python
# Extract Method
def process():
    validate()  # Extracted
    transform()  # Extracted

# Inline Method
return age >= 18  # Instead of calling is_adult()

# Extract Variable
is_valid = condition1 and condition2
if is_valid: ...

# Inline Temp
return order.price()  # Instead of temp = order.price(); return temp

# Replace Temp with Query
def price(): return base * (1 + tax)  # Called multiple times instead of temp

# Split Temporary Variable
perimeter = 2 * (h + w)  # Not reusing 'temp'
area = h * w

# Remove Assignments to Parameters
result = price; result *= 0.9  # Don't reassign 'price'

# Replace Method with Method Object
class Calculator:  # When too many temps to extract
    def compute(self): ...

# Substitute Algorithm
return max(items)  # Instead of manual loop
```

### 🚚 Moving Features (8)

```python
# Move Method
class Customer:
    def invoice_priority(self): ...  # Moved from Invoice

# Move Field
class AccountType:
    interest_rate = 0.05  # Moved from Account

# Extract Class
class TelephoneNumber:  # Split from Person
    area_code: str
    number: str

# Inline Class
class Person:
    street: str  # Address inlined

# Hide Delegate
person.manager()  # Instead of person.department.manager

# Remove Middle Man
person.department.manager()  # Expose delegate

# Introduce Foreign Method
def next_day(date): return date + timedelta(days=1)

# Introduce Local Extension
class ExtendedDate(ThirdPartyDate): ...
```

### 📊 Organizing Data (16)

```python
# Self Encapsulate Field
@property
def price(self): return self._price

# Replace Data Value with Object
@dataclass(frozen=True)
class EmailAddress:
    value: str

# Change Value to Reference
CustomerRegistry.get("Alice")  # Singleton

# Change Reference to Value
@dataclass(frozen=True)
class Currency: ...  # Immutable value

# Replace Array with Object
@dataclass
class Employee:
    name: str
    age: int  # Not row[0], row[1]

# Duplicate Observed Data
order.add_observer(window)  # Separate domain from UI

# Change Unidirectional to Bidirectional
customer.orders  # Both know each other

# Change Bidirectional to Unidirectional
# Remove order.customer if not needed

# Replace Magic Number with Symbolic Constant
SPEED_OF_LIGHT = 299_792_458

# Encapsulate Field
@property
def name(self): return self._name

# Encapsulate Collection
return tuple(self._items)  # Read-only

# Replace Type Code with Class
class BloodType(Enum): ...

# Replace Type Code with Subclasses
class Engineer(Employee): ...

# Replace Type Code with State/Strategy
player.set_state(BoostedState())

# Replace Subclass with Fields
Person(gender="M")  # Not Male(Person)

# Extract Interface
class Payable(Protocol): ...
```

### 🔀 Simplifying Conditionals (9)

```python
# Decompose Conditional
if is_summer(date):
    charge = summer_charge()

# Consolidate Conditional Expression
if is_not_eligible():
    return 0

# Consolidate Duplicate Fragments
if special: total = p * 0.95
else: total = p * 0.98
send_order()  # Moved outside

# Remove Control Flag
for item in items:
    if item.name == target:
        return item  # No 'found' flag

# Replace Nested Conditional with Guard Clauses
if is_dead: return dead_amount()
if is_separated: return separated_amount()
return normal_amount()

# Replace Conditional with Polymorphism
customer.calculate_price()  # Polymorphic

# Introduce Null Object
class NullCustomer:
    plan = "basic"

# Introduce Assertion
assert price >= 0, "Price must be non-negative"

# Replace Exception with Test
if not stack.is_empty():
    stack.pop()
```

### 📞 Simplifying Method Calls (13)

```python
# Rename Method
invoice_credit_total()  # Not get_inv_cdttl()

# Add Parameter
contact_customer(method="email")

# Remove Parameter
calculate_total(items, tax)  # Removed unused param

# Separate Query from Modifier
has_permission()  # Query
send_data()  # Modifier

# Parameterize Method
increase_by(value, 10)  # Not increase_by_ten()

# Replace Parameter with Explicit Methods
set_height(10)  # Not set_value("height", 10)

# Preserve Whole Object
plan.within_range(weather)  # Not (low, high)

# Replace Parameter with Method Call
discounted_price(base)  # Calculates discount internally

# Introduce Parameter Object
@dataclass
class UserData: ...

# Remove Setting Method
# No @id.setter for immutable ID

# Hide Method
def _internal_helper(): ...  # Private

# Replace Constructor with Factory Method
@classmethod
def create_engineer(cls): ...

# Replace Error Code with Exception
raise InsufficientFundsError()

# Replace Exception with Test
if not empty: pop()  # Not try/except
```

### 🏗️ Dealing with Generalization (15)

```python
# Pull Up Field
class Employee:
    name: str  # From Engineer, Manager

# Pull Up Method
class Employee:
    def full_name(self): ...  # From subclasses

# Pull Up Constructor Body
super().__init__(name)

# Push Down Method
class Engineer:
    def specialized_task(): ...  # Only in Engineer

# Push Down Field
class Engineer:
    certification: str  # Only in Engineer

# Extract Subclass
class LaborItem(JobItem): ...

# Extract Superclass
class Party:  # Common to Employee, Department
    name: str

# Extract Interface
class Payable(Protocol): ...

# Collapse Hierarchy
class Employee: pass  # Inline Salesman

# Form Template Method
class Site(ABC):
    def billing_amount(self):
        return self._base() + self._tax()

# Replace Inheritance with Delegation
class Stack:
    def __init__(self):
        self._items = []  # Not Stack(list)

# Replace Delegation with Inheritance
class Manager(Employee): ...  # Was delegation

# Tease Apart Inheritance
class Deal:
    def __init__(self, presentation): ...  # Composition

# Convert Procedural to Objects
class Order:
    def total(self): ...  # Was function

# Separate Domain from Presentation
class Order:  # Pure domain
class OrderWindow:  # UI
```

---

## Decision Tree: Which Refactoring to Use?

```
Is the code TOO LONG?
├─ Function → Extract Method
├─ Class → Extract Class
└─ Parameter list → Introduce Parameter Object

Is the code DUPLICATED?
├─ In same class → Extract Method
├─ In sibling classes → Pull Up Method
└─ Across classes → Extract Superclass

Is the code HARD TO UNDERSTAND?
├─ Complex condition → Decompose Conditional
├─ Many conditions → Replace Conditional with Polymorphism
└─ Confusing names → Rename Method

Is the code TIGHTLY COUPLED?
├─ Message chains → Hide Delegate
├─ Feature envy → Move Method
└─ Inappropriate intimacy → Move Field

Is the code DOING NOTHING?
├─ Dead code → Delete
├─ Lazy class → Inline Class
└─ Unused parameter → Remove Parameter

Is the code USING PRIMITIVES?
├─ Domain concept → Replace Data Value with Object
├─ Type code → Replace Type Code with Class/Subclasses
└─ Magic number → Replace with Symbolic Constant

Is inheritance WRONG?
├─ Refused bequest → Replace Inheritance with Delegation
├─ Type code → Replace Type Code with Subclasses
└─ Too similar → Collapse Hierarchy
```

---

## Python-Specific Patterns

### ✅ Use These

```python
# Dataclasses for value objects
@dataclass(frozen=True)
class Money: ...

# Properties for computed/validated access
@property
def total(self): return self._subtotal + self._tax

# Protocols for structural typing
class Drawable(Protocol):
    def draw(self) -> None: ...

# Context managers for resources
with open(file) as f: ...

# Enums for type codes
class Status(Enum):
    ACTIVE = "active"

# Comprehensions for transformations
[x*2 for x in items if x > 0]

# Tuple for read-only collections
return tuple(self._items)

# classmethod for factories
@classmethod
def from_dict(cls, data): ...
```

### ❌ Avoid These

```python
# ❌ Getter/setter everywhere
def get_name(self): ...
def set_name(self, value): ...

# ❌ Unnecessary interfaces
class Nameable(ABC): ...
class Ageable(ABC): ...

# ❌ Over-abstracted
class AbstractFactoryProvider: ...

# ❌ Manual resource management
f = open(file)
try: ...
finally: f.close()

# ❌ Integer type codes
STATUS_ACTIVE = 1

# ❌ Manual loops for simple ops
result = []
for x in items:
    result.append(x*2)
```

---

## When in Doubt

1. **Can it be simpler?** → Make it simpler
2. **Can it be named better?** → Rename it
3. **Can it be shorter?** → Extract
4. **Can it be more specific?** → Replace generic with specific
5. **Can it be deleted?** → Delete it

**Remember:** Perfect is the enemy of good. Apply refactorings incrementally, test after each change, and stop when the code is clear enough.
