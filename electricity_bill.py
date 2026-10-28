"""Electricity billing module.

Reads meter data from an XML string, calculates energy charges using
tiered slabs, generates bills with optional extras and tax, and saves
the results to a JSON file.  A helper function for syncing a meter
over HTTP is also provided.
"""

import ipaddress
import json
import os
import re
import urllib.request

import defusedxml.ElementTree as ET

SLABS = [(100, 3.5), (200, 5.0), (300, 6.5)]
HIGH_RATE = 8.0
FIXED_CHARGE = 75
METER_XML = ("<meters>"
             "<meter id='M1' prev='1200' curr='1350'/>"
             "<meter id='M2' prev='5000' curr='5420'/>"
             "<meter id='M3' prev='800' curr='760'/>"
             "</meters>")
# Load the clerk password from an environment variable so that no real
# credential is ever hard-coded in source.  The fallback value below is
# intentionally a non-secret placeholder used only for local demos; it
# must never be used as a real credential in production.
CLERK_PASSWORD = os.environ.get("CLERK_PASSWORD", "bill-desk-demo")
bills = []


def read_meters(xml_text):
    """Parse meter XML and return a list of (meter_id, previous, current) tuples."""
    root = ET.fromstring(xml_text)
    return [(m.get("id"), int(m.get("prev")), int(m.get("curr")))
            for m in root.findall("meter")]


def calculate_units(previous, current):
    """Return units consumed, or 0 with a warning if the meter went backwards."""
    if current < previous:
        print("Warning: meter reading went backwards")
        return 0
    return current - previous


def energy_charge(units):
    """Calculate the energy charge for the given number of units using tiered slabs."""
    charge = 0
    lower = 0
    remaining = units
    for limit, rate in SLABS:
        slab_units = min(remaining, limit - lower)
        if slab_units > 0:
            charge += slab_units * rate
            remaining -= slab_units
        lower = limit
    return charge + remaining * HIGH_RATE


def generate_bill(meter_id, units, tax_rate=0.05, extras=None):
    """Generate a bill dict for the given meter, append it to bills, and return it.

    Args:
        meter_id: Unique identifier string for the meter.
        units:    Number of units consumed in the billing period.
        tax_rate: Fractional tax rate applied to the total (default 5 %).
        extras:   Optional dict of additional charges, e.g. {"late_fee": 25}.
    """
    if extras is None:
        extras = {}
    amount = energy_charge(units) + FIXED_CHARGE + sum(extras.values())
    bill = {"meter": meter_id, "units": units,
            "amount": round(amount * (1 + tax_rate), 2)}
    bills.append(bill)
    return bill


def average_bill():
    """Return the mean bill amount across all generated bills, or 0 if none exist."""
    if not bills:
        return 0
    return round(sum(bill["amount"] for bill in bills) / len(bills), 2)


def save_bills(file_name="bills.json"):
    """Serialise the global bills list to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=2)


def sync_meter(meter_ip):
    """Fetch the current reading from a meter over HTTP.

    The IP address is validated before use so that shell-injection via a
    malformed address is impossible.  urllib.request is used instead of
    os.system / subprocess so that no shell is ever invoked.
    """
    # Validate: accept only a bare IPv4/IPv6 address or a simple hostname
    # (letters, digits, hyphens, dots) – no ports, paths, or shell meta-chars.
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,253}", meter_ip):
        raise ValueError(f"Invalid meter address: {meter_ip!r}")
    # Extra check: if it looks like a raw IP address it must be a valid one.
    try:
        ipaddress.ip_address(meter_ip)
    except ValueError:
        pass  # It's a hostname – the regex above already sanitised it.
    url = "http://" + meter_ip + "/reading"
    with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
        return response.read()


def main():
    """Run the billing demo: parse meters, generate bills, and save results."""
    for meter_id, previous, current in read_meters(METER_XML):
        units = calculate_units(previous, current)
        generate_bill(meter_id, units)
    generate_bill("M4", 50, extras={"late_fee": 25})
    for bill in bills:
        print(bill["meter"], "used", bill["units"], "units, bill Rs.", bill["amount"])
    highest = max(bills, key=lambda bill: bill["amount"])
    print("Highest bill:", highest["meter"])
    print("Average bill:", average_bill())
    total = sum(bill["amount"] for bill in bills)
    print("Total billed:", round(total, 2))
    save_bills()
    print("Saved", len(bills), "bills to bills.json")


main()
