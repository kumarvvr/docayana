---
name: compact-clean-code
description: Rules for writing small, readable, low-ceremony code (short functions, clear names, no dead code, minimal comments). Use when writing, refactoring, or reviewing any code in this project.
---

# Compact Clean Code

Aim: the least code that is obviously correct.

## Rules
- Functions do one thing; aim for under ~20 lines and at most 3-4 parameters (group the rest in a dataclass).
- Names reveal intent: `pending_documents`, not `data2`; booleans read as questions (`is_archived`).
- Return early with guard clauses instead of nested `if`/`else`.
- No dead code, commented-out code, unused params, or speculative abstractions (YAGNI). Add a layer only when a second use exists.
- Don't repeat knowledge (DRY), but tolerate small duplication over a wrong abstraction.
- Prefer comprehensions, `any`/`all`, `dict.get`, unpacking, and stdlib helpers over manual loops when clearer.
- Keep side effects at the edges; pure functions in the middle.
- Constants over magic numbers/strings; one source of truth per constant.
- Comments explain *why*, never *what*. Docstrings only on public APIs and only when the signature isn't enough.
- One level of abstraction per function: don't mix HTTP parsing, business rules, and persistence in one body.
- Fail fast with specific exceptions; don't return `None` to signal errors.

## Example
```python
# Before
def process(d):
    if d is not None:
        if d.status == "active":
            if len(d.pages) > 0:
                return True
    return False

# After
def is_publishable(doc: Document) -> bool:
    return doc.status is Status.ACTIVE and bool(doc.pages)
```

## Review checklist
- Can any line, branch, or parameter be deleted without changing behavior?
- Would a new reader understand each function from its name and signature?
