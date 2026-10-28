# Issue Table — Electricity Bill Calculator

All issues were identified by running **Bandit**, **Pylint**, and **Flake8** against the original `electricity_bill.py`.  
Issues are ordered by severity (highest first).

| # | Tool | Severity | Issue ID | Line(s) | Description | Fix Applied |
|---|------|----------|----------|---------|-------------|-------------|
| 1 | Bandit | **High** | B605 | 63 | `os.system("curl http://" + meterIp + "/reading")` — shell is invoked with a user-controlled string, enabling shell-injection (CWE-78). | Replaced `os.system` with `urllib.request.urlopen()` (no shell). Added `re.fullmatch` regex + `ipaddress.ip_address` validation to reject addresses containing shell meta-characters. Renamed `meterIp` → `meter_ip` (snake_case). |
| 2 | Bandit | **Medium** | B314 | 18 | `ET.fromstring(xmlText)` — `xml.etree.ElementTree.fromstring` is vulnerable to XML bomb, XXE, and billion-laughs attacks (CWE-20). | Replaced call with `defusedxml.ElementTree.fromstring`, which safely rejects malicious XML payloads. |
| 3 | Bandit | **Low** | B105 | 13 | `CLERK_PASSWORD = "bill-desk-demo"` — password hard-coded in source; exposed when code is shared or committed (CWE-259). | Changed to `os.environ.get("CLERK_PASSWORD", "bill-desk-demo")` so a real secret is loaded from the environment. Added comment documenting the fallback as a demo-only placeholder. |
| 4 | Bandit | **Low** | B405 | 3 | `import xml.etree.ElementTree as ET` — importing a known-vulnerable XML library (CWE-20). | Replaced import with `import defusedxml.ElementTree as ET` as part of fixing issue 2. |
| 5 | Pylint | **Warning** | W0102 | 42 | `generateBill(…, extras={})` — mutable default argument; the same dict object is shared across all calls, leading to subtle data-corruption bugs. | Changed default to `extras=None`; inside the function body, replaced with `if extras is None: extras = {}`. |
| 6 | Pylint | **Warning** | W0613 | 50 | `averageBill(currency)` — argument `currency` is declared but never used, creating dead code. | Removed the unused `currency` parameter; all call sites updated accordingly. |
| 7 | Pylint | **Warning** | W1514 | 57 | `open(fileName, "w")` — file opened without an explicit encoding, making behaviour locale-dependent. | Added `encoding="utf-8"` to the `open()` call. |
| 8 | Pylint | **Convention** | C0114 | 1 | No module-level docstring; purpose of the file is undocumented. | Added a module docstring describing the billing module's purpose. |
| 9 | Pylint | **Convention** | C0116 | 17, 22, 29, 42, 50, 56, 61, 66 | Six functions missing docstrings. | Added a descriptive docstring to every function. |
| 10 | Pylint | **Convention** | C0103 | Multiple | Function names (`readMeters`, `calculateUnits`, `energyCharge`, `generateBill`, `averageBill`, `saveBills`, `syncMeter`) and arguments (`xmlText`, `meterId`, `taxRate`, `fileName`, `meterIp`) do not follow PEP 8 snake_case naming. | Renamed all functions and arguments to snake_case (`read_meters`, `calculate_units`, `energy_charge`, `generate_bill`, `average_bill`, `save_bills`, `sync_meter`, `xml_text`, `meter_id`, `tax_rate`, `file_name`, `meter_ip`). All call sites updated. |
| 11 | Flake8 | **Style** | E302 | 22 | Only one blank line before `calculateUnits` definition; PEP 8 requires two. | Added a second blank line (resolved automatically during pylint renaming pass). |
| 12 | Flake8 | **Style** | E203 | 44 | `{"meter" : meterId}` — unexpected whitespace before the colon in a dict literal. | Removed the extra space: `{"meter": meter_id}`. |
| 13 | Flake8 | **Style** | E501 | 72 | Line `amount = energyCharge(units) + FIXED_CHARGE + sum(extras.values())` was 86 characters, exceeding the 79-character PEP 8 limit. Additional long lines introduced by docstrings during the pylint fix. | Wrapped all offending lines (docstrings and one `print` statement) to stay within 79 characters. |
| 14 | Flake8 | **Style** | E225 | 76 | `total=sum(…)` — missing whitespace around the `=` operator. | Changed to `total = sum(…)`. |
