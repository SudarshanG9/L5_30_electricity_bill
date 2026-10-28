# Reflection — Lab 5: Static Code Analysis

## Question 1 — What is the difference between a linting error and a security vulnerability? Give one example of each from your report.

A **linting error** is a style or quality violation that makes code harder to read, maintain, or reason about, but does not by itself allow an attacker to cause harm.  
A **security vulnerability** is a flaw that could be exploited by a malicious actor to compromise the confidentiality, integrity, or availability of a system.

**Linting example (Flake8 E225):** The original code wrote `total=sum(bill["amount"] for bill in bills)` without spaces around the `=` operator. This violates PEP 8 style, but the program still produces the correct answer. It is purely a readability issue.

**Security example (Bandit B605 — shell injection):** The original `sync_meter` function called `os.system("curl http://" + meterIp + "/reading")`. If an attacker controlled the value of `meterIp` (e.g., by injecting `; rm -rf /`), the shell would execute the injected command with the same privileges as the Python process. This is a genuine, exploitable vulnerability (CWE-78).

---

## Question 2 — Why is a mutable default argument dangerous in Python? How did you fix it?

In Python, default argument values are evaluated **once** when the function is defined, not each time the function is called. This means a mutable default (like a `dict` or `list`) is shared across every call that relies on the default.

In the original code:

```python
def generateBill(meterId, units, taxRate=0.05, extras={}):
```

If any caller mutated `extras` (e.g., `extras["penalty"] = 10`), that change would persist into the next call that omits `extras`, silently corrupting results for subsequent bills.

**Fix:** Use `None` as the sentinel default and create a fresh container inside the function body:

```python
def generate_bill(meter_id, units, tax_rate=0.05, extras=None):
    if extras is None:
        extras = {}
```

This guarantees each call gets its own independent dict.

---

## Question 3 — What are two ways that hardcoded passwords create risk, and how did you mitigate them?

1. **Source-code exposure:** When code is pushed to a repository (even a private one), the password travels with every clone, fork, and commit. If the repository is ever made public, or a contributor's machine is compromised, the credential leaks permanently — git history retains it even after deletion.

2. **No rotation path:** A password embedded in source requires a code change and redeployment to rotate. In a real incident, slow rotation significantly increases the exposure window.

**Mitigation applied:**  
Changed `CLERK_PASSWORD = "bill-desk-demo"` to:

```python
CLERK_PASSWORD = os.environ.get("CLERK_PASSWORD", "bill-desk-demo")
```

A real deployment sets the `CLERK_PASSWORD` environment variable to the actual secret; the fallback string is documented in a comment as a demo-only placeholder that must never be used in production. This keeps secrets out of source control and allows rotation without a code change.

---

## Question 4 — Reflecting on the process, what would you do differently if you were writing this code from scratch to avoid these issues?

**Use a linter and security scanner from day one.** Integrating Pylint, Flake8, and Bandit into a pre-commit hook or CI pipeline means issues are caught at the moment they are introduced rather than accumulated over time. Fixing a warning immediately is far cheaper than untangling a dozen inter-related issues later.

**Follow naming conventions consistently.** Choosing snake_case from the start avoids bulk renaming passes that risk introducing call-site mismatches.

**Treat any external input as untrusted.** The `sync_meter` function accepted a raw string and passed it directly to a shell command. A secure design would validate and sanitise all external values at the boundary where they enter the program, before they reach any system call.

**Never use mutable defaults.** The idiomatic Python pattern (`None` sentinel) is simple and well-documented. Making it a personal habit eliminates a whole class of subtle bugs.

**Never hardcode secrets.** Environment variables, secret managers, or configuration files outside the repository should be the default choice for any credential, even during early prototyping — it is easy to forget to remove them before a commit.

Overall, the exercise showed that automated tools catch real problems quickly and cheaply. Writing code with these tools in mind from the start, rather than treating analysis as an afterthought, produces cleaner, safer, and more maintainable software.
