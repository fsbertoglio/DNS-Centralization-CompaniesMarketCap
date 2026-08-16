# DNS Sovereignty Research
### Mapping Economic Centralization of DNS Infrastructure Across the World's Largest Companies

---

## Overview

This project investigates **digital sovereignty** through the lens of DNS infrastructure concentration among the world's largest companies by revenue. The central hypothesis is that a small number of infrastructure providers — nameservers, registrars, and email services — hold technical control over a disproportionate share of global economic activity.

**Universe of analysis:** The 10,000 largest companies by revenue, sourced from the [Companies Market Cap](https://companiesmarketcap.com) portal.

---

## Folder Structure

```
dns-sovereignty/
│
├── data/
│   ├── raw/                        # Raw data — never modify directly
│   │   ├── companies_marketcap/    # HTMLs and CSVs downloaded from the portal
│   │   └── dns_records/            # Raw DNS query responses
│   │
│   ├── interim/                    # Data in transformation between stages
│   │   ├── companies_clean.csv     # Cleaned companies with identified domains
│   │   └── dns_raw.jsonl           # Extracted DNS records, not yet aggregated
│   │
│   └── processed/                  # Data ready for analysis
│       ├── dns_enriched.parquet    # DNS + metadata (ASN, country, provider)
│       └── analysis_dataset.parquet
│
├── notebooks/
│   ├── 01_scraping/
│   ├── 02_domain_identification/
│   ├── 03_dns_extraction/
│   ├── 04_enrichment/
│   └── 05_analysis/
│
├── src/                            # Reusable Python modules
│   ├── scrapers/                   # Companies Market Cap collection logic
│   ├── dns/                        # DNS resolution wrapper (dnspython)
│   └── utils/                      # General helpers (logging, I/O, retries)
│
├── outputs/
│   ├── figures/                    # Exported charts and maps
│   ├── tables/                     # Result tables
│   └── report/                     # Final research report
│
├── config/
│   └── settings.yaml               # Rate limits, DNS resolvers, paths, TLDs
│
└── requirements.txt
```

---

## Data Pipeline

The project is organized into **5 sequential stages**, each corresponding to a folder inside `notebooks/`. Data flows as follows:

```
Companies Market Cap
      │
      ▼
[01] Scraping ──────────────► companies_raw.csv
      │
      ▼
[02] Domain Identification ──► companies_clean.csv  (+columns: domain, domain_source)
      │
      ▼
[03] DNS Extraction ─────────► dns_raw.jsonl
      │
      ▼
[04] Enrichment ─────────────► dns_enriched.parquet  (ASN, registrar, geo)
      │
      ▼
[05] Analysis ───────────────► outputs/figures/ + outputs/report/
```

---

## Notebooks by Stage

### 01 — Scraping (`notebooks/01_scraping/`)

Collection and structuring of the company list from the Companies Market Cap portal.

| Notebook | Description |
|---|---|
| `01a_fetch_companies.ipynb` | Navigates portal pagination, respects rate limits, and saves raw pages to `data/raw/companies_marketcap/` |
| `01b_parse_companies.ipynb` | Extracts the structured table from raw pages and generates `companies_raw.csv` |

**Output:** `data/raw/companies_marketcap/`, `data/interim/companies_raw.csv`

---

### 02 — Domain Identification (`notebooks/02_domain_identification/`)

The most critical stage of the pipeline. Combines multiple strategies to associate a primary domain with each company. Every identified domain receives a `domain_source` column indicating its origin — essential for methodological traceability.

| Notebook | Strategy |
|---|---|
| `02a_direct_lookup.ipynb` | Attempts to infer the domain directly from the company name (e.g. `apple.com`) and validates it via HTTP request |
| `02b_search_api.ipynb` | Queries a Search API (Google or Bing) with the company name to find the official website |
| `02c_wikidata_lookup.ipynb` | Queries Wikidata, which has a structured `official website` field for most large corporations |
| `02d_merge_domains.ipynb` | Consolidates all three sources, resolves conflicts by priority order, and produces the final validated domain dataset |

> **Expected coverage:** Wikidata + Search API cover ~85% of the companies in the analysis universe. Remaining cases are resolved manually or flagged and discarded.

**Output:** `data/interim/companies_clean.csv`

---

### 03 — DNS Extraction (`notebooks/03_dns_extraction/`)

Bulk DNS queries for all identified domains.

| Notebook | Description |
|---|---|
| `03a_resolve_dns.ipynb` | Performs A, NS, MX, SOA, and TXT record queries using multiple resolvers (8.8.8.8, 1.1.1.1, 9.9.9.9) to avoid infrastructure bias |
| `03b_validate_dns.ipynb` | Filters and classifies failures: `NXDOMAIN`, timeout, missing MX record, etc. Generates a coverage log |

> **Methodological note:** Using multiple resolvers is deliberate — a single resolver would introduce bias, as providers like Cloudflare and Google have incentives to respond in subtly different ways.

**Output:** `data/interim/dns_raw.jsonl`

---

### 04 — Enrichment (`notebooks/04_enrichment/`)

Associates infrastructure metadata with the raw DNS records.

| Notebook | Description |
|---|---|
| `04a_asn_lookup.ipynb` | Converts IPs to ASN and organization name (e.g. `AS13335 Cloudflare`, `AS16509 Amazon`) |
| `04b_registrar_lookup.ipynb` | Queries WHOIS to identify the domain registrar and registration date |
| `04c_geo_lookup.ipynb` | Geolocates nameserver and mail server IPs by country |
| `04d_merge_enrichment.ipynb` | Merges all metadata into the DNS dataset and generates the final enriched file |

**Output:** `data/processed/dns_enriched.parquet`

---

### 05 — Analysis (`notebooks/05_analysis/`)

Concentration and sovereignty analyses built on the enriched dataset.

| Notebook | Analytical Focus |
|---|---|
| `05a_ns_concentration.ipynb` | Nameserver concentration — who controls DNS resolution for the world's largest companies |
| `05b_mx_concentration.ipynb` | Email service concentration (Google Workspace vs Microsoft 365 vs self-hosted) |
| `05c_registrar_concentration.ipynb` | Concentration by domain registrar |
| `05d_geo_sovereignty.ipynb` | Geographic dependency: cross-analysis between company headquarters country and DNS infrastructure country |
| `05e_cross_analysis.ipynb` | Composite cross-analyses: sector × provider, revenue bracket × concentration, region × sovereignty |

**Output:** `outputs/figures/`, `outputs/tables/`, `outputs/report/`

---

## Python Modules (`src/`)

| Module | Description |
|---|---|
| `src/scrapers/marketcap.py` | Pagination and collection logic for Companies Market Cap |
| `src/dns/resolver.py` | Wrapper over `dnspython` with retry, configurable timeout, and multi-resolver support |
| `src/dns/parser.py` | Normalizes DNS records into tabular format |
| `src/utils/io.py` | Read/write helpers (CSV, JSONL, Parquet) |
| `src/utils/logging.py` | Standardized log configuration per pipeline stage |

---

## Configuration (`config/settings.yaml`)

Centralizes all operational parameters for the pipeline:

```yaml
scraping:
  rate_limit_seconds: 2
  max_retries: 3

dns:
  resolvers:
    - "8.8.8.8"    # Google
    - "1.1.1.1"    # Cloudflare
    - "9.9.9.9"    # Quad9
  timeout_seconds: 5
  record_types: [A, NS, MX, SOA, TXT]

domain_identification:
  priority_order: [wikidata, search_api, direct_lookup]
  tld_priority: [.com, .net, .org, .io]

paths:
  raw: data/raw/
  interim: data/interim/
  processed: data/processed/
  outputs: outputs/
```

---

## Key Dependencies

```
dnspython          # Programmatic DNS resolution
pandas             # Tabular data manipulation
pyarrow            # Parquet read/write
requests           # HTTP requests
beautifulsoup4     # HTML parsing (scraping)
SPARQLWrapper      # Wikidata SPARQL queries
python-whois       # WHOIS queries
ipwhois            # ASN lookup by IP
geopandas          # Geospatial analyses
matplotlib / seaborn / plotly  # Visualizations
jupyter            # Notebook environment
```

---

## Methodological Decisions

- **Parquet format** for processed data — efficient for analytical queries across 10k companies × multiple DNS records.
- **`domain_source` as a mandatory column** — allows auditing and questioning the origin of every identified domain.
- **Multiple DNS resolvers** — reduces infrastructure bias in the extraction stage.
- **Raw data preserved** — the `data/raw/` folder is never modified, guaranteeing full pipeline reproducibility.

---

## Project Status

| Stage | Status |
|---|---|
| 01 — Scraping | 🔲 Not started |
| 02 — Domain Identification | 🔲 Not started |
| 03 — DNS Extraction | 🔲 Not started |
| 04 — Enrichment | 🔲 Not started |
| 05 — Analysis | 🔲 Not started |