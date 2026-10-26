"""
analysis_utils.py — funções compartilhadas pelos notebooks de análise
(05_concentracao, 06_dependencia_estrangeira, 07_redundancia).

Decisões metodológicas fixas (documentadas também nos notebooks):
  - Escopo: apenas IPv4 (ip_type == "A").
  - Unidade de análise: a empresa (rank). Cada empresa distribui peso 1 entre os seus
    provedores, proporcional ao número de NS de cada um (atribuição fracionada).
  - País de origem: `company_country` (CompaniesMarketCap), convertido para ISO-2.
  - País do provedor: país do grupo controlador (`dp_as_country_code`).
  - Blocos: US, EU (UE-27), BRICS e Others.

Uso:
    from src.analysis_utils import *
    v4 = load_ipv4()
    cp = company_provider(v4)
    comp = company_table(v4, cp)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import norm

FINAL = Path(__file__).resolve().parents[2] / "data" / "final" / "final_data.parquet"
FIG_DIR = Path(__file__).resolve().parents[2] / "outputs" / "figures"
TAB_DIR = Path(__file__).resolve().parents[2] / "data" / "analysis"

# ----------------------------------------------------------------------------
# PAÍSES E BLOCOS
# ----------------------------------------------------------------------------
# Nomes usados pelo CompaniesMarketCap -> ISO 3166-1 alfa-2
COUNTRY_ISO2 = {
    "Argentina": "AR", "Australia": "AU", "Austria": "AT", "Bahamas": "BS", "Bahrain": "BH",
    "Belgium": "BE", "Bermuda": "BM", "Brazil": "BR", "British Virgin Islands": "VG",
    "Bulgaria": "BG", "Canada": "CA", "Cayman Islands": "KY", "Chile": "CL", "China": "CN",
    "Colombia": "CO", "Costa Rica": "CR", "Cyprus": "CY", "Czech Republic": "CZ",
    "Denmark": "DK", "Egypt": "EG", "Estonia": "EE", "Finland": "FI", "France": "FR",
    "Germany": "DE", "Gibraltar": "GI", "Greece": "GR", "Guernsey": "GG", "Hong Kong": "HK",
    "Hungary": "HU", "Iceland": "IS", "India": "IN", "Indonesia": "ID", "Ireland": "IE",
    "Isle of Man": "IM", "Israel": "IL", "Italy": "IT", "Japan": "JP", "Jersey": "JE",
    "Jordan": "JO", "Kazakhstan": "KZ", "Kuwait": "KW", "Latvia": "LV",
    "Liechtenstein": "LI", "Lithuania": "LT", "Luxembourg": "LU", "Macau": "MO",
    "Malaysia": "MY", "Malta": "MT", "Mexico": "MX", "Monaco": "MC", "Netherlands": "NL",
    "New Zealand": "NZ", "Norway": "NO", "Panama": "PA", "Peru": "PE", "Philippines": "PH",
    "Poland": "PL", "Portugal": "PT", "Qatar": "QA", "Romania": "RO", "Saudi Arabia": "SA",
    "Singapore": "SG", "South Africa": "ZA", "South Korea": "KR", "Spain": "ES",
    "Sweden": "SE", "Switzerland": "CH", "Taiwan": "TW", "Thailand": "TH", "Turkey": "TR",
    "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US",
    "Uruguay": "UY", "Vietnam": "VN", "Russia": "RU", "Ethiopia": "ET", "Iran": "IR",
}

EU27 = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
        "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}
# BRICS: 5 membros originais; "plus" = membros plenos a partir de 2025 (sem a Arábia Saudita,
# cuja adesão formal é ambígua — avaliar como sensibilidade).
BRICS_CORE = {"BR", "RU", "IN", "CN", "ZA"}
BRICS_PLUS = BRICS_CORE | {"EG", "ET", "IR", "AE", "ID"}

BLOCS = ["US", "EU", "BRICS", "Others"]

# O código "EU" aparece como país de alguns registros WHOIS (RIPE, escopo regional).
# Onde o grupo é sabidamente de um país, corrigimos; o restante fica como "EU" (bloco UE,
# país não resolvido, tratado como estrangeiro na classificação por país).
PROVIDER_CC_FIX = {"Tele2 Sverige AB": "SE", "Vetenskapsradet / SUNET": "SE"}


def bloc_of(iso, brics=BRICS_PLUS):
    if iso == "US":
        return "US"
    if iso == "EU" or iso in EU27:
        return "EU"
    if iso in brics:
        return "BRICS"
    return "Others"


# ----------------------------------------------------------------------------
# CARGA E TABELAS-BASE
# ----------------------------------------------------------------------------
def load_ipv4(path=FINAL, brics=BRICS_PLUS):
    """Linhas IPv4 do dataset final, com país/bloco de origem (ISO-2)."""
    d = pd.read_parquet(path)
    v4 = d[d["ip_type"] == "A"].copy()
    v4["home"] = v4["company_country"].map(COUNTRY_ISO2)
    miss = v4.loc[v4["home"].isna(), "company_country"].unique()
    if len(miss):
        raise ValueError(f"países sem mapeamento ISO-2: {list(miss)}")
    v4["home_bloc"] = v4["home"].map(lambda c: bloc_of(c, brics))
    return v4


def _fix_cc(org, cc):
    return org.map(PROVIDER_CC_FIX).fillna(cc)


def company_provider(v4, provider="dp_as_org", country="dp_as_country_code",
                     brics=BRICS_PLUS):
    """Uma linha por (empresa, provedor) com peso fracionado.

    weight = nº de NS distintos do provedor / nº total de NS-provedor da empresa
    (soma 1 por empresa). `provider`/`country` permitem a sensibilidade sem de-para
    (provider="as_org", country="as_country_code").
    """
    t = v4.assign(provider=v4[provider], provider_cc=_fix_cc(v4[provider], v4[country]))
    cp = (t.groupby(["rank", "provider"], as_index=False)
            .agg(n_ns=("ns", "nunique"), provider_cc=("provider_cc", "first"),
                 home=("home", "first"), home_bloc=("home_bloc", "first"),
                 company_name=("company_name", "first"),
                 revenue_ttm=("revenue_ttm", "first"), sector=("sector", "first")))
    cp["weight"] = cp["n_ns"] / cp.groupby("rank")["n_ns"].transform("sum")
    cp["provider_bloc"] = cp["provider_cc"].map(lambda c: bloc_of(c, brics))
    return cp


def classify_dependence(cp, level="country"):
    """Por empresa: has_domestic, has_foreign e dependence_type.

    level="country": doméstico = provedor no mesmo país da sede.
    level="bloc":    doméstico = provedor no mesmo bloco (só para US/EU/BRICS).
    """
    if level == "country":
        same = cp["provider_cc"] == cp["home"]
    else:
        same = (cp["provider_bloc"] == cp["home_bloc"]) & (cp["home_bloc"] != "Others")
    g = cp.assign(same=same).groupby("rank")["same"]
    out = pd.DataFrame({"has_domestic": g.any(), "has_foreign": ~g.all()})
    out["dependence_type"] = np.select(
        [out.has_domestic & ~out.has_foreign, ~out.has_domestic & out.has_foreign],
        ["domestic-only", "foreign-only"], default="mixed")
    return out


def company_table(v4, cp):
    """Uma linha por empresa, com métricas de redundância e tipo de dependência."""
    base = (v4.groupby("rank")
              .agg(company_name=("company_name", "first"), revenue_ttm=("revenue_ttm", "first"),
                   sector=("sector", "first"), home=("home", "first"),
                   home_bloc=("home_bloc", "first"),
                   n_ns=("ns", "nunique"), n_ns_apex=("ns_apex", "nunique"),
                   n_asn=("asn", "nunique"), n_prefix=("prefix", "nunique")))
    base["n_providers"] = cp.groupby("rank")["provider"].nunique()
    base["n_provider_cc"] = cp.groupby("rank")["provider_cc"].nunique()
    base = base.join(classify_dependence(cp, "country"))
    base["dependence_bloc"] = classify_dependence(cp, "bloc")["dependence_type"]
    base.loc[base["home_bloc"] == "Others", "dependence_bloc"] = np.nan
    # posição por receita DENTRO da amostra analisada (1 = maior receita)
    base["rev_rank"] = base["revenue_ttm"].rank(ascending=False, method="first").astype(int)
    return base


def prepare(brics=BRICS_PLUS):
    """Atalho: (v4, company_provider, company_table) com a configuração padrão."""
    v4 = load_ipv4(brics=brics)
    cp = company_provider(v4, brics=brics)
    return v4, cp, company_table(v4, cp)


# ----------------------------------------------------------------------------
# CONCENTRAÇÃO
# ----------------------------------------------------------------------------
def share_matrix(cp):
    """Matriz esparsa empresas x provedores com os pesos fracionados."""
    r_idx, r_lab = pd.factorize(cp["rank"])
    p_idx, p_lab = pd.factorize(cp["provider"])
    W = sparse.csr_matrix((cp["weight"].to_numpy(), (r_idx, p_idx)),
                          shape=(len(r_lab), len(p_lab)))
    return W, pd.Index(r_lab, name="rank"), pd.Index(p_lab, name="provider")


def metrics_from_shares(s):
    """HHI (0-10.000), nº efetivo de provedores e CR_k, a partir de participações."""
    s = np.asarray(s, dtype=float)
    s = s[s > 0] / s.sum()
    top = np.sort(s)[::-1]
    hhi = 10_000 * float((s ** 2).sum())
    return {"HHI": hhi, "N_eff": 10_000 / hhi, "CR1": top[:1].sum(), "CR3": top[:3].sum(),
            "CR5": top[:5].sum(), "CR10": top[:10].sum(), "n_providers": len(s)}


def group_metrics(W, rows, weight=None):
    """Métricas de concentração do subconjunto `rows` (índices de linha de W).
    `weight` = peso por empresa (ex.: receita); None = cada empresa pesa 1."""
    w = np.ones(W.shape[0]) if weight is None else np.asarray(weight, dtype=float)
    tot = np.asarray(W[rows].multiply(w[rows][:, None]).sum(axis=0)).ravel()
    return metrics_from_shares(tot)


def bootstrap_metrics(W, rows, weight=None, n_boot=1000, seed=0, keys=("HHI", "CR1", "CR3",
                                                                         "CR5", "CR10")):
    """IC 95% (percentil) por bootstrap de empresas para as métricas de concentração."""
    rng = np.random.default_rng(seed)
    w = np.ones(W.shape[0]) if weight is None else np.asarray(weight, dtype=float)
    D = sparse.diags(w[rows]) @ W[rows]          # empresas do grupo, já ponderadas
    n = D.shape[0]
    DT = D.T.tocsr()
    res = {k: [] for k in keys}
    for _ in range(n_boot):
        c = rng.multinomial(n, np.full(n, 1.0 / n))
        m = metrics_from_shares(DT @ c)
        for k in keys:
            res[k].append(m[k])
    return {k: (np.percentile(v, 2.5), np.percentile(v, 97.5)) for k, v in res.items()}


def permutation_hhi_diff(W, rows_a, rows_b, weight=None, n_perm=2000, seed=0):
    """Teste de permutação bicaudal para HHI(a) - HHI(b). Devolve (diferença, p-valor)."""
    rng = np.random.default_rng(seed)
    w = np.ones(W.shape[0]) if weight is None else np.asarray(weight, dtype=float)
    rows = np.concatenate([rows_a, rows_b])
    D = (sparse.diags(w[rows]) @ W[rows]).tocsr()
    na = len(rows_a)

    def hhi_of(idx):
        return metrics_from_shares(np.asarray(D[idx].sum(axis=0)).ravel())["HHI"]

    obs = hhi_of(np.arange(na)) - hhi_of(np.arange(na, len(rows)))
    cnt = 0
    for _ in range(n_perm):
        p = rng.permutation(len(rows))
        d = hhi_of(p[:na]) - hhi_of(p[na:])
        cnt += abs(d) >= abs(obs)
    return obs, (cnt + 1) / (n_perm + 1)


# ----------------------------------------------------------------------------
# ESTATÍSTICA DE APOIO
# ----------------------------------------------------------------------------
def wilson_ci(k, n, alpha=0.05):
    """IC de Wilson para uma proporção k/n."""
    if n == 0:
        return (np.nan, np.nan)
    z = norm.ppf(1 - alpha / 2)
    p = k / n
    den = 1 + z ** 2 / n
    centre = (p + z ** 2 / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return (centre - half, centre + half)


def prop_ci_table(df, group, cat, order=None):
    """Tabela longa (grupo x categoria) com contagem, % e IC de Wilson (em %)."""
    ct = pd.crosstab(df[group], df[cat])
    if order is not None:
        ct = ct.reindex(columns=order, fill_value=0)
    n = ct.sum(axis=1)
    rows = []
    for g in ct.index:
        for c in ct.columns:
            lo, hi = wilson_ci(ct.loc[g, c], n[g])
            rows.append({group: g, cat: c, "k": int(ct.loc[g, c]), "n": int(n[g]),
                         "pct": 100 * ct.loc[g, c] / n[g], "lo": 100 * lo, "hi": 100 * hi})
    return pd.DataFrame(rows)


def cramers_v(table):
    """V de Cramér para uma tabela de contingência (DataFrame de contagens)."""
    from scipy.stats import chi2_contingency
    chi2, p, dof, _ = chi2_contingency(table)
    n = table.to_numpy().sum()
    k = min(table.shape) - 1
    return chi2, p, dof, float(np.sqrt(chi2 / (n * k)))


# ----------------------------------------------------------------------------
# ESTILO DOS GRÁFICOS (paleta categórica validada: azul, laranja, água; neutro p/ "Others")
# ----------------------------------------------------------------------------
BLOC_COLOR = {"US": "#2a78d6", "EU": "#eb6834", "BRICS": "#1baf7a", "Others": "#8a8a85"}
DEP_COLOR = {"domestic-only": "#2a78d6", "mixed": "#1baf7a", "foreign-only": "#eb6834"}
DEP_ORDER = ["domestic-only", "mixed", "foreign-only"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SEQ_BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def set_style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
        "ytick.color": INK2, "text.color": INK, "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelsize": 10, "legend.frameon": False, "font.size": 10,
        "figure.dpi": 110,
    })


def seq_cmap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUES)


def save_fig(fig, name):
    """Salva em PNG e PDF (vetorial, para o paper) em outputs/figures/."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight")


def save_table(df, name):
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TAB_DIR / f"{name}.csv")


def _lum(hexcolor):
    r, g, b = [int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def stacked_hbar(ax, pct, colors, min_label=7):
    """Barras horizontais empilhadas a 100%. `pct`: linhas = grupos, colunas = categorias (em %).
    Segmentos separados por 2px de superfície; rótulo só nos segmentos largos."""
    from matplotlib.ticker import FuncFormatter
    left = np.zeros(len(pct))
    y = np.arange(len(pct))
    for c in pct.columns:
        w = pct[c].to_numpy()
        ax.barh(y, w, left=left, color=colors[c], edgecolor="white", linewidth=1.5,
                height=0.62, label=c)
        txt = "white" if _lum(colors[c]) < 0.45 else INK
        for yi in range(len(y)):
            if w[yi] >= min_label:
                ax.text(left[yi] + w[yi] / 2, yi, f"{w[yi]:.0f}%", ha="center", va="center",
                        color=txt, fontsize=8, fontweight="bold")
        left += w
    ax.set_yticks(y)
    ax.set_yticklabels(pct.index)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", visible=False)


def ci_dots(ax, labels, pct, lo, hi, colors, hollow=False, offset=0.0):
    """Gráfico de pontos com IC horizontal; `colors` por linha."""
    y = np.arange(len(labels)) + offset
    for yi, p, l, h, c in zip(y, pct, lo, hi, colors):
        ax.plot([l, h], [yi, yi], color=c, linewidth=2, solid_capstyle="round")
        ax.plot([p], [yi], "o", markersize=7, markerfacecolor="white" if hollow else c,
                markeredgecolor=c, markeredgewidth=2)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.grid(axis="y", visible=False)
