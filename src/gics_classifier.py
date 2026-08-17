"""
gics_resolver.py

Resolve classificação setorial aproximada (GICS-like) para uma lista de empresas
usando a base open-source JerBouma/FinanceDatabase (https://github.com/JerBouma/FinanceDatabase).

IMPORTANTE: Esta NÃO é a classificação GICS oficial (MSCI/S&P). É uma aproximação
de código aberto, construída por curadoria manual, sem uso de dados proprietários.
Documentar isso explicitamente no COLUMN_STANDARDS.md (ver sufixo `_gics_approx`
sugerido nos nomes de coluna abaixo).

Estratégia de match, em ordem de prioridade (a mais confiável primeiro):
    1. Domínio (website) — normalizado, sem protocolo/www/subpaths
    2. ISIN (se disponível na sua base)
    3. Nome da empresa — fuzzy match (fallback, menos confiável)

Cada resultado retorna também `match_method` e `match_score`, para que você
possa auditar a confiança de cada linha antes de aceitar ou descartar.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import pandas as pd

try:
    import financedatabase as fd
except ImportError as e:
    raise ImportError(
        "Instale a dependência: pip install financedatabase rapidfuzz --break-system-packages"
    ) from e

try:
    from rapidfuzz import fuzz, process
except ImportError as e:
    raise ImportError(
        "Instale a dependência: pip install rapidfuzz --break-system-packages"
    ) from e


GICS_APPROX_COLUMNS = {
    "sector": "company_sector_gics_approx",
    "industry_group": "company_industry_group_gics_approx",
    "industry": "company_industry_gics_approx",
}


def normalize_domain(url_or_domain: str) -> str | None:
    """Normaliza uma URL ou domínio para comparação: remove protocolo, www, path, porta."""
    if not isinstance(url_or_domain, str) or not url_or_domain.strip():
        return None
    s = url_or_domain.strip().lower()
    if not s.startswith(("http://", "https://")):
        s = "http://" + s
    try:
        netloc = urlparse(s).netloc
    except Exception:
        return None
    netloc = re.sub(r":\d+$", "", netloc)  # remove porta
    netloc = re.sub(r"^www\.", "", netloc)  # remove www.
    return netloc or None


@dataclass
class ResolverStats:
    total: int
    matched_domain: int
    matched_name: int
    unmatched: int

    def summary(self) -> str:
        pct_reliable = 100 * self.matched_domain / self.total if self.total else 0
        pct_low_conf = 100 * self.matched_name / self.total if self.total else 0
        pct_total = 100 * (self.matched_domain + self.matched_name) / self.total if self.total else 0
        pct_unmatched = 100 * self.unmatched / self.total if self.total else 0
        return (
            f"Total: {self.total}\n"
            f"  Match confiável (symbol/domain) : {self.matched_domain:5d} ({pct_reliable:5.1f}%)\n"
            f"  Match baixa confiança (fuzzy)    : {self.matched_name:5d} ({pct_low_conf:5.1f}%) -- precisa revisão\n"
            f"  Sem match                        : {self.unmatched:5d} ({pct_unmatched:5.1f}%)\n"
            f"  Cobertura total (com revisão)    : {pct_total:5.1f}%"
        )


def load_financedatabase_equities() -> pd.DataFrame:
    """Carrega a base de equities do FinanceDatabase (todas as bolsas/países)."""
    equities = fd.Equities()
    df = equities.select()
    df = df.reset_index()  # symbol vira coluna
    return df


def build_domain_index(fdb_df: pd.DataFrame) -> dict[str, dict]:
    """
    Constrói um índice domínio -> registro de referência.
    Quando várias linhas do FinanceDatabase compartilham o mesmo domínio
    (empresa listada em múltiplas bolsas), prioriza a linha com market_cap
    mais alto / com mais campos preenchidos.
    """
    fdb_df = fdb_df.copy()
    fdb_df["_domain"] = fdb_df["website"].apply(normalize_domain)
    fdb_df = fdb_df.dropna(subset=["_domain"])

    index: dict[str, dict] = {}
    for domain, group in fdb_df.groupby("_domain"):
        # Prioriza a linha com mais campos GICS preenchidos
        group = group.assign(
            _completeness=group[["sector", "industry_group", "industry"]].notna().sum(axis=1)
        ).sort_values("_completeness", ascending=False)
        index[domain] = group.iloc[0].to_dict()
    return index


def build_name_choices(fdb_df: pd.DataFrame) -> tuple[list[str], dict[str, dict]]:
    """Prepara estruturas para fuzzy match por nome (fallback)."""
    fdb_df = fdb_df.dropna(subset=["name"]).drop_duplicates(subset=["name"])
    name_to_record = {row["name"]: row.to_dict() for _, row in fdb_df.iterrows()}
    return list(name_to_record.keys()), name_to_record


def resolve_gics_approx(
    companies: pd.DataFrame,
    symbol_col: str | None = "Symbol",
    domain_col: str | None = "domain_final",
    name_col: str | None = "Name",
    country_col: str | None = "country",
    name_match_threshold: int = 90,
    enable_name_fuzzy: bool = True,
    fdb_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, ResolverStats]:
    """
    Enriquece um DataFrame de empresas com classificação setorial aproximada.

    Ordem de prioridade dos métodos (mais confiável primeiro):
        1. symbol  -> match exato de ticker (mesma convenção do Yahoo Finance:
                      ex. '2222.SR', '600028.SS'). Sem ambiguidade.
        2. domain  -> match exato de domínio normalizado. Sem ambiguidade.
        3. name_fuzzy -> fuzzy match por nome, restrito ao mesmo país quando
                      disponível. IMPORTANTE: nomes curtos/genéricos (bancos,
                      conglomerados) geram falsos positivos com score alto
                      mesmo com token_set_ratio. Por isso esses matches são
                      marcados como `name_fuzzy_low_confidence` e os valores
                      de GICS aproximado NÃO são preenchidos automaticamente
                      -- ficam disponíveis em colunas `_candidate` para
                      revisão manual ou validação adicional (ex. fallback
                      para Claude apenas nesses casos, não no dataset todo).

    Parâmetros
    ----------
    companies : DataFrame de entrada
    symbol_col : coluna com o ticker (formato Yahoo Finance). None para pular.
    domain_col : coluna com o domínio já resolvido (Stage 02). None para pular.
    name_col : coluna com o nome da empresa.
    country_col : coluna com o país (usada para restringir o fuzzy match).
    name_match_threshold : score mínimo (0-100) para considerar um candidato
                      no fallback de nome (mas ainda como low_confidence).
    enable_name_fuzzy : se False, pula a etapa 3 inteiramente (mais rápido,
                      mais conservador -- recomendado se você já vai rodar
                      Stage 02 de domínio antes de usar este fallback).
    fdb_df : opcionalmente, passe um FinanceDatabase já carregado.

    Retorna
    -------
    (DataFrame enriquecido, ResolverStats)
    """
    if fdb_df is None:
        fdb_df = load_financedatabase_equities()

    symbol_index = (
        fdb_df.dropna(subset=["symbol"]).drop_duplicates(subset=["symbol"]).set_index("symbol").to_dict("index")
        if symbol_col
        else {}
    )
    domain_index = build_domain_index(fdb_df) if domain_col else {}

    country_groups = {}
    if enable_name_fuzzy and name_col:
        fdb_dedup = fdb_df.dropna(subset=["name"]).drop_duplicates(subset=["name"])
        country_groups = {c: g["name"].tolist() for c, g in fdb_dedup.groupby("country")}
        name_all_choices, name_index = build_name_choices(fdb_df)

    out = companies.copy()
    for col in GICS_APPROX_COLUMNS.values():
        out[col] = None
        out[col + "_candidate"] = None  # preenchido só para matches de baixa confiança
    out["meta_gics_match_method"] = "unmatched"
    out["meta_gics_match_score"] = None
    out["meta_gics_source"] = "JerBouma/FinanceDatabase"

    matched_symbol = matched_domain = matched_name_low_conf = 0

    for idx, row in out.iterrows():
        record = None
        method = "unmatched"
        score = None
        low_confidence = False

        # 1. Match por symbol (ticker) — exato, sem ambiguidade
        if symbol_col and pd.notna(row.get(symbol_col)) and row[symbol_col] in symbol_index:
            record = symbol_index[row[symbol_col]]
            method = "symbol"
            score = 100
            matched_symbol += 1

        # 2. Match por domínio — exato, sem ambiguidade
        if record is None and domain_col and pd.notna(row.get(domain_col)):
            norm_domain = normalize_domain(row[domain_col])
            if norm_domain and norm_domain in domain_index:
                record = domain_index[norm_domain]
                method = "domain"
                score = 100
                matched_domain += 1

        # 3. Fallback fuzzy por nome, restrito ao país — marcado como baixa confiança
        if record is None and enable_name_fuzzy and name_col and pd.notna(row.get(name_col)):
            country = row.get(country_col) if country_col else None
            choices = country_groups.get(country, name_all_choices)
            best = process.extractOne(row[name_col], choices, scorer=fuzz.token_set_ratio)
            if best and best[1] >= name_match_threshold:
                record = name_index[best[0]]
                method = "name_fuzzy_low_confidence"
                score = best[1]
                low_confidence = True
                matched_name_low_conf += 1

        if record is not None:
            for key, col in GICS_APPROX_COLUMNS.items():
                target_col = col + "_candidate" if low_confidence else col
                out.at[idx, target_col] = record.get(key)
        out.at[idx, "meta_gics_match_method"] = method
        out.at[idx, "meta_gics_match_score"] = score

    total = len(out)
    unmatched = total - matched_symbol - matched_domain - matched_name_low_conf
    stats = ResolverStats(
        total=total,
        matched_domain=matched_symbol + matched_domain,  # confiáveis (symbol + domain)
        matched_name=matched_name_low_conf,  # baixa confiança, precisa revisão
        unmatched=unmatched,
    )
    return out, stats