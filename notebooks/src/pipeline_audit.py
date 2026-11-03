"""Auditoria do pipeline: compara todas as tabelas intermediárias e gera um relatório
de texto com as empresas não resolvidas, a etapa em que falharam e o que falta.

Uso (a partir da raiz do repositório ou de notebooks/):
    python notebooks/src/pipeline_audit.py
ou, no notebook:
    from src.pipeline_audit import run_audit; run_audit()
"""
import ipaddress
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data" / "interim"
FINAL = ROOT / "data" / "final"     # saída do notebook 04 (mesma base das análises)
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" #/ "analysis"

STAGE_ORDER = [
    "1_yfinance",
    "2_sem_website",
    "2_apex_nao_extraido",
    "3_ns_lookup",
    "4_ns_sem_ip_ipv4",
    "5_ip_sem_asn",
    "6_asn_sem_org",
    "OK",
]
STAGE_DESC = {
    "1_yfinance": "yfinance não retornou dados da empresa (yf_status != success)",
    "2_sem_website": "yfinance respondeu, mas sem campo 'website' -> sem domínio para consultar",
    "2_apex_nao_extraido": "há website, mas não foi possível extrair o domínio apex",
    "3_ns_lookup": "consulta de NS do domínio falhou (nxdomain / no_ns / timeout / sem NS)",
    "4_ns_sem_ip_ipv4": "há NS, mas nenhum registro A (IPv4) foi obtido para eles",
    "5_ip_sem_asn": "há IPv4, mas nenhum foi mapeado a um ASN (IP privado ou prefixo não roteado)",
    "6_asn_sem_org": "há ASN, mas sem organização/handle na base de ASN->org",
    "OK": "resolvida em IPv4 (ao menos um NS com IP, ASN e organização)",
}


def _is_private(ip):
    try:
        a = ipaddress.ip_address(ip)
        return a.is_private or a.is_loopback or a.is_link_local or a.is_reserved
    except (ValueError, TypeError):
        return False


def _pct(n, d):
    return f"{n / d:.1%}" if d else "n/a"


def _table(df, indent="    "):
    return "\n".join(indent + l for l in df.to_string().splitlines())


def classify_companies(full):
    """Uma linha por empresa (rank) com a primeira etapa em que a resolução IPv4 falhou."""
    rows = []
    for rank, g in full.groupby("rank", sort=False):
        first = g.iloc[0]
        stage, detail = "OK", ""
        if first["yf_status"] != "success":
            stage, detail = "1_yfinance", str(first["yf_status"])
        elif pd.isna(first["apex"]):
            if pd.isna(first["website"]) or not str(first["website"]).strip():
                stage = "2_sem_website"
            else:
                stage, detail = "2_apex_nao_extraido", str(first["website"])
        elif first["dns_status"] not in ("ok",) or g["ns"].isna().all():
            stage, detail = "3_ns_lookup", str(first["dns_status"])
        else:
            a = g[g["ip_type"] == "A"]
            if a["ip"].notna().sum() == 0:
                st = a["ip_lookup_status"].dropna().unique().tolist()
                stage = "4_ns_sem_ip_ipv4"
                detail = ",".join(sorted(map(str, st))) if st else "NS nunca consultado"
            elif a["asn"].notna().sum() == 0:
                stage = "5_ip_sem_asn"
                ips = a["ip"].dropna().unique()
                detail = "somente IP privado" if all(_is_private(i) for i in ips) else "IP público sem ASN"
            elif a["as_org"].notna().sum() == 0:
                stage = "6_asn_sem_org"
                detail = ",".join(map(str, a["asn"].dropna().unique()[:5]))
        a = g[g["ip_type"] == "A"]
        a6 = g[g["ip_type"] == "AAAA"]
        rows.append({
            "rank": rank,
            "stage": stage,
            "detail": detail,
            "n_ns": g["ns"].nunique(),
            "n_ns_v4_resolved": a.loc[a["as_org"].notna(), "ns"].nunique(),
            "has_v6_org": bool(a6["as_org"].notna().any()),
        })
    return pd.DataFrame(rows).set_index("rank")


def run_audit(out_path=None):
    L = []  # linhas do relatório
    w = L.append

    # ------------------------------------------------------------------ carga
    raw_files = sorted(RAW.glob("top_companies_revenue_*.csv"))
    yf = pd.read_csv(INTERIM / "01_data_after_yfinance.csv")
    comp = pd.read_parquet(INTERIM / "ns_resolver" / "companies.parquet")
    dns_status = pd.read_parquet(INTERIM / "ns_resolver" / "dns_status.parquet")
    ns_hosts = pd.read_parquet(INTERIM / "ns_resolver" / "ns_hosts.parquet")
    ns_ips = pd.read_parquet(INTERIM / "ns_resolver" / "ns_ips.parquet")
    ip_asn = pd.read_parquet(INTERIM / "asn_resolver" / "ip_asn.parquet")
    asn_org = pd.read_parquet(INTERIM / "asn_resolver" / "asn_org_info.parquet")
    full = pd.read_parquet(FINAL / "full_dns_enriched.parquet")
    final = pd.read_parquet(FINAL / "final_data.parquet")   # base usada nas análises (05 a 08)

    w("=" * 78)
    w("AUDITORIA DO PIPELINE - LIMITAÇÕES E EMPRESAS NÃO RESOLVIDAS")
    w(f"Gerado em {datetime.now():%Y-%m-%d %H:%M}")
    w("=" * 78)

    # ------------------------------------------------------- 1. funil por tabela
    w("\n1. FUNIL: TAMANHO DE CADA TABELA INTERMEDIÁRIA")
    w("-" * 78)
    n_total = yf["rank"].nunique()
    if raw_files:
        try:
            raw = pd.read_csv(raw_files[-1])
            w(f"  raw ({raw_files[-1].name}): {len(raw)} linhas")
        except Exception as e:  # noqa: BLE001
            w(f"  raw: não foi possível ler ({e})")
    w(f"  01_data_after_yfinance.csv           : {len(yf):>7} linhas | {n_total} empresas")
    w(f"  ns_resolver/companies.parquet        : {len(comp):>7} linhas | {comp['rank'].nunique()} empresas "
      f"| {comp['apex'].notna().sum()} com apex | {comp['apex'].nunique()} apex únicos")
    w(f"  ns_resolver/dns_status.parquet       : {len(dns_status):>7} domínios com falha registrada")
    w(f"  ns_resolver/ns_hosts.parquet         : {len(ns_hosts):>7} pares (domínio, NS) | "
      f"{ns_hosts['domain'].nunique()} domínios | {ns_hosts['ns'].nunique()} NS únicos")
    w(f"  ns_resolver/ns_ips.parquet           : {len(ns_ips):>7} linhas | {ns_ips['ns'].nunique()} NS | "
      f"{ns_ips['ip'].nunique()} IPs únicos")
    w(f"  asn_resolver/ip_asn.parquet          : {len(ip_asn):>7} IPs | {ip_asn['asn'].nunique()} ASNs")
    w(f"  asn_resolver/asn_org_info.parquet    : {len(asn_org):>7} ASNs com org")
    w(f"  final/full_dns_enriched.parquet      : {len(full):>7} linhas | {full['rank'].nunique()} empresas")
    w(f"  final/final_data.parquet             : {len(final):>7} linhas | {final['rank'].nunique()} empresas")

    # ---------------------------------------------- 2. consistência entre tabelas
    w("\n2. CONSISTÊNCIA ENTRE TABELAS (itens órfãos = informação perdida entre etapas)")
    w("-" * 78)
    ranks_yf, ranks_comp, ranks_full = set(yf["rank"]), set(comp["rank"]), set(full["rank"])
    w(f"  empresas em 01 e ausentes em companies.parquet : {len(ranks_yf - ranks_comp)}")
    w(f"  empresas em companies e ausentes em full       : {len(ranks_comp - ranks_full)}")
    w(f"  empresas duplicadas em 01 (rank repetido)      : {yf['rank'].duplicated().sum()}")
    ns_in_hosts, ns_in_ips = set(ns_hosts["ns"]), set(ns_ips["ns"])
    w(f"  NS em ns_hosts sem registro em ns_ips          : {len(ns_in_hosts - ns_in_ips)}")
    ips_ns, ips_asn = set(ns_ips["ip"].dropna()), set(ip_asn["ip"])
    w(f"  IPs em ns_ips sem registro em ip_asn           : {len(ips_ns - ips_asn)}")
    asns_ip = set(ip_asn["asn"].dropna().astype(int))
    asns_org = set(asn_org["asn"].dropna().astype(int))
    w(f"  ASNs em ip_asn sem registro em asn_org_info    : {len(asns_ip - asns_org)}")
    if asn_org.get("org") is not None:
        w(f"  ASNs em asn_org_info com org vazia             : {asn_org['org'].isna().sum()}")
    priv = [ip for ip in ips_ns if _is_private(ip)]
    w(f"  IPs privados/reservados vazados no DNS público : {len(priv)}")

    # ----------------------------------------------- 3. falhas por etapa (tabela)
    w("\n3. STATUS DE CADA CONSULTA (nível de linha, antes de agrupar por empresa)")
    w("-" * 78)
    w("  dns_status (por apex, ns_resolver):")
    w(_table(dns_status["status"].value_counts().to_frame("domínios")))
    w("  ip_lookup_status (por NS e tipo de registro, ns_ips):")
    w(_table(ns_ips.groupby(["rtype", "status"]).size().to_frame("NS")))
    w("  asn_status (por IP, ip_asn):")
    w(_table(ip_asn["status"].value_counts().to_frame("IPs")))
    w("  yf_status (por empresa, 01):")
    w(_table(yf["yf_status"].value_counts(dropna=False).to_frame("empresas")))

    # ------------------------------------------ 4. classificação por empresa
    cls = classify_companies(full)
    meta = full.drop_duplicates("rank").set_index("rank")
    cls = cls.join(meta[["company_name", "ticker_symbol", "revenue_ttm", "sector",
                         "company_country", "website", "apex"]])
    n = len(cls)
    w("\n4. ONDE CADA EMPRESA PARAROU (resolução IPv4, primeira etapa que falhou)")
    w("-" * 78)
    counts = cls["stage"].value_counts().reindex(STAGE_ORDER).fillna(0).astype(int)
    for s in STAGE_ORDER:
        w(f"  {s:<22} {counts[s]:>6}  {_pct(counts[s], n):>6}  {STAGE_DESC[s]}")
    n_fail = n - counts["OK"]
    w(f"\n  Resolvidas em IPv4 : {counts['OK']} de {n} ({_pct(counts['OK'], n)})")
    w(f"  Não resolvidas     : {n_fail} ({_pct(n_fail, n)})")

    w("\n  Detalhe por etapa:")
    for s in STAGE_ORDER[:-1]:
        sub = cls[cls["stage"] == s]
        if sub.empty:
            continue
        w(f"\n  [{s}] {len(sub)} empresas - {STAGE_DESC[s]}")
        if sub["detail"].replace("", pd.NA).notna().any() and s not in ("2_apex_nao_extraido",):
            w(_table(sub["detail"].replace("", "(sem detalhe)").value_counts().head(10).to_frame("empresas"), "      "))

    # --------------------------------------------------- 5. impacto econômico
    w("\n5. IMPACTO NA AMOSTRA (receita e composição)")
    w("-" * 78)
    rev_tot = cls["revenue_ttm"].sum()
    rev_fail = cls.loc[cls["stage"] != "OK", "revenue_ttm"].sum()
    w(f"  Receita total da amostra           : {rev_tot:,.0f}")
    w(f"  Receita das não resolvidas         : {rev_fail:,.0f} ({_pct(rev_fail, rev_tot)})")
    by_sector = cls.groupby("sector", dropna=False).agg(
        empresas=("stage", "size"),
        nao_resolvidas=("stage", lambda s: (s != "OK").sum()))
    by_sector["%"] = (by_sector["nao_resolvidas"] / by_sector["empresas"] * 100).round(1)
    w("  Taxa de não resolução por setor:")
    w(_table(by_sector.sort_values("%", ascending=False)))
    by_cty = cls.groupby("company_country", dropna=False).agg(
        empresas=("stage", "size"),
        nao_resolvidas=("stage", lambda s: (s != "OK").sum()))
    by_cty["%"] = (by_cty["nao_resolvidas"] / by_cty["empresas"] * 100).round(1)
    w("  Países com mais empresas não resolvidas (top 15):")
    w(_table(by_cty.sort_values("nao_resolvidas", ascending=False).head(15)))
    w("  Maiores empresas (por receita) não resolvidas (top 20):")
    top = (cls[cls["stage"] != "OK"].sort_values("revenue_ttm", ascending=False).head(20)
           [["company_name", "ticker_symbol", "company_country", "stage", "detail"]])
    w(_table(top))

    # ------------------------------------------ 6. completude entre os resolvidos
    ok = cls[cls["stage"] == "OK"]
    w("\n6. COMPLETUDE ENTRE AS EMPRESAS RESOLVIDAS (resolução parcial)")
    w("-" * 78)
    partial = ok[ok["n_ns_v4_resolved"] < ok["n_ns"]]
    w(f"  Empresas com TODOS os NS resolvidos em IPv4        : {len(ok) - len(partial)}")
    w(f"  Empresas com NS parcialmente resolvidos (>=1 falha): {len(partial)} "
      f"({_pct(len(partial), len(ok))} das resolvidas)")
    if len(ok):
        frac = (ok["n_ns_v4_resolved"] / ok["n_ns"]).describe()
        w(f"  Fração de NS resolvidos por empresa: média={frac['mean']:.2f} "
          f"mín={frac['min']:.2f} mediana={frac['50%']:.2f}")
    w(f"  Empresas com NS único (sem redundância)            : {(ok['n_ns'] == 1).sum()}")
    v6 = ok["has_v6_org"].sum()
    w(f"  Resolvidas em IPv4 que também têm IPv6 com org     : {v6} ({_pct(v6, len(ok))})")
    w(f"  Resolvidas em IPv4 SEM IPv6 (sem AAAA: não é falha): {len(ok) - v6}")
    v6_only = cls[(cls["stage"] != "OK") & cls["has_v6_org"]]
    w(f"  Não resolvidas em IPv4 mas com IPv6 resolvido      : {len(v6_only)}")

    # ------------------------------------------- 7. perda no nível de linha
    w("\n7. LINHAS SEM as_org EM full_dns_enriched (nível NS x IP)")
    w("-" * 78)
    m = full["as_org"].isna()
    w(f"  {m.sum()} de {len(full)} linhas ({_pct(m.sum(), len(full))})")
    full_ip = full[m & full["ip"].notna()]
    n_priv = full_ip["ip"].map(_is_private).sum()
    w(f"  Dessas, {len(full_ip)} têm IP mas sem org: {n_priv} privados, "
      f"{len(full_ip) - n_priv} públicos (sem ASN ou ASN sem org)")
    w("  Causa das linhas sem org (ip_type x ip_lookup_status x asn_status):")
    w(_table(full[m].groupby(["ip_type", "ip_lookup_status", "asn_status"], dropna=False).size().to_frame("linhas")))

    # ------------------------------------------------------- 8. limitações
    w("\n8. LIMITAÇÕES METODOLÓGICAS (para registrar no texto)")
    w("-" * 78)
    lims = [
        f"Cobertura: {_pct(counts['OK'], n)} das {n} empresas têm resolução IPv4 completa; "
        f"{n_fail} ficam fora da análise de concentração.",
        f"Viés de seleção: as não resolvidas somam {_pct(rev_fail, rev_tot)} da receita da amostra; "
        "ver seção 5 para setores/países sobre-representados entre as perdas.",
        f"Dependência do yfinance para o website: {counts['1_yfinance'] + counts['2_sem_website']} empresas "
        "perdidas por falta de dado cadastral (não há fonte alternativa de domínio).",
        "Domínio apex único por empresa: subsidiárias, domínios regionais e serviços "
        "(CDN, e-mail, SaaS) não são capturados; a infraestrutura medida é apenas a do site corporativo principal.",
        "Mede-se o DNS autoritativo (NS) e a rede que hospeda os servidores de nomes, "
        "não o provedor do conteúdo/web; um NS pode ser operado por terceiro distinto do hosting.",
        f"IPs privados vazados no DNS público ({len(priv)} IPs) e prefixos não roteados "
        "não têm ASN e são tratados como não resolvidos.",
        "Falhas de timeout/SERVFAIL podem ser transitórias: um novo passe pode recuperar parte delas.",
        "Mapeamento IP->ASN e ASN->org é um retrato único no tempo; anycast, múltiplas origens "
        "(asn_all) e mudanças de prefixo não são modelados, e fica-se com o primeiro ASN.",
        "IPv6: empresas sem AAAA não são falha, mas fazem o IPv6 cobrir população diferente do IPv4; "
        "as análises por família de endereço não são diretamente comparáveis.",
        "Resolução parcial: parte das empresas resolvidas tem NS sem IP/org, "
        "o que pode subestimar a diversidade de provedores (seção 6).",
    ]
    for i, t in enumerate(lims, 1):
        w(f"  {i:>2}. {t}")

    # ------------------------------------------- 9. tabela do artigo (funil por empresa)
    w("\n9. TABELA DO ARTIGO: FUNIL POR EMPRESA (perdas sempre em nº de empresas)")
    w("-" * 78)
    perdas = counts.drop("OK")
    linhas_tab = [
        ("Companies with revenue > 0", full.loc[full["revenue_ttm"] > 0, "rank"].nunique(), None),
        ("Resolved websites", full.loc[full["apex"].notna(), "rank"].nunique(),
         perdas[["1_yfinance", "2_sem_website", "2_apex_nao_extraido"]].sum()),
        ("Domains with NS records", full.loc[full["ns"].notna(), "rank"].nunique(), perdas["3_ns_lookup"]),
        ("Distinct name servers", full["ns"].nunique(), None),
        ("Server addresses (v4+v6)", full["ip"].nunique(), perdas["4_ns_sem_ip_ipv4"]),
        ("Distinct ASes", full["asn"].nunique(), perdas[["5_ip_sem_asn", "6_asn_sem_org"]].sum()),
        ("Complete resolution chain", counts["OK"], n_fail),
    ]
    for nome, valor, perda in linhas_tab:
        w(f"  {nome:<28} {valor:>7,}   {'--' if perda is None else f'{perda:,}':>5}")
    w(f"\n  Domínios distintos com NS (sem contar empresas que compartilham domínio): "
      f"{full.loc[full['ns'].notna(), 'apex'].nunique():,}")
    w(f"  Conferência: {n} - {n_fail} perdas = {counts['OK']} resolvidas; "
      f"final_data tem {final['rank'].nunique()} empresas "
      f"({'BATE' if final['rank'].nunique() == counts['OK'] else 'NÃO BATE'})")

    text = "\n".join(L) + "\n"
    out_path = Path(out_path) if out_path else OUT / "pipeline_limitations_report.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    cls.reset_index().to_csv(out_path.with_name("company_resolution_stage.csv"), index=False)
    print(text)
    print(f"\nRelatório salvo em: {out_path}")
    return cls


if __name__ == "__main__":
    run_audit()
