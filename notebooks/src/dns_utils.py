"""
dns_utils.py — funções de resolução de NS por domínio.

Uso no notebook:
    from dns_utils import resolve_dns, to_apex, is_conclusive
"""
from functools import lru_cache

import dns.exception
import dns.resolver
import pandas as pd
import tldextract

# --- Resolver ---------------------------------------------------------------
# configure=False ignora o DNS do sistema; por isso os servidores são informados.
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ["1.1.1.1", "8.8.8.8"]
resolver.lifetime = 5  # tempo máximo total por consulta (segundos)


def to_apex(url):
    """Extrai o domínio registrável (ex.: https://www.amazon.com -> amazon.com).
    Devolve None se a URL for vazia/NaN/inválida."""
    if url is None or pd.isna(url):
        return None
    return tldextract.extract(str(url)).top_domain_under_public_suffix or None


@lru_cache(maxsize=None)  # memoiza (domain, rtype): NS compartilhados são consultados uma vez só
def _query(domain, rtype):
    """Retorna uma lista de strings, ou um status:
    'nxdomain', 'no_<tipo>', 'no_nameservers', 'timeout', 'error: ...'.
    ATENÇÃO: o retorno é cacheado e compartilhado; não modifique a lista."""
    try:
        resp = resolver.resolve(domain, rtype)
        if rtype == "NS":
            return [str(rr.target).rstrip(".").lower() for rr in resp]
        return [rr.to_text() for rr in resp]
    except dns.resolver.NXDOMAIN:
        return "nxdomain"             # domínio não existe
    except dns.resolver.NoAnswer:
        return f"no_{rtype.lower()}"  # existe, mas sem registro desse tipo
    except dns.resolver.NoNameservers:
        return "no_nameservers"       # todos os servidores responderam SERVFAIL
    except dns.exception.Timeout:
        return "timeout"              # inconclusivo
    except Exception as e:
        return f"error: {e}"


def resolve_dns(domain):
    """Resolve NS do apex de `domain` e A/AAAA de cada nameserver.

    Chaves retornadas (sempre as mesmas):
      domain, apex, NS, NS_apex, NS_A, NS_AAAA
    NS é uma lista de hosts ou uma string de status.
    """
    apex = tldextract.extract(domain).top_domain_under_public_suffix
    base = {"domain": domain, "apex": apex, "NS": None,
            "NS_apex": None, "NS_A": None, "NS_AAAA": None}

    if not apex:
        return {**base, "NS": "invalid"}

    ns = _query(apex, "NS")
    if not isinstance(ns, list):
        return {**base, "NS": ns}

    return {
        **base,
        "NS": ns,
        "NS_apex": [tldextract.extract(h).top_domain_under_public_suffix for h in ns],
        "NS_A": [_query(h, "A") for h in ns],
        "NS_AAAA": [_query(h, "AAAA") for h in ns],
    }


def is_conclusive(rec):
    """False para timeout/erro (vale tentar de novo); True para respostas reais
    (lista de NS, nxdomain, no_ns, invalid...)."""
    ns = rec.get("NS")
    return not (isinstance(ns, str) and ns.startswith(("timeout", "error", "no_nameservers")))


## ------- ASN via Team Cymru ----------------------------------------------------------

import ipaddress
import dns.reversename

CYMRU_V4 = "origin.asn.cymru.com"
CYMRU_V6 = "origin6.asn.cymru.com"


def _txt(name):
    """Consulta TXT via _query. Devolve (texto_sem_aspas, 'ok') ou (None, status)."""
    res = _query(name, "TXT")            # lista de strings OU status ('nxdomain', 'timeout'...)
    if isinstance(res, list):
        return res[0].strip('"'), "ok"   # to_text() do TXT vem entre aspas
    return None, res


@lru_cache(maxsize=None)                 # muitos IPs pertencem ao mesmo ASN: o nome é buscado 1x
def _as_name(asn):
    txt, _ = _txt(f"AS{asn}.asn.cymru.com")
    if not txt:
        return None
    parts = [p.strip() for p in txt.split("|", 4)]   # maxsplit=4: o nome pode conter "|"
    return parts[4] if len(parts) == 5 else None


@lru_cache(maxsize=None)                 # mesmo IP nunca é consultado duas vezes
def resolve_asn(ip):
    """Resolve o ASN de um IP (v4 ou v6) via Team Cymru.
    Chaves: ip, asn, asn_all, prefix, cc, registry, as_name, status.
    status = 'ok' ou o motivo da falha. Não modifique o dict retornado (é cacheado)."""
    base = {"ip": ip, "asn": None, "asn_all": None, "prefix": None,
            "cc": None, "registry": None, "as_name": None, "status": None}

    try:
        addr = ipaddress.ip_address(ip)  # valida e normaliza (IPv6 comprimido vira forma padrão)
    except ValueError:
        return {**base, "status": "invalid_ip"}

    suffix = ".in-addr.arpa." if addr.version == 4 else ".ip6.arpa."
    rev = dns.reversename.from_address(str(addr)).to_text().removesuffix(suffix)
    zone = CYMRU_V4 if addr.version == 4 else CYMRU_V6

    txt, status = _txt(f"{rev}.{zone}")
    if txt is None:                      # nxdomain = IP sem rota anunciada; timeout = inconclusivo
        return {**base, "status": status}

    parts = [p.strip() for p in txt.split("|")]
    if len(parts) < 4:
        return {**base, "status": f"error: formato inesperado: {txt}"}

    asn_all = parts[0]                   # pode ter vários ASNs separados por espaço (multi-origem)
    asn = asn_all.split()[0]             # guardamos o primeiro em 'asn' e o campo inteiro em 'asn_all'
    return {**base, "asn": int(asn), "asn_all": asn_all, "prefix": parts[1],
            "cc": parts[2] or None, "registry": parts[3] or None,
            "as_name": _as_name(asn), "status": "ok"}


def is_conclusive_asn(rec):
    """Mesma ideia do is_conclusive: nxdomain é resposta real; timeout/erro merecem nova tentativa."""
    s = rec.get("status") or ""
    return not s.startswith(("timeout", "error", "no_nameservers"))
