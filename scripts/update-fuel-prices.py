#!/usr/bin/env python3
"""
Weekly fuel price updater.
Sources:
  - EIA.gov        → US national average (requires EIA_API_KEY env var)
  - EU Oil Bulletin → All 27 EU countries via stable EC download URL (no key)
  - Everything else → left unchanged from previous week

Usage:
  EIA_API_KEY=your_key python3 scripts/update-fuel-prices.py
"""

import json
import os
import sys
import io
import requests
import openpyxl
from datetime import date

PRICES_FILE = "fuel-prices.json"
TIMEOUT = 20

# Stable URL — always serves the latest weekly bulletin (prices WITH taxes)
EU_BULLETIN_URL = (
    "https://energy.ec.europa.eu/document/download/"
    "264c2d0f-f161-4ea3-a777-78faae59bea0_en"
)

# Country name → ISO code (as written in the EU Oil Bulletin XLSX, column A)
EU_NAME_TO_CODE = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR",
    "Cyprus": "CY", "Czech Republic": "CZ", "Czechia": "CZ", "Denmark": "DK",
    "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE",
    "Greece": "GR", "Hungary": "HU", "Ireland": "IE", "Italy": "IT",
    "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT",
    "Netherlands": "NL", "Poland": "PL", "Portugal": "PT", "Romania": "RO",
    "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES", "Sweden": "SE",
}

# Countries whose JSON prices are in local currency (not EUR).
# The Oil Bulletin reports in EUR — skip these so we don't corrupt local values.
NON_EUR_COUNTRIES = {"BG", "CZ", "DK", "HU", "PL", "RO", "SE"}


def load_prices():
    with open(PRICES_FILE, "r") as f:
        return json.load(f)


def save_prices(data):
    with open(PRICES_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {PRICES_FILE}")


def fetch_us_prices(api_key):
    """Returns (petrol_per_litre, diesel_per_litre) in USD, or (None, None)."""
    base = (
        "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
        "?api_key={key}&frequency=weekly&data[0]=value"
        "&facets[duoarea][]=NUS&facets[product][]={product}"
        "&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
    )
    results = {}
    for label, product in [("petrol", "EPM0"), ("diesel", "EPD2D")]:
        try:
            r = requests.get(base.format(key=api_key, product=product), timeout=TIMEOUT)
            r.raise_for_status()
            per_gallon = float(r.json()["response"]["data"][0]["value"])
            per_litre  = round(per_gallon / 3.78541, 4)
            print(f"  US {label}: ${per_gallon:.3f}/gal → ${per_litre:.4f}/L")
            results[label] = per_litre
        except Exception as e:
            print(f"  ✗ EIA {label} failed: {e}")
    return results.get("petrol"), results.get("diesel")


def fetch_eu_prices():
    """
    Downloads the EU Oil Bulletin XLSX and extracts petrol + diesel prices.
    Prices in the file are EUR per 1000 litres → divide by 1000 for per-litre.
    Returns dict { "DE": {"petrol": 1.75, "diesel": 1.68}, ... }
    """
    try:
        r = requests.get(EU_BULLETIN_URL, timeout=TIMEOUT)
        r.raise_for_status()

        wb = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)
        ws = wb.active

        results = {}
        for row in ws.iter_rows(min_row=3, values_only=True):
            country_name = str(row[0]).strip() if row[0] else ""
            code = EU_NAME_TO_CODE.get(country_name)
            if not code:
                continue  # skip aggregates (EU27 average, Euro Area, etc.)
            if code in NON_EUR_COUNTRIES:
                print(f"  {code}: skipped (local currency — not EUR)")
                continue
            try:
                petrol = round(float(row[1]) / 1000, 4)  # Col B: EUR/1000L → EUR/L
                diesel = round(float(row[2]) / 1000, 4)  # Col C: EUR/1000L → EUR/L
                results[code] = {"petrol": petrol, "diesel": diesel}
                print(f"  {code}: petrol={petrol:.4f} diesel={diesel:.4f} EUR/L")
            except Exception as e:
                print(f"  ✗ {code} ({country_name}): {e}")

        return results

    except Exception as e:
        print(f"  ✗ EU Oil Bulletin failed: {e}")
        return {}


def main():
    print(f"\n{'='*50}")
    print(f"Fuel price update — {date.today()}")
    print(f"{'='*50}\n")

    prices = load_prices()
    updated = []

    # ── US via EIA ────────────────────────────────────────────────────────────
    eia_key = os.environ.get("EIA_API_KEY", "").strip()
    if eia_key:
        print("→ Fetching US prices from EIA...")
        petrol, diesel = fetch_us_prices(eia_key)
        if petrol is not None:
            prices["countries"]["US"]["petrol"] = petrol
            updated.append("US petrol")
        if diesel is not None:
            prices["countries"]["US"]["diesel"] = diesel
            updated.append("US diesel")
    else:
        print("→ EIA_API_KEY not set — skipping US")

    # ── EU via Oil Bulletin ───────────────────────────────────────────────────
    print("\n→ Fetching EU prices from EU Oil Bulletin...")
    for code, vals in fetch_eu_prices().items():
        if code in prices["countries"]:
            prices["countries"][code]["petrol"] = vals["petrol"]
            prices["countries"][code]["diesel"] = vals["diesel"]
            updated.append(code)

    # ── Wrap up ───────────────────────────────────────────────────────────────
    prices["_meta"]["updated"] = str(date.today())

    print(f"\n{'='*50}")
    if updated:
        print(f"✓ Updated: {', '.join(updated)}")
    else:
        print("⚠ No prices updated — all sources failed or no API key.")
    print(f"{'='*50}\n")

    save_prices(prices)
    return 0


if __name__ == "__main__":
    sys.exit(main())
