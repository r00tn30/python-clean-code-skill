# Clean Code Catalog — Python Reference

This document provides a catalog of **23 code smells** and **70 refactoring techniques**, expressed in idiomatic Python with examples.

---

## Table of Contents

### Code Smells by Category
1. [Bloaters](#bloaters) (5 smells)
2. [Object-Orientation Abusers](#object-orientation-abusers) (4 smells)
3. [Change Preventers](#change-preventers) (3 smells)
4. [Dispensables](#dispensables) (6 smells)
5. [Couplers](#couplers) (5 smells)

### Refactoring Techniques by Category
1. [Composing Methods](#composing-methods) (9 techniques)
2. [Moving Features Between Objects](#moving-features-between-objects) (8 techniques)
3. [Organizing Data](#organizing-data) (16 techniques)
4. [Simplifying Conditional Expressions](#simplifying-conditional-expressions) (9 techniques)
5. [Simplifying Method Calls](#simplifying-method-calls) (13 techniques)
6. [Dealing with Generalization](#dealing-with-generalization) (15 techniques)

---

# Code Smells

## Bloaters

Bloaters are code elements that have grown so large they are hard to work with.

### 1. Long Method

**Description**: A method that has grown too long to understand at a glance.

**Threshold**: > 10 lines is suspicious, > 20 lines needs refactoring.

**Python example** (bad):
```python
def process_order(order_data):
    # Validate
    if not order_data.get('customer_id'):
        raise ValueError("Missing customer")
    if not order_data.get('items'):
        raise ValueError("No items")

    # Calculate totals
    subtotal = 0
    for item in order_data['items']:
        subtotal += item['price'] * item['quantity']

    # Apply discount
    discount = 0
    if order_data.get('coupon'):
        if order_data['coupon'] == 'SAVE10':
            discount = subtotal * 0.1

    # Calculate tax
    tax = (subtotal - discount) * 0.08

    # Save to database
    total = subtotal - discount + tax
    # ... database code ...
```

**Refactoring**: Extract Method

**Python example** (good):
```python
def process_order(order_data):
    _validate_order(order_data)
    subtotal = _calculate_subtotal(order_data['items'])
    discount = _calculate_discount(subtotal, order_data.get('coupon'))
    tax = _calculate_tax(subtotal - discount)
    total = subtotal - discount + tax
    _save_order(order_data, total)
```

---

### 2. Large Class

**Description**: A class with too many attributes, methods, or lines of code.

**Threshold**: > 150 lines, > 10 methods, or > 5 attributes all hint at multiple responsibilities.

**Python example** (bad):
```python
class UserManager:
    def authenticate(self, username, password): ...
    def send_welcome_email(self, user): ...
    def log_user_action(self, user, action): ...
    def generate_report(self, user): ...
    def export_to_csv(self, users): ...
    def validate_password_strength(self, password): ...
    # 20 more methods...
```

**Refactoring**: Extract Class, Extract Subclass

**Python example** (good):
```python
class Authenticator:
    def authenticate(self, username, password): ...
    def validate_password_strength(self, password): ...

class UserNotifier:
    def send_welcome_email(self, user): ...

class UserLogger:
    def log_action(self, user, action): ...

class UserReporter:
    def generate_report(self, user): ...
    def export_to_csv(self, users): ...
```

---

### 3. Primitive Obsession

**Description**: Using primitive types (int, str, float) instead of small domain objects.

**Python example** (bad):
```python
def send_email(to: str, subject: str, body: str):
    # No validation that 'to' is a valid email
    ...

price = 19.99  # Is this USD? EUR? Pre-tax? Post-tax?
```

**Refactoring**: Replace Data Value with Object, Replace Type Code with Class

**Python example** (good):
```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.value):
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

def send_email(to: EmailAddress, subject: str, body: str):
    ...

price = Money(19.99, "USD")
```

---

### 4. Long Parameter List

**Description**: More than 3 parameters make a function hard to understand and call.

**Python example** (bad):
```python
def create_user(first_name: str, last_name: str, email: str,
                phone: str, address: str, city: str, zip_code: str):
    ...
```

**Refactoring**: Introduce Parameter Object, Preserve Whole Object

**Python example** (good):
```python
from dataclasses import dataclass

@dataclass
class UserData:
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    city: str
    zip_code: str

def create_user(data: UserData):
    ...
```

---

### 5. Data Clumps

**Description**: The same group of variables always appears together.

**Python example** (bad):
```python
def calculate_distance(x1, y1, x2, y2):
    ...

def plot_line(x1, y1, x2, y2, color):
    ...

def check_collision(x1, y1, x2, y2, radius):
    ...
```

**Refactoring**: Introduce Parameter Object, Extract Class

**Python example** (good):
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

def calculate_distance(p1: Point, p2: Point) -> float:
    ...

def plot_line(start: Point, end: Point, color: str):
    ...

def check_collision(p1: Point, p2: Point, radius: float) -> bool:
    ...
```

---

## Object-Orientation Abusers

### 6. Switch Statements

**Description**: Complex switch/if-elif chains based on type codes or object types.

**Python example** (bad):
```python
def calculate_price(customer_type: str, base_price: float) -> float:
    if customer_type == "regular":
        return base_price
    elif customer_type == "premium":
        return base_price * 0.9
    elif customer_type == "gold":
        return base_price * 0.8
    else:
        raise ValueError(f"Unknown customer type: {customer_type}")
```

**Refactoring**: Replace Conditional with Polymorphism, Replace Type Code with Subclasses

**Python example** (good):
```python
from abc import ABC, abstractmethod

class Customer(ABC):
    @abstractmethod
    def calculate_price(self, base_price: float) -> float:
        pass

class RegularCustomer(Customer):
    def calculate_price(self, base_price: float) -> float:
        return base_price

class PremiumCustomer(Customer):
    def calculate_price(self, base_price: float) -> float:
        return base_price * 0.9

class GoldCustomer(Customer):
    def calculate_price(self, base_price: float) -> float:
        return base_price * 0.8
```

---

### 7. Temporary Field

**Description**: An attribute that is only set and used under certain conditions.

**Python example** (bad):
```python
class Order:
    def __init__(self):
        self.items = []
        self.discount = None  # Only set if there's a coupon
        self.coupon_code = None  # Only set if there's a coupon

    def apply_coupon(self, code):
        self.coupon_code = code
        self.discount = self._calculate_discount(code)
```

**Refactoring**: Extract Class, Introduce Null Object

**Python example** (good):
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Discount:
    code: str
    amount: float

class Order:
    def __init__(self, items: list, discount: Optional[Discount] = None):
        self.items = items
        self.discount = discount
```

---

### 8. Refused Bequest

**Description**: A subclass inherits methods/data it doesn't use or overrides them to do nothing.

**Python example** (bad):
```python
class Bird:
    def fly(self):
        print("Flying")

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError("Penguins can't fly")
```

**Refactoring**: Replace Inheritance with Delegation, Extract Superclass

**Python example** (good):
```python
class Bird:
    pass

class FlyingBird(Bird):
    def fly(self):
        print("Flying")

class Penguin(Bird):
    pass  # No fly method

class Sparrow(FlyingBird):
    pass  # Inherits fly
```

---

### 9. Alternative Classes with Different Interfaces

**Description**: Two classes do similar things but have different method names/signatures.

**Python example** (bad):
```python
class FileReader:
    def read_from_file(self, path):
        ...

class DatabaseReader:
    def fetch_from_db(self, query):
        ...
```

**Refactoring**: Rename Method, Extract Superclass, Extract Interface

**Python example** (good):
```python
from typing import Protocol

class DataSource(Protocol):
    def read(self) -> str:
        ...

class FileReader:
    def __init__(self, path: str):
        self._path = path

    def read(self) -> str:
        with open(self._path) as f:
            return f.read()

class DatabaseReader:
    def __init__(self, query: str):
        self._query = query

    def read(self) -> str:
        # Execute query and return results
        ...
```

---

## Change Preventers

### 10. Divergent Change

**Description**: One class is changed in different ways for different reasons.

**Example**: A `User` class that needs changes for authentication, reporting, and email logic.

**Refactoring**: Extract Class, Extract Superclass

**Python example**:
```python
# Bad: User class changes for multiple reasons
class User:
    def authenticate(self): ...
    def send_notification(self): ...
    def generate_report(self): ...

# Good: Split by responsibility
class User:
    def __init__(self, auth: Authenticator, notifier: Notifier):
        self._auth = auth
        self._notifier = notifier

class Authenticator:
    def authenticate(self, user): ...

class Notifier:
    def send_notification(self, user): ...
```

---

### 11. Shotgun Surgery

**Description**: A single change requires modifying many unrelated classes.

**Example**: Adding a new field requires changes in UI, database, API, validator, serializer.

**Refactoring**: Move Method, Move Field, Inline Class

**Python example**:
```python
# Bad: Adding 'email' field requires changes everywhere
class UserUI:
    def display(self, first, last, phone, email): ...

class UserDB:
    def save(self, first, last, phone, email): ...

# Good: Encapsulate in one place
@dataclass
class User:
    first_name: str
    last_name: str
    phone: str
    email: str

class UserUI:
    def display(self, user: User): ...

class UserDB:
    def save(self, user: User): ...
```

---

### 12. Parallel Inheritance Hierarchies

**Description**: Every time you add a subclass to one hierarchy, you must add a corresponding subclass to another.

**Python example** (bad):
```python
# Every new Shape requires a new ShapeDrawer
class Shape: pass
class Circle(Shape): pass
class Square(Shape): pass

class ShapeDrawer: pass
class CircleDrawer(ShapeDrawer): pass
class SquareDrawer(ShapeDrawer): pass
```

**Refactoring**: Move Method, Move Field

**Python example** (good):
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def draw(self):
        pass

class Circle(Shape):
    def draw(self):
        # Circle-specific drawing logic
        ...

class Square(Shape):
    def draw(self):
        # Square-specific drawing logic
        ...
```

---

## Dispensables

### 13. Comments

**Description**: Comments that explain *what* the code does (not *why*).

**Python example** (bad):
```python
# Check if the user has permission
if user.role == "admin" or user.role == "moderator":
    # Allow access
    return True
```

**Refactoring**: Extract Method, Rename Method, Introduce Assertion

**Python example** (good):
```python
def has_moderation_permission(user):
    return user.role in ("admin", "moderator")

if has_moderation_permission(user):
    return True
```

---

### 14. Duplicate Code

**Description**: The same code structure in multiple places.

**Python example** (bad):
```python
def save_customer(customer):
    if not customer.email:
        raise ValueError("Email required")
    db.save(customer)

def save_order(order):
    if not order.customer:
        raise ValueError("Customer required")
    db.save(order)
```

**Refactoring**: Extract Method, Extract Class, Pull Up Method

**Python example** (good):
```python
def validate_and_save(entity, validator):
    validator(entity)
    db.save(entity)

def validate_customer(customer):
    if not customer.email:
        raise ValueError("Email required")

def validate_order(order):
    if not order.customer:
        raise ValueError("Customer required")

# Usage
validate_and_save(customer, validate_customer)
validate_and_save(order, validate_order)
```

---

### 15. Lazy Class

**Description**: A class that doesn't do enough to justify its existence.

**Python example** (bad):
```python
class Formatter:
    def format(self, text):
        return text.upper()

# Used in only one place
formatter = Formatter()
result = formatter.format(data)
```

**Refactoring**: Inline Class, Collapse Hierarchy

**Python example** (good):
```python
# Just use the method directly
result = data.upper()
```

---

### 16. Data Class

**Description**: A class with only public attributes and getters/setters, no behavior.

**Note**: Legitimate for DTOs crossing boundaries. Otherwise, move behavior to the data.

**Python example** (bad for domain logic):
```python
@dataclass
class Order:
    items: list
    subtotal: float
    tax: float

# Behavior lives outside the data
def calculate_total(order):
    return order.subtotal + order.tax
```

**Refactoring**: Move Method

**Python example** (good):
```python
@dataclass
class Order:
    items: list
    subtotal: float
    tax: float

    def total(self) -> float:
        return self.subtotal + self.tax
```

---

### 17. Dead Code

**Description**: Unused variables, parameters, functions, classes, or imports.

**Python example** (bad):
```python
import os  # Never used
import sys

def calculate_price(base, tax, discount):  # discount never used
    return base * (1 + tax)

def old_algorithm():  # Never called
    ...
```

**Refactoring**: Delete it. Use tools like `ruff`, `vulture`, or `flake8`.

---

### 18. Speculative Generality

**Description**: Code written to support future requirements that don't exist yet.

**Python example** (bad):
```python
class AbstractFactoryProducer:
    def get_factory(self, factory_type, **kwargs):
        # Supports 10 different factory types, only 1 is ever used
        ...
```

**Refactoring**: Collapse Hierarchy, Inline Class, Remove Parameter

**Python example** (good):
```python
# Just write what you need now
def create_user(name: str, email: str):
    return User(name, email)
```

---

## Couplers

### 19. Feature Envy

**Description**: A method accesses data of another object more than its own.

**Python example** (bad):
```python
class Invoice:
    def calculate_priority(self):
        # Accesses customer data more than invoice data
        if self.customer.premium and self.customer.days_overdue > 30:
            return "high"
        elif self.customer.days_overdue > 60:
            return "urgent"
        return "normal"
```

**Refactoring**: Move Method

**Python example** (good):
```python
class Customer:
    def invoice_priority(self):
        if self.premium and self.days_overdue > 30:
            return "high"
        elif self.days_overdue > 60:
            return "urgent"
        return "normal"

class Invoice:
    def calculate_priority(self):
        return self.customer.invoice_priority()
```

---

### 20. Inappropriate Intimacy

**Description**: One class uses internal attributes/methods of another.

**Python example** (bad):
```python
class Order:
    def __init__(self):
        self._items = []

class OrderProcessor:
    def process(self, order):
        # Directly accesses private attribute
        for item in order._items:
            ...
```

**Refactoring**: Move Method, Move Field, Change Bidirectional Association to Unidirectional

**Python example** (good):
```python
class Order:
    def __init__(self):
        self._items = []

    def items(self):
        return tuple(self._items)  # Read-only access

class OrderProcessor:
    def process(self, order):
        for item in order.items():
            ...
```

---

### 21. Message Chains

**Description**: Chaining through multiple objects: `a.b.c.d.e`.

**Python example** (bad):
```python
city = order.customer.address.city
```

**Refactoring**: Hide Delegate

**Python example** (good):
```python
class Order:
    def customer_city(self):
        return self.customer.address.city

city = order.customer_city()
```

---

### 22. Middle Man

**Description**: A class that does nothing but delegate to another class.

**Python example** (bad):
```python
class OrderFacade:
    def __init__(self, order):
        self._order = order

    def total(self):
        return self._order.total()

    def items(self):
        return self._order.items()

    # Every method just forwards to _order
```

**Refactoring**: Remove Middle Man, Inline Class

**Python example** (good):
```python
# Just use Order directly
order.total()
order.items()
```

---

### 23. Incomplete Library Class

**Description**: A third-party library is missing methods you need.

**Python example** (bad):
```python
# Using a third-party Date class that lacks a method
def days_until(date):
    return (date.value - datetime.now()).days  # Accessing internals
```

**Refactoring**: Introduce Foreign Method, Introduce Local Extension

**Python example** (good):
```python
# Foreign method (module-level function)
def days_until(date: ThirdPartyDate) -> int:
    return (date.to_datetime() - datetime.now()).days

# Or local extension (wrapper)
class ExtendedDate:
    def __init__(self, date: ThirdPartyDate):
        self._date = date

    def days_until(self) -> int:
        return (self._date.to_datetime() - datetime.now()).days

    def __getattr__(self, name):
        return getattr(self._date, name)
```

---

# Refactoring Techniques

## Composing Methods

### 1. Extract Method

**When**: A code fragment can be grouped together and given a name.

**Python**:
```python
# Before
def print_invoice(orders):
    print("*** Invoice ***")
    total = 0
    for order in orders:
        print(f"{order.name}: ${order.price}")
        total += order.price
    print(f"Total: ${total}")

# After
def print_invoice(orders):
    print_header()
    total = print_items(orders)
    print_footer(total)

def print_header():
    print("*** Invoice ***")

def print_items(orders):
    total = 0
    for order in orders:
        print(f"{order.name}: ${order.price}")
        total += order.price
    return total

def print_footer(total):
    print(f"Total: ${total}")
```

---

### 2. Inline Method

**When**: A method body is as clear as its name.

**Python**:
```python
# Before
def is_underage(person):
    return person.age < 18

def can_vote(person):
    return not is_underage(person)

# After
def can_vote(person):
    return person.age >= 18
```

---

### 3. Extract Variable

**When**: A complex expression is hard to read.

**Python**:
```python
# Before
if (platform == "web" and user.age > 18 and user.verified):
    ...

# After
is_adult_verified_web_user = (
    platform == "web" and
    user.age > 18 and
    user.verified
)
if is_adult_verified_web_user:
    ...
```

---

### 4. Inline Temp

**When**: A variable is assigned once and used once.

**Python**:
```python
# Before
base_price = order.base_price()
return base_price > 1000

# After
return order.base_price() > 1000
```

---

### 5. Replace Temp with Query

**When**: A temporary variable holds a computed value used multiple times.

**Python**:
```python
# Before
def calculate_total(order):
    base_price = order.quantity * order.item_price
    if base_price > 1000:
        return base_price * 0.95
    else:
        return base_price * 0.98

# After
def calculate_total(order):
    if base_price(order) > 1000:
        return base_price(order) * 0.95
    else:
        return base_price(order) * 0.98

def base_price(order):
    return order.quantity * order.item_price
```

---

### 6. Split Temporary Variable

**When**: A variable is assigned more than once (and not a loop counter).

**Python**:
```python
# Before
temp = 2 * (height + width)
print(f"Perimeter: {temp}")
temp = height * width
print(f"Area: {temp}")

# After
perimeter = 2 * (height + width)
print(f"Perimeter: {perimeter}")
area = height * width
print(f"Area: {area}")
```

---

### 7. Remove Assignments to Parameters

**When**: A parameter is reassigned within the method.

**Python**:
```python
# Before
def discount(price, quantity):
    if quantity > 10:
        price = price * 0.9  # Reassigning parameter
    return price

# After
def discount(price, quantity):
    result = price
    if quantity > 10:
        result = result * 0.9
    return result
```

---

### 8. Replace Method with Method Object

**When**: A long method has too many local variables to extract easily.

**Python**:
```python
# Before
def calculate_price(base, quantity, discount_code, tax_rate):
    temp1 = base * quantity
    temp2 = apply_discount(temp1, discount_code)
    temp3 = temp2 * (1 + tax_rate)
    # Many more temps...
    return temp3

# After
class PriceCalculator:
    def __init__(self, base, quantity, discount_code, tax_rate):
        self.base = base
        self.quantity = quantity
        self.discount_code = discount_code
        self.tax_rate = tax_rate

    def compute(self):
        subtotal = self._subtotal()
        discounted = self._apply_discount(subtotal)
        return self._add_tax(discounted)

    def _subtotal(self):
        return self.base * self.quantity

    def _apply_discount(self, amount):
        # Use self.discount_code
        ...

    def _add_tax(self, amount):
        return amount * (1 + self.tax_rate)

def calculate_price(base, quantity, discount_code, tax_rate):
    calculator = PriceCalculator(base, quantity, discount_code, tax_rate)
    return calculator.compute()
```

---

### 9. Substitute Algorithm

**When**: You want to replace an algorithm with a clearer or more standard one.

**Python**:
```python
# Before
def find_max(numbers):
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

# After
def find_max(numbers):
    return max(numbers)
```

---

## Moving Features Between Objects

### 10. Move Method

**When**: A method is used more by another class than its own.

**Python**:
```python
# Before
class Account:
    def overdraft_charge(self):
        if self.account_type == "premium":
            return 10
        else:
            return 20

# After
class AccountType:
    def overdraft_charge(self):
        return 10  # Or 20, depending on subclass

class Account:
    def overdraft_charge(self):
        return self.account_type.overdraft_charge()
```

---

### 11. Move Field

**When**: An attribute is used more by another class.

**Python**:
```python
# Before
class Account:
    def __init__(self):
        self.interest_rate = 0.05

class AccountCalculator:
    def calculate_interest(self, account):
        return account.balance * account.interest_rate

# After
class AccountType:
    def __init__(self):
        self.interest_rate = 0.05

class Account:
    def __init__(self, account_type):
        self.account_type = account_type

    def interest_rate(self):
        return self.account_type.interest_rate
```

---

### 12. Extract Class

**When**: One class does the work of two.

**Python**:
```python
# Before
class Person:
    def __init__(self):
        self.name = ""
        self.area_code = ""
        self.phone_number = ""

    def telephone_number(self):
        return f"{self.area_code}-{self.phone_number}"

# After
class TelephoneNumber:
    def __init__(self, area_code, number):
        self.area_code = area_code
        self.number = number

    def full_number(self):
        return f"{self.area_code}-{self.number}"

class Person:
    def __init__(self):
        self.name = ""
        self.phone = TelephoneNumber("", "")
```

---

### 13. Inline Class

**When**: A class does too little to justify its existence.

**Python**:
```python
# Before
class Address:
    def __init__(self, street):
        self.street = street

class Person:
    def __init__(self, address):
        self.address = address

# After (if Address has no other behavior)
class Person:
    def __init__(self, street):
        self.street = street
```

---

### 14. Hide Delegate

**When**: A client calls methods on an object obtained from another.

**Python**:
```python
# Before
manager = employee.department.manager

# After
class Employee:
    def manager(self):
        return self.department.manager

manager = employee.manager()
```

---

### 15. Remove Middle Man

**When**: A class does too much delegation.

**Python**:
```python
# Before
class Person:
    def __init__(self, department):
        self._department = department

    def manager(self):
        return self._department.manager()

    def budget(self):
        return self._department.budget()

    # 20 more forwarding methods

# After
# Just expose the department and let clients call it directly
person.department.manager()
person.department.budget()
```

---

### 16. Introduce Foreign Method

**When**: You need a method on a class you can't modify.

**Python**:
```python
# ThirdPartyDate is a library class you can't modify
def next_day(date: ThirdPartyDate) -> ThirdPartyDate:
    return ThirdPartyDate(date.year, date.month, date.day + 1)

# Usage
tomorrow = next_day(today)
```

---

### 17. Introduce Local Extension

**When**: You need many methods on a class you can't modify.

**Python**:
```python
# Option 1: Subclass
class ExtendedDate(ThirdPartyDate):
    def next_day(self):
        return ExtendedDate(self.year, self.month, self.day + 1)

    def previous_day(self):
        return ExtendedDate(self.year, self.month, self.day - 1)

# Option 2: Wrapper
class DateWrapper:
    def __init__(self, date: ThirdPartyDate):
        self._date = date

    def next_day(self):
        return DateWrapper(ThirdPartyDate(
            self._date.year, self._date.month, self._date.day + 1
        ))

    def __getattr__(self, name):
        return getattr(self._date, name)
```

---

## Organizing Data

### 18. Self Encapsulate Field

**When**: You need to add behavior around field access.

**Python**:
```python
# Before
class Product:
    def __init__(self, price):
        self.price = price

# After
class Product:
    def __init__(self, price):
        self._price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value
```

---

### 19. Replace Data Value with Object

**When**: A simple field needs additional behavior or validation.

**Python**:
```python
# Before
customer_name = "John"  # Just a string

# After
@dataclass(frozen=True)
class CustomerName:
    value: str

    def __post_init__(self):
        if len(self.value) < 2:
            raise ValueError("Name too short")

    def initials(self):
        return ''.join(word[0] for word in self.value.split())

customer_name = CustomerName("John Doe")
```

---

### 20. Change Value to Reference

**When**: Many identical value objects should actually be references to a single shared object.

**Python**:
```python
# Before: Every order has its own Customer instance
order1 = Order(Customer("Alice"))
order2 = Order(Customer("Alice"))  # Different object, same data

# After: Use a registry
class CustomerRegistry:
    _customers = {}

    @classmethod
    def get(cls, name):
        if name not in cls._customers:
            cls._customers[name] = Customer(name)
        return cls._customers[name]

order1 = Order(CustomerRegistry.get("Alice"))
order2 = Order(CustomerRegistry.get("Alice"))  # Same object
```

---

### 21. Change Reference to Value

**When**: A small reference object is better as an immutable value object.

**Python**:
```python
# Before: Currency as singleton
class Currency:
    _instances = {}

    @classmethod
    def get(cls, code):
        if code not in cls._instances:
            cls._instances[code] = Currency(code)
        return cls._instances[code]

# After: Currency as value
@dataclass(frozen=True)
class Currency:
    code: str

    def __eq__(self, other):
        return isinstance(other, Currency) and self.code == other.code

    def __hash__(self):
        return hash(self.code)
```

---

### 22. Replace Array with Object

**When**: An array has elements with special meanings.

**Python**:
```python
# Before
row = ["Alice", "30", "Engineer"]
name = row[0]
age = row[1]
title = row[2]

# After
@dataclass
class Employee:
    name: str
    age: int
    title: str

employee = Employee("Alice", 30, "Engineer")
```

---

### 23. Duplicate Observed Data

**When**: Domain data is stored in GUI components.

**Python**:
```python
# Before
class OrderWindow:
    def __init__(self):
        self.total_text = "0.00"  # GUI component

    def calculate(self):
        self.total_text = str(compute_total())

# After
class Order:
    def __init__(self):
        self._total = 0.0

    def total(self):
        return self._total

    def set_total(self, value):
        self._total = value
        self._notify_observers()

class OrderWindow:
    def __init__(self, order):
        self.order = order
        self.order.add_observer(self)

    def update(self):
        self.total_text = str(self.order.total())
```

---

### 24. Change Unidirectional Association to Bidirectional

**When**: Two classes need to reference each other.

**Python**:
```python
# Before
class Order:
    def __init__(self, customer):
        self.customer = customer
# Customer doesn't know about its orders

# After
class Order:
    def __init__(self, customer):
        self._customer = None
        self.set_customer(customer)

    def set_customer(self, customer):
        if self._customer:
            self._customer._remove_order(self)
        self._customer = customer
        customer._add_order(self)

class Customer:
    def __init__(self):
        self._orders = []

    def _add_order(self, order):
        self._orders.append(order)

    def _remove_order(self, order):
        self._orders.remove(order)
```

---

### 25. Change Bidirectional Association to Unidirectional

**When**: A two-way link is no longer needed.

**Python**:
```python
# Before
class Order:
    def __init__(self, customer):
        self.customer = customer
        customer.add_order(self)

class Customer:
    def __init__(self):
        self.orders = []

# After (if Customer doesn't need orders list)
class Order:
    def __init__(self, customer):
        self.customer = customer

class Customer:
    pass  # No orders list
```

---

### 26. Replace Magic Number with Symbolic Constant

**Python**:
```python
# Before
def calculate_energy(mass):
    return mass * 299792458 ** 2

# After
SPEED_OF_LIGHT = 299_792_458  # meters per second

def calculate_energy(mass):
    return mass * SPEED_OF_LIGHT ** 2
```

---

### 27. Encapsulate Field

**Python**:
```python
# Before
class Person:
    def __init__(self, name):
        self.name = name

# After
class Person:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
```

---

### 28. Encapsulate Collection

**Python**:
```python
# Before
class Course:
    def __init__(self):
        self.students = []  # Mutable collection exposed

course.students.append(student)  # Direct modification

# After
class Course:
    def __init__(self):
        self._students = []

    def students(self):
        return tuple(self._students)  # Read-only view

    def add_student(self, student):
        self._students.append(student)

    def remove_student(self, student):
        self._students.remove(student)
```

---

### 29. Replace Type Code with Class

**Python**:
```python
# Before
BLOOD_TYPE_O = 0
BLOOD_TYPE_A = 1
BLOOD_TYPE_B = 2

class Person:
    def __init__(self, blood_type):
        self.blood_type = blood_type

# After
from enum import Enum

class BloodType(Enum):
    O = "O"
    A = "A"
    B = "B"
    AB = "AB"

class Person:
    def __init__(self, blood_type: BloodType):
        self.blood_type = blood_type
```

---

### 30. Replace Type Code with Subclasses

**Python**:
```python
# Before
class Employee:
    def __init__(self, employee_type):
        self.type = employee_type

    def pay_amount(self):
        if self.type == "engineer":
            return 5000
        elif self.type == "manager":
            return 8000

# After
class Employee:
    @abstractmethod
    def pay_amount(self):
        pass

class Engineer(Employee):
    def pay_amount(self):
        return 5000

class Manager(Employee):
    def pay_amount(self):
        return 8000
```

---

### 31. Replace Type Code with State/Strategy

**Python**:
```python
# Before
class Player:
    def __init__(self):
        self.state = "normal"

    def move(self):
        if self.state == "normal":
            return 5
        elif self.state == "boosted":
            return 10

# After
class PlayerState(ABC):
    @abstractmethod
    def move_speed(self):
        pass

class NormalState(PlayerState):
    def move_speed(self):
        return 5

class BoostedState(PlayerState):
    def move_speed(self):
        return 10

class Player:
    def __init__(self):
        self._state = NormalState()

    def set_state(self, state: PlayerState):
        self._state = state

    def move(self):
        return self._state.move_speed()
```

---

### 32. Replace Subclass with Fields

**Python**:
```python
# Before
class Person:
    pass

class Male(Person):
    def gender(self):
        return "M"

class Female(Person):
    def gender(self):
        return "F"

# After
class Person:
    def __init__(self, gender):
        self._gender = gender

    def gender(self):
        return self._gender
```

---

### 33. Encapsulate Downcast

(Less relevant in Python due to duck typing, but if needed:)

**Python**:
```python
# Before
def last_reading(sensors):
    return sensors[-1]  # Returns Any, caller must cast

reading = last_reading(sensors)
temp = reading.temperature  # Assumes it's a TempReading

# After
def last_reading(sensors) -> TempReading:
    return sensors[-1]  # Type hint makes it clear
```

---

## Simplifying Conditional Expressions

### 34. Decompose Conditional

**Python**:
```python
# Before
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
def is_winter(date):
    return date.before(SUMMER_START) or date.after(SUMMER_END)

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge

def summer_charge(quantity):
    return quantity * summer_rate

if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

---

### 35. Consolidate Conditional Expression

**Python**:
```python
# Before
def disability_amount(employee):
    if employee.seniority < 2:
        return 0
    if employee.months_disabled > 12:
        return 0
    if employee.is_part_time:
        return 0
    # Calculate disability

# After
def disability_amount(employee):
    if is_not_eligible_for_disability(employee):
        return 0
    # Calculate disability

def is_not_eligible_for_disability(employee):
    return (employee.seniority < 2 or
            employee.months_disabled > 12 or
            employee.is_part_time)
```

---

### 36. Consolidate Duplicate Conditional Fragments

**Python**:
```python
# Before
if is_special_deal():
    total = price * 0.95
    send_order()
else:
    total = price * 0.98
    send_order()

# After
if is_special_deal():
    total = price * 0.95
else:
    total = price * 0.98
send_order()
```

---

### 37. Remove Control Flag

**Python**:
```python
# Before
def find_person(people, name):
    found = False
    for person in people:
        if not found:
            if person.name == name:
                found = True
                return person
    return None

# After
def find_person(people, name):
    for person in people:
        if person.name == name:
            return person
    return None
```

---

### 38. Replace Nested Conditional with Guard Clauses

**Python**:
```python
# Before
def pay_amount(employee):
    if employee.is_dead:
        result = dead_amount()
    else:
        if employee.is_separated:
            result = separated_amount()
        else:
            if employee.is_retired:
                result = retired_amount()
            else:
                result = normal_amount()
    return result

# After
def pay_amount(employee):
    if employee.is_dead:
        return dead_amount()
    if employee.is_separated:
        return separated_amount()
    if employee.is_retired:
        return retired_amount()
    return normal_amount()
```

---

### 39. Replace Conditional with Polymorphism

See "Switch Statements" smell example above.

---

### 40. Introduce Null Object

**Python**:
```python
# Before
if customer is None:
    plan = "basic"
else:
    plan = customer.plan

# After
class NullCustomer:
    @property
    def plan(self):
        return "basic"

class RealCustomer:
    def __init__(self, plan):
        self._plan = plan

    @property
    def plan(self):
        return self._plan

# Usage
customer = customer or NullCustomer()
plan = customer.plan
```

---

### 41. Introduce Assertion

**Python**:
```python
# Before
def calculate_discount(price):
    # Assumes price is positive
    return price * 0.1

# After
def calculate_discount(price):
    assert price >= 0, "Price must be non-negative"
    return price * 0.1
```

---

## Simplifying Method Calls

### 42. Rename Method

**Python**:
```python
# Before
def get_inv_cdttl():
    ...

# After
def invoice_credit_total():
    ...
```

---

### 43. Add Parameter

**Python**:
```python
# Before
def contact_customer():
    ...

# After
def contact_customer(method: str):  # "email", "phone"
    ...
```

---

### 44. Remove Parameter

**Python**:
```python
# Before
def calculate_total(items, tax_rate, unused_param):
    ...

# After
def calculate_total(items, tax_rate):
    ...
```

---

### 45. Separate Query from Modifier

**Python**:
```python
# Before
def check_security_and_send(user, data):
    if user.has_permission():
        send_data(data)
        return True
    return False

# After
def has_send_permission(user):
    return user.has_permission()

def send_data_if_allowed(user, data):
    if has_send_permission(user):
        send_data(data)
```

---

### 46. Parameterize Method

**Python**:
```python
# Before
def increase_by_five(value):
    return value + 5

def increase_by_ten(value):
    return value + 10

# After
def increase_by(value, amount):
    return value + amount
```

---

### 47. Replace Parameter with Explicit Methods

**Python**:
```python
# Before
def set_value(name, value):
    if name == "height":
        self._height = value
    elif name == "width":
        self._width = value

# After
def set_height(self, value):
    self._height = value

def set_width(self, value):
    self._width = value
```

---

### 48. Preserve Whole Object

**Python**:
```python
# Before
low = weather.low_temperature()
high = weather.high_temperature()
is_within = plan.within_range(low, high)

# After
is_within = plan.within_range(weather)
```

---

### 49. Replace Parameter with Method Call

**Python**:
```python
# Before
base_price = quantity * item_price
discount = self.discount_level()
price = discounted_price(base_price, discount)

# After
base_price = quantity * item_price
price = discounted_price(base_price)

def discounted_price(base_price):
    return base_price * (1 - self.discount_level())
```

---

### 50. Introduce Parameter Object

See "Data Clumps" and "Long Parameter List" examples above.

---

### 51. Remove Setting Method

**Python**:
```python
# Before
class Account:
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):  # Should not be settable
        self._id = value

# After
class Account:
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id
    # No setter
```

---

### 52. Hide Method

**Python**:
```python
# Before
class Account:
    def validate_balance(self):  # Public but only used internally
        ...

# After
class Account:
    def _validate_balance(self):  # Private
        ...
```

---

### 53. Replace Constructor with Factory Method

**Python**:
```python
# Before
class Employee:
    def __init__(self, employee_type):
        self.type = employee_type

employee = Employee("engineer")

# After
class Employee:
    def __init__(self):
        pass

    @classmethod
    def create_engineer(cls):
        employee = cls()
        employee.type = "engineer"
        return employee

    @classmethod
    def create_manager(cls):
        employee = cls()
        employee.type = "manager"
        return employee

employee = Employee.create_engineer()
```

---

### 54. Replace Error Code with Exception

**Python**:
```python
# Before
def withdraw(amount):
    if amount > balance:
        return -1  # Error code
    balance -= amount
    return 0  # Success

if withdraw(100) == -1:
    print("Insufficient funds")

# After
def withdraw(amount):
    if amount > balance:
        raise InsufficientFundsError(f"Balance: {balance}, Requested: {amount}")
    balance -= amount

try:
    withdraw(100)
except InsufficientFundsError as e:
    print(f"Error: {e}")
```

---

### 55. Replace Exception with Test

**Python**:
```python
# Before
try:
    value = stack.pop()
    # Use value
except IndexError:
    # Handle empty stack
    pass

# After
if not stack.is_empty():
    value = stack.pop()
    # Use value
else:
    # Handle empty stack
    pass
```

---

## Dealing with Generalization

### 56. Pull Up Field

**Python**:
```python
# Before
class Engineer:
    def __init__(self, name):
        self.name = name

class Manager:
    def __init__(self, name):
        self.name = name

# After
class Employee:
    def __init__(self, name):
        self.name = name

class Engineer(Employee):
    pass

class Manager(Employee):
    pass
```

---

### 57. Pull Up Method

**Python**:
```python
# Before
class Engineer:
    def full_name(self):
        return f"{self.first} {self.last}"

class Manager:
    def full_name(self):
        return f"{self.first} {self.last}"

# After
class Employee:
    def full_name(self):
        return f"{self.first} {self.last}"

class Engineer(Employee):
    pass

class Manager(Employee):
    pass
```

---

### 58. Pull Up Constructor Body

**Python**:
```python
# Before
class Engineer:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

class Manager:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

# After
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

class Engineer(Employee):
    def __init__(self, name, salary):
        super().__init__(name, salary)

class Manager(Employee):
    def __init__(self, name, salary):
        super().__init__(name, salary)
```

---

### 59. Push Down Method

**Python**:
```python
# Before
class Employee:
    def specialized_task(self):
        # Only used by Engineer subclass
        ...

# After
class Engineer(Employee):
    def specialized_task(self):
        ...
```

---

### 60. Push Down Field

**Python**:
```python
# Before
class Employee:
    def __init__(self):
        self.certification = None  # Only used by Engineer

# After
class Engineer(Employee):
    def __init__(self):
        super().__init__()
        self.certification = None
```

---

### 61. Extract Subclass

**Python**:
```python
# Before
class JobItem:
    def __init__(self, quantity, unit_price, is_labor, employee=None):
        self.quantity = quantity
        self.unit_price = unit_price
        self.is_labor = is_labor
        self.employee = employee

    def total_price(self):
        if self.is_labor:
            return self.quantity * self.employee.rate
        return self.quantity * self.unit_price

# After
class JobItem:
    def __init__(self, quantity, unit_price):
        self.quantity = quantity
        self.unit_price = unit_price

    def total_price(self):
        return self.quantity * self.unit_price

class LaborItem(JobItem):
    def __init__(self, quantity, employee):
        super().__init__(quantity, 0)
        self.employee = employee

    def total_price(self):
        return self.quantity * self.employee.rate
```

---

### 62. Extract Superclass

**Python**:
```python
# Before
class Employee:
    def __init__(self, name, annual_cost):
        self.name = name
        self.annual_cost = annual_cost

class Department:
    def __init__(self, name, staff):
        self.name = name
        self.staff = staff

    def total_annual_cost(self):
        return sum(s.annual_cost for s in self.staff)

# After (both have name and annual cost)
class Party:
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def annual_cost(self):
        pass

class Employee(Party):
    def __init__(self, name, cost):
        super().__init__(name)
        self._annual_cost = cost

    def annual_cost(self):
        return self._annual_cost

class Department(Party):
    def __init__(self, name, staff):
        super().__init__(name)
        self.staff = staff

    def annual_cost(self):
        return sum(s.annual_cost() for s in self.staff)
```

---

### 63. Extract Interface

**Python**:
```python
# Before
class Employee:
    def calculate_pay(self): ...
    def send_notification(self): ...

class Contractor:
    def calculate_pay(self): ...
    def send_notification(self): ...

# After
from typing import Protocol

class Payable(Protocol):
    def calculate_pay(self) -> float: ...

class Notifiable(Protocol):
    def send_notification(self) -> None: ...

# Employee and Contractor implicitly implement these protocols
```

---

### 64. Collapse Hierarchy

**Python**:
```python
# Before
class Employee:
    pass

class Salesman(Employee):
    pass  # No additional behavior

# After
class Employee:
    pass
# Just use Employee directly
```

---

### 65. Form Template Method

**Python**:
```python
# Before
class Site:
    def billing_amount(self):
        base = self.units * self.rate
        tax = base * 0.1
        return base + tax

class ResidentialSite(Site):
    def billing_amount(self):
        base = self.units * self.rate * 0.5  # Different calculation
        tax = base * 0.2  # Different tax
        return base + tax

# After
class Site(ABC):
    def billing_amount(self):
        base = self._base_amount()
        tax = self._tax_amount(base)
        return base + tax

    @abstractmethod
    def _base_amount(self):
        pass

    @abstractmethod
    def _tax_amount(self, base):
        pass

class CommercialSite(Site):
    def _base_amount(self):
        return self.units * self.rate

    def _tax_amount(self, base):
        return base * 0.1

class ResidentialSite(Site):
    def _base_amount(self):
        return self.units * self.rate * 0.5

    def _tax_amount(self, base):
        return base * 0.2
```

---

### 66. Replace Inheritance with Delegation

**Python**:
```python
# Before
class Stack(list):
    def push(self, item):
        self.append(item)
    # Inherits all list methods, many don't make sense for a stack

# After
class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def is_empty(self):
        return len(self._items) == 0
```

---

### 67. Replace Delegation with Inheritance

**Python**:
```python
# Before
class Manager:
    def __init__(self):
        self._employee = Employee()

    def name(self):
        return self._employee.name()

    def salary(self):
        return self._employee.salary()
    # Many forwarding methods

# After (if Manager truly "is-a" Employee)
class Manager(Employee):
    pass  # Inherits name(), salary(), etc.
```

---

### 68. Tease Apart Inheritance

**When**: A hierarchy is doing two jobs.

**Python**:
```python
# Before
class Deal:
    pass

class ActiveDeal(Deal):
    pass

class PassiveDeal(Deal):
    pass

class TabularActiveDeal(ActiveDeal):  # Mixed concerns: active vs presentation
    pass

class TabularPassiveDeal(PassiveDeal):
    pass

# After
class Deal:
    def __init__(self, presentation_style):
        self._presentation = presentation_style

class PresentationStyle:
    pass

class TabularPresentation(PresentationStyle):
    pass

class ActiveDeal(Deal):
    pass

class PassiveDeal(Deal):
    pass
```

---

### 69. Convert Procedural Design to Objects

**Python**:
```python
# Before (procedural)
def calculate_order_total(items, customer_type):
    subtotal = sum(item['price'] * item['qty'] for item in items)
    if customer_type == "premium":
        discount = subtotal * 0.1
    else:
        discount = 0
    return subtotal - discount

# After (OO)
class Order:
    def __init__(self, items, customer):
        self.items = items
        self.customer = customer

    def total(self):
        subtotal = sum(item.price * item.quantity for item in self.items)
        return subtotal - self.customer.discount(subtotal)

class Customer:
    def discount(self, amount):
        return 0

class PremiumCustomer(Customer):
    def discount(self, amount):
        return amount * 0.1
```

---

### 70. Separate Domain from Presentation

**Python**:
```python
# Before
class OrderWindow:
    def __init__(self):
        self.items = []  # Domain data
        self.total_label = Label()  # UI component

    def add_item(self, item):
        self.items.append(item)
        self.total_label.set_text(str(sum(i.price for i in self.items)))

# After
class Order:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def total(self):
        return sum(i.price for i in self.items)

class OrderWindow:
    def __init__(self, order):
        self.order = order
        self.total_label = Label()

    def add_item(self, item):
        self.order.add_item(item)
        self.total_label.set_text(str(self.order.total()))
```

---

# Quick Lookup: Smell → Refactoring

| Code Smell | Primary Refactoring Techniques |
|------------|-------------------------------|
| Long Method | Extract Method, Replace Temp with Query, Replace Method with Method Object |
| Large Class | Extract Class, Extract Subclass, Extract Interface |
| Primitive Obsession | Replace Data Value with Object, Replace Type Code with Class, Extract Class |
| Long Parameter List | Introduce Parameter Object, Preserve Whole Object, Replace Parameter with Method Call |
| Data Clumps | Introduce Parameter Object, Extract Class |
| Switch Statements | Replace Conditional with Polymorphism, Replace Type Code with Subclasses, Replace Type Code with State/Strategy |
| Temporary Field | Extract Class, Introduce Null Object |
| Refused Bequest | Replace Inheritance with Delegation, Push Down Method, Push Down Field |
| Alternative Classes with Different Interfaces | Rename Method, Move Method, Extract Superclass, Extract Interface |
| Divergent Change | Extract Class, Extract Superclass |
| Shotgun Surgery | Move Method, Move Field, Inline Class |
| Parallel Inheritance Hierarchies | Move Method, Move Field |
| Comments | Extract Method, Rename Method, Introduce Assertion |
| Duplicate Code | Extract Method, Extract Class, Pull Up Method, Form Template Method |
| Lazy Class | Inline Class, Collapse Hierarchy |
| Data Class | Move Method, Encapsulate Field, Encapsulate Collection |
| Dead Code | Delete it |
| Speculative Generality | Collapse Hierarchy, Inline Class, Remove Parameter, Rename Method |
| Feature Envy | Move Method, Move Field, Extract Method |
| Inappropriate Intimacy | Move Method, Move Field, Change Bidirectional Association to Unidirectional, Replace Inheritance with Delegation |
| Message Chains | Hide Delegate |
| Middle Man | Remove Middle Man, Inline Class, Replace Delegation with Inheritance |
| Incomplete Library Class | Introduce Foreign Method, Introduce Local Extension |

---

# Conclusion

This catalog provides the complete vocabulary for discussing code quality in Python. When you identify a smell, you know exactly which technique(s) to apply. When you apply a technique, you know which smell(s) you're eliminating.

Use this reference while coding to internalize these patterns until they become second nature.
