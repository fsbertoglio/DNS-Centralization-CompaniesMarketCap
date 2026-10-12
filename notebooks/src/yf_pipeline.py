"""
yf_pipeline.py
==============

Blocos disponíveis:
  Por ticker (rodam dentro das threads):
    get_yfinance_info(ticker)         -> consulta o Yahoo (com pausa global e sessão)
    resolver_ticker(ticker, cache)    -> CACHE primeiro; se não houver, Yahoo

  Cache (dict em memória: {ticker: {coluna: valor}}):
    carregar_cache(caminho)           -> lê o CSV e devolve o dict
    eh_cacheavel(resultado)           -> este resultado merece entrar no cache?
    atualizar_cache(cache, resultados)-> adiciona os sucessos novos do Yahoo
    salvar_cache(cache, caminho)      -> grava o dict em CSV

  Tabela (DataFrame):
    garantir_colunas(df)              -> cria as colunas yf_* que faltarem
    listar_pendentes(df, ...)         -> lista de tickers que ainda faltam
    aplicar_resultados(df, resultados)-> grava resultados no df, por ticker
    salvar_csv(tabela, caminho)       -> to_csv criando a pasta, se preciso
"""

import os
import random
import threading
import time

import pandas as pd
import yfinance as yf
from curl_cffi import requests as cffi_requests


# =============================================================================
# COLUNAS
# =============================================================================

COLUNAS_YF = [
    "ticker_symbol", "website", "longBusinessSummary",
    "sector", "industry", "country", "city", "yf_status",
]
# Tudo, menos a chave. São as colunas copiadas para o df e para o cache.
COLUNAS_DADOS = [c for c in COLUNAS_YF if c != "ticker_symbol"]


# =============================================================================
# PAUSA GLOBAL (rate limit compartilhado entre threads)
# =============================================================================

# Dicionário mutável: todas as threads enxergam o MESMO objeto.
estado_pausa = {"bloqueado_ate": 0}
# Lock: só uma thread por vez executa o bloco "with lock_pausa".
lock_pausa = threading.Lock()


def aguardar_se_pausado():
    """Se alguma thread ativou a pausa, dorme só o tempo que falta."""
    agora = time.time()
    if estado_pausa["bloqueado_ate"] > agora:
        time.sleep(estado_pausa["bloqueado_ate"] - agora)


def ativar_pausa_global(segundos=60):
    """Define 'ninguém chama até o horário X'. max() garante que a pausa só estende."""
    with lock_pausa:
        novo_horario = time.time() + segundos
        estado_pausa["bloqueado_ate"] = max(estado_pausa["bloqueado_ate"], novo_horario)


# =============================================================================
# SESSÃO HTTP (curl_cffi imitando Chrome)
# =============================================================================

def criar_sessao():
    # impersonate="chrome": imita o handshake TLS de um Chrome real
    return cffi_requests.Session(impersonate="chrome")


sessao_global = criar_sessao()
lock_sessao = threading.Lock()


def recriar_sessao_global(sessao_antiga):
    """
    Recebe a sessão que FALHOU. Dentro do lock, só recria se a global ainda for
    aquela mesma sessão (is). Se outra thread já recriou, reaproveita a nova.
    """
    global sessao_global  # global é necessário porque aqui REATRIBUÍMOS o nome
    with lock_sessao:
        if sessao_global is sessao_antiga:
            sessao_global = criar_sessao()


# =============================================================================
# POR TICKER: Yahoo
# =============================================================================

def _resultado_ok(ticker, info):
    return {
        "ticker_symbol": ticker,
        "website": info.get("website"),
        "longBusinessSummary": info.get("longBusinessSummary"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "city": info.get("city"),
        "yf_status": "success",
    }


def _resultado_vazio(ticker, status):
    # Todas as colunas None, só ticker e status preenchidos
    r = {col: None for col in COLUNAS_YF}
    r["ticker_symbol"] = ticker
    r["yf_status"] = status
    return r


def _buscar(ticker, sessao):
    return _resultado_ok(ticker, yf.Ticker(ticker, session=sessao).info)


def get_yfinance_info(ticker, pausa_segundos=60, jitter_max=3.0):
    """
    Consulta UM ticker no Yahoo. Nunca levanta exceção: sempre devolve um dict
    com yf_status. Ordem das decisões (ifs independentes; 'mensagem' é
    reatribuída nos retries):
      1) tentativa normal
      2) rate limit  -> pausa global + 1 retry
      3) not found   -> "not_found"
      4) 401         -> recria sessão + 1 retry
      5) outro erro  -> "error: ..."
    """
    aguardar_se_pausado()
    sessao = sessao_global
    try:
        return _buscar(ticker, sessao)
    except Exception as e:
        mensagem = str(e)

    if "Too Many Requests" in mensagem or "Rate limited" in mensagem:
        ativar_pausa_global(pausa_segundos)
        aguardar_se_pausado()
        time.sleep(random.uniform(0, jitter_max))  # threads não acordam todas juntas
        try:
            return _buscar(ticker, sessao_global)
        except Exception as e2:
            mensagem = str(e2)

    if "Not Found" in mensagem or "Quote not found" in mensagem:
        return _resultado_vazio(ticker, "not_found")

    if "Unauthorized" in mensagem or "401" in mensagem:
        print(f"Sessão inválida detectada (ticker {ticker}), recriando sessão...")
        recriar_sessao_global(sessao)
        aguardar_se_pausado()
        try:
            return _buscar(ticker, sessao_global)
        except Exception as e2:
            # "error" (não "not_found"): é temporário, será reprocessado na próxima execução
            return _resultado_vazio(ticker, f"error: {e2}")

    print(f"Error fetching data for {ticker}: {mensagem}")
    return _resultado_vazio(ticker, f"error: {mensagem}")


# =============================================================================
# POR TICKER: cache primeiro, Yahoo depois
# =============================================================================

def resolver_ticker(ticker, cache, pausa_segundos=60, jitter_max=3.0):
    """
    A função que o notebook chama para cada ticker.
      1) está no cache?  -> devolve os dados de lá (nenhuma chamada ao Yahoo)
      2) não está        -> get_yfinance_info(ticker)
    O dict devolvido ganha a chave "origem" ("cache" ou "yahoo").

    IMPORTANTE: aqui o cache é só LIDO. Quem escreve nele é atualizar_cache(),
    chamado pelo notebook depois do lote. Assim as threads não disputam o mesmo
    dict para escrita (menos risco, mais fácil de entender).
    """
    if ticker in cache:
        linha = cache[ticker]
        resultado = {"ticker_symbol": ticker}
        resultado.update({c: linha.get(c) for c in COLUNAS_DADOS})
        resultado["origem"] = "cache"
        return resultado

    resultado = get_yfinance_info(ticker, pausa_segundos, jitter_max)
    resultado["origem"] = "yahoo"
    return resultado


# =============================================================================
# CACHE (dict em memória <-> CSV)
# =============================================================================

def carregar_cache(caminho):
    """CSV -> dict {ticker: {coluna: valor}}. Se o arquivo não existe, devolve {}."""
    if not os.path.exists(caminho):
        return {}
    tab = pd.read_csv(caminho).dropna(subset=["ticker_symbol"])
    tab = tab.drop_duplicates("ticker_symbol", keep="last").set_index("ticker_symbol")
    tab = tab.astype(object).where(tab.notna(), None)   # NaN -> None
    return tab.to_dict("index")                         # {ticker: {coluna: valor}}


def eh_cacheavel(resultado):
    """Critério do cache: success + resumo realmente preenchido."""
    resumo = resultado.get("longBusinessSummary")
    return (
        resultado.get("yf_status") == "success"
        and isinstance(resumo, str)
        and resumo.strip() != ""
        and resultado.get("ticker_symbol") is not None
    )


def atualizar_cache(cache, resultados):
    """
    Adiciona ao dict os sucessos NOVOS vindos do Yahoo (cache hits já estão lá).
    Modifica o dict em memória e devolve quantos tickers entraram.
    """
    hoje = pd.Timestamp.now().normalize()
    n = 0
    for r in resultados:
        if r.get("origem") == "yahoo" and eh_cacheavel(r):
            linha = {c: r.get(c) for c in COLUNAS_DADOS}
            linha["yf_cached_at"] = hoje
            cache[r["ticker_symbol"]] = linha
            n += 1
    return n


def salvar_cache(cache, caminho):
    """dict -> CSV (uma linha por ticker, colunas na ordem padrão)."""
    if not cache:
        return
    tab = pd.DataFrame.from_dict(cache, orient="index")
    tab.index.name = "ticker_symbol"
    tab = tab.reset_index().reindex(columns=COLUNAS_YF + ["yf_cached_at"])
    salvar_csv(tab, caminho)


# =============================================================================
# TABELA (DataFrame)
# =============================================================================

def garantir_colunas(df):
    """Cria colunas yf ausentes e força dtype object (evita warnings ao gravar texto). In-place."""
    for col in COLUNAS_YF:
        if col not in df.columns:
            df[col] = None
    for col in COLUNAS_DADOS:
        df[col] = df[col].astype("object")


def listar_pendentes(df, reprocessar_not_found=True, ordem_reversa=True):
    """Lista de tickers (sem repetição) cujo yf_status ainda não é 'success'."""
    status = df["yf_status"]
    mascara = status != "success"            # NaN != "success" => True (nunca processado)
    if not reprocessar_not_found:
        mascara &= status != "not_found"

    tickers = df.loc[mascara, "ticker_symbol"].dropna().drop_duplicates()
    if ordem_reversa:
        tickers = tickers.iloc[::-1]         # aqui sim inverte a ordem de processamento
    return tickers.tolist()


def aplicar_resultados(df, resultados):
    """
    Grava resultados (lista de dicts OU DataFrame) no df, casando por ticker_symbol.
    Modifica o df in-place. Linhas sem yf_status são ignoradas (nunca apagam dados).
    Serve tanto para o checkpoint (CSV lido) quanto para os lotes (lista de dicts).
    """
    res = resultados if isinstance(resultados, pd.DataFrame) else pd.DataFrame(resultados)
    if res.empty:
        return
    res = (
        res.dropna(subset=["ticker_symbol", "yf_status"])
        .drop_duplicates("ticker_symbol", keep="last")   # chave única => map é seguro
        .set_index("ticker_symbol")
    )
    alvo = df["ticker_symbol"].isin(res.index)
    for col in COLUNAS_DADOS:
        if col in res.columns:
            # map: para cada ticker, busca o valor correspondente na coluna de res
            df.loc[alvo, col] = df.loc[alvo, "ticker_symbol"].map(res[col])


def salvar_csv(tabela, caminho):
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    tabela.to_csv(caminho, index=False)
    