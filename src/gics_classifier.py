"""
gics_classifier.py
──────────────────
Classifies companies into GICS Sector, Industry Group, and Industry using a
local CSV cache before falling back to the Claude API.

Cache file: data/raw/gics_lookup.csv
    Columns: company_name, gics_sector, gics_industry_group, gics_industry

Lookup logic:
    1. Check gics_lookup.csv for an exact match on company_name.
    2. If found  → return cached values (no API call).
    3. If missing → call Claude Haiku, then append result to the cache.

Usage:
    from gics_classifier import classify_gics

    # Single company
    result = classify_gics(
        company_name="Apple Inc.",
        country="United States",
        stock_symbol="AAPL"
    )

"""

import csv
import json
import os
import re
from pathlib import Path

import anthropic

# ── Paths ─────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = _PROJECT_ROOT / "vault.txt"
LOOKUP_PATH = Path("data/raw/gics_lookup.csv")

LOOKUP_COLUMNS = [
    "company_name",
    "gics_sector",
    "gics_industry_group",
    "gics_industry",
]
# ── Client ──────────────────────────────────────────────────────


def _load_api_key() -> str:
    if VAULT_PATH.exists():
        for line in VAULT_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError("API key not found in vault.txt or ANTHROPIC_API_KEY env var.")
    return key


client = anthropic.Anthropic(api_key="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")


# ── Prompt ───────────────────────────────────────

SYSTEM_PROMPT = """\
You are a GICS (Global Industry Classification Standard) expert.
Given a company name, country, and stock symbol, return its Sector, \
Industry Group, and Industry classification.

Respond ONLY with a JSON object. No explanation, no markdown, no preamble, no anotation or ''.

Required format:
{
  "gics_sector": "<name>",
  "gics_industry_group": "<name>",
  "gics_industry": "<name>"
}

Valid GICS sectors (use exactly these names):
Energy | Materials | Industrials | Consumer Discretionary | Consumer Staples |
Health Care | Financials | Information Technology | Communication Services |
Utilities | Real Estate
"""


# ── Cache helpers ────────
def _load_lookup() -> dict[str, dict]:
    """
    Loads gics_lookup.csv into a dict keyed by lowercase company_name.
    Returns an empty dict if the file does not exist yet.
    """
    lookup = {}
    if not LOOKUP_PATH.exists():
        return lookup

    with LOOKUP_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row["company_name"].strip().lower()
            lookup[key] = {
                "gics_sector": row["gics_sector"],
                "gics_industry_group": row["gics_industry_group"],
                "gics_industry": row["gics_industry"],
                "gics_source": "cache",
            }
    return lookup


def _append_to_lookup(
        company_name: str,
        gics_sector: str,
        gics_industry_group: str,
        gics_industry: str) -> None:
    """
    Appends a single row to gics_lookup.csv.
    Creates the file with headers if it does not exist.
    """
    LOOKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not LOOKUP_PATH.exists()

    with LOOKUP_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOOKUP_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "company_name": company_name,
            "gics_sector": gics_sector,
            "gics_industry_group": gics_industry_group,
            "gics_industry": gics_industry,
        })


# ── API call
def _call_api(company_name: str, country: str, stock_symbol: str) -> tuple[str, str, str]:
    """
    Calls Claude Haiku and returns (gics_sector, gics_industry_group, gics_industry).
    Raises ValueError if the response cannot be parsed.
    """
    user_message = (
        f"Company: {company_name}\n"
        f"Country: {country}\n"
        f"Stock symbol: {stock_symbol}"
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in API response: {raw}")
    raw = match.group()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse API response as JSON: {raw}") from e

    return data["gics_sector"], data["gics_industry_group"], data["gics_industry"]


# ── Public interface
def classify_gics(company_name: str, country: str, stock_symbol: str) -> dict:
    """
    Returns gics_sector, gics_industry_group, and gics_industry for a company.

    Checks the local cache first. Falls back to the Claude API on a miss
    and persists the result to the cache before returning.

    Return fields:
        gics_sector         (str)
        gics_industry_group (str)
        gics_industry       (str)
        gics_source         "cache" | "api"
    """
    lookup = _load_lookup()
    cache_key = company_name.strip().lower()

    # ── Cache hit
    if cache_key in lookup:
        return lookup[cache_key]

    # ── Cache miss → API
    gics_sector, gics_industry_group, gics_industry = _call_api(company_name, country, stock_symbol)

    _append_to_lookup(
        company_name=company_name,
        gics_sector=gics_sector,
        gics_industry_group=gics_industry_group,
        gics_industry=gics_industry,
    )

    return {
        "gics_sector": gics_sector,
        "gics_industry_group": gics_industry_group,
        "gics_industry": gics_industry,
        "gics_source": "api",
    }


# ── Example

if __name__ == "__main__":
    result = classify_gics(
        company_name="pursuit attractions and hospitality",
        country="United States",
        stock_symbol="PRSU"
    )
    print(json.dumps(result, indent=2))
