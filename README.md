# Python Clean Code Skill

A comprehensive skill for writing clean Python code. This skill provides 23 code smells and 70 refactoring techniques expressed in idiomatic Python.

## What This Skill Does

This skill acts as **proactive clean code enforcement** when writing Python. Instead of reviewing code after it's written and suggesting fixes, it applies refactoring principles *as you write*, ensuring zero technical debt from the start.

### Key Features

- ✅ **Proactive application** of all 23 code smells as constraints
- ✅ **70 refactoring techniques** translated to Python idioms
- ✅ **Comprehensive reference** with examples

## Contents

```
python-clean-code/
├── SKILL.md                    # Main skill file loaded by Claude
├── README.md                   # This file
├── references/
│   └── refactoring-catalog.md  # Clean code catalog: 23 smells + 70 techniques
└── assets/
    └── quick-reference.md      # Visual quick reference chart
```

## How It Works

### For Claude Code Users

When this skill is installed, Claude will automatically:

1. **Apply clean code principles proactively** when writing any Python code
2. **Name refactoring techniques** as they're applied (e.g., "Applying Extract Method...")
3. **Prevent code smells** before they're written
4. **Suggest techniques** when reviewing existing code

### Installation

```bash
# If you have the .skill file
claude-code install python-clean-code.skill

# Or manually copy to your skills directory
cp -r python-clean-code ~/.claude/skills/
```

### Usage Examples

#### Writing New Code
```python
# ❌ Without skill: Claude might write this
def process_order(order):
    if order['status'] == 'pending':
        # 30 lines of processing logic...

# ✅ With skill: Claude writes this automatically
def process_order(order):
    if not is_pending(order):
        return
    validate_order(order)
    calculate_totals(order)
    apply_discounts(order)
    finalize_order(order)

def is_pending(order):
    return order['status'] == 'pending'

def validate_order(order):
    # Focused validation logic
```

#### Reviewing Existing Code
When you ask Claude to review code, it will:
- Identify specific smells by name
- Suggest specific refactoring techniques
- Show before/after examples

## Reference Materials

### Quick Reference Chart
See `assets/quick-reference.md` for:
- Visual guide to all 23 smells
- Cheat sheet for all 70 techniques
- Decision tree for choosing refactorings
- Python-specific patterns

### Complete Catalog
See `references/refactoring-catalog.md` for:
- Detailed explanation of each smell
- Step-by-step refactoring techniques
- Python code examples for each
- Smell-to-technique mapping table

## The 23 Code Smells

### Bloaters
1. Long Method
2. Large Class
3. Primitive Obsession
4. Long Parameter List
5. Data Clumps

### Object-Orientation Abusers
6. Switch Statements
7. Temporary Field
8. Refused Bequest
9. Alternative Classes with Different Interfaces

### Change Preventers
10. Divergent Change
11. Shotgun Surgery
12. Parallel Inheritance Hierarchies

### Dispensables
13. Comments (explaining what)
14. Duplicate Code
15. Lazy Class
16. Data Class
17. Dead Code
18. Speculative Generality

### Couplers
19. Feature Envy
20. Inappropriate Intimacy
21. Message Chains
22. Middle Man
23. Incomplete Library Class

## The 70 Refactoring Techniques

### Composing Methods (9)
Extract Method • Inline Method • Extract Variable • Inline Temp • Replace Temp with Query • Split Temporary Variable • Remove Assignments to Parameters • Replace Method with Method Object • Substitute Algorithm

### Moving Features (8)
Move Method • Move Field • Extract Class • Inline Class • Hide Delegate • Remove Middle Man • Introduce Foreign Method • Introduce Local Extension

### Organizing Data (16)
Self Encapsulate Field • Replace Data Value with Object • Change Value to Reference • Change Reference to Value • Replace Array with Object • Duplicate Observed Data • Change Unidirectional to Bidirectional • Change Bidirectional to Unidirectional • Replace Magic Number with Symbolic Constant • Encapsulate Field • Encapsulate Collection • Replace Type Code with Class • Replace Type Code with Subclasses • Replace Type Code with State/Strategy • Replace Subclass with Fields • Extract Interface

### Simplifying Conditionals (9)
Decompose Conditional • Consolidate Conditional Expression • Consolidate Duplicate Conditional Fragments • Remove Control Flag • Replace Nested Conditional with Guard Clauses • Replace Conditional with Polymorphism • Introduce Null Object • Introduce Assertion • Replace Exception with Test

### Simplifying Method Calls (13)
Rename Method • Add Parameter • Remove Parameter • Separate Query from Modifier • Parameterize Method • Replace Parameter with Explicit Methods • Preserve Whole Object • Replace Parameter with Method Call • Introduce Parameter Object • Remove Setting Method • Hide Method • Replace Constructor with Factory Method • Replace Error Code with Exception

### Dealing with Generalization (15)
Pull Up Field • Pull Up Method • Pull Up Constructor Body • Push Down Method • Push Down Field • Extract Subclass • Extract Superclass • Extract Interface • Collapse Hierarchy • Form Template Method • Replace Inheritance with Delegation • Replace Delegation with Inheritance • Tease Apart Inheritance • Convert Procedural to Objects • Separate Domain from Presentation

## Philosophy

This skill embodies three core principles:

1. **Proactive over Reactive**: Apply techniques as you write, not after code review
2. **Named Techniques**: Think in consistent transformation vocabulary
3. **Zero Technical Debt**: Every line of generated code should be clean from the start

## Tips for Best Results

1. **Let the skill work**: Don't fight its suggestions—it's applying proven techniques
2. **Learn the names**: Understanding technique names helps you think in terms of transformations
3. **Review the examples**: The reference materials show before/after for every technique
4. **Iterate**: Refactoring is continuous—small improvements compound over time

## Common Questions

### Q: Will this make my code more verbose?
A: Initially, yes—more functions and classes. But each piece becomes simpler and more understandable. The overall complexity decreases even as line count increases.

### Q: Should I apply ALL these rules ALL the time?
A: Use judgment. The rules are guidelines, not laws. Small scripts don't need the same rigor as production systems. But in a professional codebase, these rules prevent maintenance nightmares.

### Q: What about performance?
A: Clean code and performance are not opposites. Most refactorings have zero performance impact. When performance matters, measure first, then optimize specific hotspots while keeping the rest clean.

### Q: Isn't this overkill for simple code?
A: Simple code doesn't need these techniques. But "simple" is relative—what seems simple today becomes complex tomorrow when requirements change. These techniques make code resilient to change.

## Credits

Influences:
- **"Dive Into Refactoring"** by Alexander Shvets
- **Python best practices** from PEP 8, PEP 20 (Zen of Python)
- **Type hinting** from PEP 484, PEP 544 (Protocols)

## License

This skill is provided as-is for educational and professional use.

## Contributing

Found an issue? Have a suggestion? Contributions welcome:
- Improve Python idiom translations
- Add more examples to the catalog
- Suggest additional refactoring patterns

---

**Remember**: The goal is not perfect code—it's *maintainable* code that can evolve as requirements change.
