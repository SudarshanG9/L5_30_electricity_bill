# Lab 5: Static Code Analysis — Electricity Bill Calculator

**Your file:** `electricity_bill.py`

Follow the lab handout for the full instructions.

## About the program

A slab-based billing tool. It reads meter readings from a small XML block, works out units used, applies the tariff slabs, fixed charge, tax and any extra fees, and saves the bills to bills.json.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:

   ```
   python electricity_bill.py
   ```

   It runs a short demonstration and needs no input. Note what it prints, so you can check that it still behaves the same after your fixes.

2. **Install the tools:**

   ```
   python -m pip install pylint bandit flake8
   ```

3. **Run the analysis and save the reports:**

   ```
   python -m pylint electricity_bill.py > pylint_report.txt
   python -m bandit -r electricity_bill.py > bandit_report.txt
   python -m flake8 electricity_bill.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | B605 — Shell injection | Bandit · **High** | 63 | `os.system("curl http://" + meterIp + "/reading")` passes a user-controlled string straight to the shell, enabling command injection (CWE-78). | Replaced `os.system` with `urllib.request.urlopen()` so no shell is ever invoked; added regex + `ipaddress` validation to reject addresses containing shell meta-characters. |
   | B314 — Unsafe XML parse | Bandit · **Medium** | 18 | `xml.etree.ElementTree.fromstring()` is vulnerable to XML bomb and XXE attacks (CWE-20). | Swapped the import and call for `defusedxml.ElementTree.fromstring()`, which safely rejects malicious XML inputs. |
   | W0102 — Mutable default | Pylint · **Warning** | 42 | `generateBill(…, extras={})` — the same dict object is shared across every call that omits `extras`, silently corrupting data. | Changed default to `extras=None`; added `if extras is None: extras = {}` inside the function body so each call gets a fresh dict. |
   | W0613 — Unused argument | Pylint · **Warning** | 50 | `averageBill(currency)` — the `currency` parameter is declared but never read, creating dead code. | Removed the unused parameter and updated the single call site. |
   | W1514 — Missing encoding | Pylint · **Warning** | 57 | `open(fileName, "w")` — no explicit encoding specified; output is locale-dependent and may differ across machines. | Added `encoding="utf-8"` to the `open()` call. |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

- `electricity_bill.py`: your cleaned version, with at least 4 issues fixed.
- `issues.md`: the completed issue table.
- `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.
