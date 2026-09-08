#!/usr/bin/env python3
"""
Ferramenta para buscar e validar websites de empresas em massa.

Pode ser usada de duas formas:
  1. Linha de comando:  python company_website_finder.py empresas.csv batch
  2. Dentro de um notebook (Jupyter/Colab):

     from company_website_finder import find_websites_sync, find_websites_batch, load_companies_from_csv

     companies = load_companies_from_csv("empresas.csv")
     results = find_websites_sync(companies[:20])   # rápido, poucas empresas
     # ou
     results = find_websites_batch(companies)        # Batch API, 50% desconto, lista grande

Nenhuma variável de ambiente é exigida na importação do módulo — a API key só
é checada quando uma função que realmente chama a API é executada, então é
seguro fazer `import company_website_finder` mesmo sem a key configurada.
"""

import json
import csv
import os
import time
from typing import Optional, Iterable

import anthropic

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

DEFAULT_MODEL = "claude-3-5-haiku-20241022"  # rápido e barato


def _get_client(api_key: Optional[str] = None) -> anthropic.Anthropic:
    """Cria o client Anthropic. Só falha aqui (uso tardio), não na importação."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "ANTHROPIC_API_KEY não configurada. Defina a variável de ambiente "
            "ou passe api_key='...' diretamente na função."
        )
    return anthropic.Anthropic(api_key=key)


# ============================================================================
# CARREGAMENTO DE DADOS
# ============================================================================

def load_companies_from_csv(filepath: str) -> list[dict]:
    """Carrega lista de empresas de um CSV.

    Colunas reconhecidas (todas opcionais exceto o nome):
      - company_name (ou name)      -> obrigatório
      - website                     -> opcional
      - ticker_symbol (ou ticker)   -> opcional
      - country
      - industry
    """
    companies = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append({
                "name": (row.get("company_name") or row.get("name") or "").strip(),
                "website": (row.get("website") or "").strip() or None,
                "ticker_symbol": (row.get("ticker_symbol") or row.get("ticker") or "").strip() or None,
                "country": (row.get("country") or "").strip() or None,
                "industry": (row.get("industry") or "").strip() or None,
            })
    return companies


def companies_from_dataframe(df) -> list[dict]:
    """Conveniência para notebooks: converte um pandas.DataFrame em lista de dicts.

    Espera colunas com os mesmos nomes aceitos em load_companies_from_csv
    (company_name/name, website, ticker_symbol/ticker, country, industry).
    """
    records = df.to_dict(orient="records")
    companies = []
    for row in records:
        companies.append({
            "name": str(row.get("company_name") or row.get("name") or "").strip(),
            "website": (str(row["website"]).strip() if row.get("website") not in (None, "", float("nan")) else None),
            "ticker_symbol": (str(row.get("ticker_symbol") or row.get("ticker") or "").strip() or None),
            "country": (str(row.get("country")).strip() if row.get("country") else None),
            "industry": (str(row.get("industry")).strip() if row.get("industry") else None),
        })
    return companies


def _company_context(company: dict) -> str:
    parts = [f"Empresa: {company['name']}"]
    if company.get("ticker_symbol"):
        parts.append(f"Ticker: {company['ticker_symbol']}")
    if company.get("country"):
        parts.append(f"País: {company['country']}")
    if company.get("industry"):
        parts.append(f"Indústria: {company['industry']}")
    return ", ".join(parts)


def _build_prompt(company: dict) -> str:
    context = _company_context(company)
    if company.get("website"):
        return f"""Valide este website da empresa:
{context}
URL fornecida: {company['website']}

1. Confirme se a URL funciona e pertence à empresa (use o ticker, se fornecido, para desambiguar).
2. Se não funcionar, procure o website oficial correto.
3. Retorne APENAS um JSON: {{"status": "valid"|"incorrect"|"not_found", "website": "URL_atualizada_ou_corrigida"}}"""
    else:
        return f"""Encontre o website oficial desta empresa:
{context}

Use o ticker (se houver) para confirmar que é a empresa certa (ex: capital aberto na bolsa correspondente).
Use web search se necessário. Retorne APENAS um JSON: {{"status": "found"|"not_found", "website": "URL_do_website_ou_null"}}"""


# ============================================================================
# MODO NOTEBOOK / SÍNCRONO — chamável diretamente em uma célula
# ============================================================================

def find_website(company: dict, use_web_search: bool = True,
                  model: str = DEFAULT_MODEL, api_key: Optional[str] = None) -> dict:
    """Busca/valida o website de UMA empresa. Retorna o dict da empresa atualizado.

    Uso em notebook:
        result = find_website({"name": "Embraer", "ticker_symbol": "EMBR3"})
    """
    client = _get_client(api_key)
    prompt = _build_prompt(company)
    tools = [{"type": "web_search_20250305"}] if use_web_search else []

    response = client.messages.create(
        model=model,
        max_tokens=200,
        tools=tools,
        messages=[{"role": "user", "content": prompt}],
    )

    text_content = next((b.text for b in response.content if hasattr(b, "text")), None)
    out = dict(company)
    try:
        parsed = json.loads(text_content)
        out["website_status"] = parsed.get("status")
        out["website_updated"] = parsed.get("website")
    except Exception:
        out["website_status"] = "error"
        out["website_updated"] = None
        out["_raw_response"] = text_content
    return out


def find_websites_sync(companies: list[dict], use_web_search: bool = True,
                        model: str = DEFAULT_MODEL, api_key: Optional[str] = None,
                        progress: bool = True) -> list[dict]:
    """Processa uma lista de empresas de forma síncrona (uma a uma).

    Bom para notebooks e listas pequenas/médias (até ~200 empresas) onde você
    quer ver o resultado na hora. Para listas grandes, prefira find_websites_batch.

    Uso em notebook:
        companies = load_companies_from_csv("empresas.csv")
        results = find_websites_sync(companies[:50])
        import pandas as pd
        pd.DataFrame(results)
    """
    client = _get_client(api_key)  # valida a key uma vez, cedo
    results = []
    for i, company in enumerate(companies, 1):
        if progress and i % 10 == 0:
            print(f"Processadas {i}/{len(companies)} empresas...")
        results.append(find_website(company, use_web_search=use_web_search, model=model, api_key=api_key))
    return results


# ============================================================================
# MODO BATCH — 50% de desconto, ideal para listas grandes (500-5000+)
# ============================================================================

def create_batch_requests(companies: list[dict], model: str = DEFAULT_MODEL) -> list[dict]:
    requests = []
    for i, company in enumerate(companies):
        requests.append({
            "custom_id": f"company_{i}_{(company['name'] or 'unnamed')[:20].replace(' ', '_')}",
            "params": {
                "model": model,
                "max_tokens": 200,
                "messages": [{"role": "user", "content": _build_prompt(company)}],
            },
        })
    return requests


def submit_batch_job(companies: list[dict], model: str = DEFAULT_MODEL,
                      api_key: Optional[str] = None) -> str:
    """Submete o batch e retorna o batch_id. Não bloqueia."""
    client = _get_client(api_key)
    requests = create_batch_requests(companies, model=model)
    response = client.beta.messages.batches.create(requests=requests)
    print(f"✅ Batch job criado: {response.id} (status: {response.processing_status})")
    return response.id


def poll_batch_status(batch_id: str, check_interval: int = 30,
                       api_key: Optional[str] = None) -> dict:
    """Bloqueia até o batch terminar, imprimindo progresso."""
    client = _get_client(api_key)
    while True:
        batch = client.beta.messages.batches.retrieve(batch_id)
        done = batch.request_counts.succeeded + batch.request_counts.errored
        total = (batch.request_counts.processing + batch.request_counts.succeeded
                 + batch.request_counts.errored + batch.request_counts.canceled
                 + batch.request_counts.expired)
        print(f"Status: {batch.processing_status} | concluídas: {done}/{total}")
        if batch.processing_status == "ended":
            return {"id": batch.id, "counts": batch.request_counts}
        time.sleep(check_interval)


def process_batch_results(batch_id: str, companies: list[dict],
                           api_key: Optional[str] = None) -> list[dict]:
    """Lê os resultados de um batch já concluído e junta com os dados originais."""
    client = _get_client(api_key)
    by_index = {i: dict(c) for i, c in enumerate(companies)}

    for result in client.beta.messages.batches.results(batch_id):
        idx = int(result.custom_id.split("_")[1])
        company = by_index.get(idx)
        if company is None:
            continue
        if result.result.type == "succeeded":
            try:
                text = result.result.message.content[0].text
                parsed = json.loads(text)
                company["website_status"] = parsed.get("status")
                company["website_updated"] = parsed.get("website")
            except Exception as e:
                company["website_status"] = "parse_error"
                company["website_updated"] = None
        else:
            company["website_status"] = "api_error"
            company["website_updated"] = None

    return [by_index[i] for i in range(len(companies))]


def find_websites_batch(companies: list[dict], model: str = DEFAULT_MODEL,
                         api_key: Optional[str] = None, check_interval: int = 30) -> list[dict]:
    """Função "tudo em um" para notebook: submete, espera e retorna os resultados.

    Bloqueia a célula até terminar (pode levar de minutos a ~1h dependendo do volume).
    Ideal para 500-5000+ empresas — usa a Batch API (50% de desconto).

    Uso em notebook:
        companies = load_companies_from_csv("empresas.csv")
        results = find_websites_batch(companies)
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv("websites_updated.csv", index=False)
    """
    batch_id = submit_batch_job(companies, model=model, api_key=api_key)
    poll_batch_status(batch_id, check_interval=check_interval, api_key=api_key)
    return process_batch_results(batch_id, companies, api_key=api_key)


# ============================================================================
# EXPORT
# ============================================================================

def save_results_to_csv(results: list[dict], output_filepath: str = "websites_updated.csv"):
    fieldnames = ["name", "ticker_symbol", "country", "industry",
                  "website", "website_updated", "website_status"]
    with open(output_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for company in results:
            writer.writerow(company)
    print(f"\n✅ Resultados salvos em: {output_filepath}")


def print_summary(results: list[dict]):
    total = len(results)
    counts = {}
    for r in results:
        s = r.get("website_status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS RESULTADOS")
    print("=" * 60)
    print(f"Total de empresas: {total}")
    for status, n in counts.items():
        print(f"  {status}: {n}")
    print("=" * 60)


# ============================================================================
# CLI
# ============================================================================

def main():
    import sys
    if len(sys.argv) < 2:
        print("Uso: python company_website_finder.py <arquivo.csv> [batch|regular]")
        sys.exit(1)

    input_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "batch"

    companies = load_companies_from_csv(input_file)
    print(f"✅ {len(companies)} empresas carregadas")

    if mode == "batch":
        results = find_websites_batch(companies)
    else:
        results = find_websites_sync(companies)

    save_results_to_csv(results)
    print_summary(results)


if __name__ == "__main__":
    main()
