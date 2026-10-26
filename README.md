# Pipeline de dados: infraestrutura de DNS das maiores empresas do mundo

Este pipeline responde: **em qual infraestrutura de rede (provedor e país) está hospedado o DNS autoritativo das maiores empresas do mundo por receita?**

Cada empresa é ligada à sua infraestrutura por esta cadeia:

```
empresa (ticker) → website → domínio apex → servidores NS → IPs dos NS → ASN → organização (e país)
```

## Visão geral

| Notebook | Entrada | Saída principal | O que faz |
|---|---|---|---|
| `01_scrapping_and_yfinance` | CompaniesMarketCap (CSV) + Yahoo Finance | `interim/01_data_after_yfinance.csv` | Baixa o ranking de empresas por receita, limpa e enriquece com site, setor, país e cidade |
| `02_ns_resolver` | saída do 01 | `interim/ns_resolver/*.parquet` | Extrai o domínio de cada site e resolve NS e IPs (A/AAAA) dos servidores DNS |
| `03_asn_resolver` | `ns_ips.parquet` | `interim/asn_resolver/*.parquet` | Mapeia cada IP para seu ASN e para a organização dona (Team Cymru) |
| `04_unified_dataset` | saídas do 02 e do 03 | `final/final_data.parquet` | Junta tudo, filtra os registros completos e agrupa organizações por grupo econômico |

Os notebooks devem rodar em ordem (01 → 04). Os módulos auxiliares ficam em `notebooks/src/`.

## Estrutura de pastas

```
data/
├── raw/        # ranking baixado, um arquivo por data (top_companies_revenue_AAAAMMDD.csv)
├── interim/    # checkpoints e tabelas intermediárias
│   ├── ns_resolver/    # saída do notebook 02
│   └── asn_resolver/   # saída do notebook 03
├── analysis/   # relatórios da auditoria
└── final/      # datasets finais (full_dns_enriched, full_clean, final_data)
notebooks/
├── 01_… 04_*.ipynb
└── src/        # módulos Python reutilizados pelos notebooks
```

## Dependências

Instale com `pip install -r requirements.txt`. As bibliotecas principais são pandas, requests, beautifulsoup4, yfinance, curl_cffi, dnspython, tldextract, tqdm e pyarrow.

Os notebooks 02 e 03 usam consultas DNS reais e precisam de acesso à internet com a porta 53 liberada.

---

## Notebook 01: coleta e enriquecimento (`01_scrapping_and_yfinance.ipynb`)

**Objetivo:** montar a lista de empresas e obter, para cada uma, o site e os dados cadastrais.

**Etapas**
1. **Download.** Baixa o CSV do ranking "largest companies by revenue" do CompaniesMarketCap. O arquivo é salvo com a data no nome em `data/raw/`. Os notebooks seguintes usam o mais recente.
2. **Padronização.** Renomeia colunas para `rank`, `company_name`, `ticker_symbol`, `revenue_ttm`, `price_usd` e `company_country`. Remove HTML dos nomes.
3. **Limpeza de escopo.**
   - Remove empresas com receita nula ou negativa.
   - Remove duplicatas pelo par `company_name` + `revenue_ttm`, para tratar dupla listagem sem apagar homônimos distintos.
4. **Verificações de sanidade.**
   - Soma da receita contra o PIB mundial (Banco Mundial, 2025).
   - Soma do top 500 contra a Fortune 500.
   - Lista dos 20 maiores.
5. **Correção de tickers.** Um dicionário troca tickers desatualizados por atuais, por exemplo `TATAMOTORS.NS → TMPV.NS` e `LTIM.NS → LTM.NS`. Empresas deslistadas ficam comentadas e vão aparecer como não resolvidas.
6. **Consulta ao Yahoo Finance.**
   - As consultas rodam em lotes de 100 tickers, com 10 threads.
   - O notebook salva um checkpoint a cada lote e retoma do ponto onde parou.
   - Há um cache em disco, `yf_cache.csv`.
   - Se o Yahoo limitar as consultas, o código pausa todas as threads.
7. **Pós-processamento.** Se o status é `success` mas o site está vazio, o status passa para `error: ticker not resolved`.
8. **Análise de lacunas.** Para o top 500, 1000, 2000, 5000 e o total, calcula quantas empresas ficaram sem dados e quanto da receita elas representam.

**Resultado:** `data/interim/01_data_after_yfinance.csv`, com 10.664 empresas, das quais 10.321 foram resolvidas e 342 não foram.

**Colunas geradas pelo Yahoo:** `website`, `longBusinessSummary`, `sector`, `industry`, `country`, `city` e `yf_status`.

### Módulo `src/yf_pipeline.py`
- `get_yfinance_info(ticker)` consulta um ticker e nunca levanta exceção. Ele devolve sempre um dicionário com `yf_status`, que pode ser `success`, `not_found` ou `error: …`. Ele trata:
  - limite de requisições (pausa global e uma nova tentativa);
  - erro 401 (recria a sessão);
  - ticker inexistente.
- A sessão HTTP usa `curl_cffi` imitando um Chrome, para evitar bloqueios.
- `resolver_ticker(ticker, cache)` consulta o cache antes de ir ao Yahoo.
- `carregar_cache`, `atualizar_cache` e `salvar_cache` mantêm o cache. Só entram nele os sucessos com resumo preenchido.
- `garantir_colunas`, `listar_pendentes`, `aplicar_resultados` e `salvar_csv` fazem a retomada e o checkpoint da tabela.

---

## Notebook 02: resolução de NS (`02_ns_resolver.ipynb`)

**Objetivo:** descobrir, para cada domínio, quais servidores DNS autoritativos o atendem e quais são os IPs deles.

**Etapas**
1. **Extração do apex.**
   - Converte `website` em domínio registrável com `to_apex`, por exemplo `https://www.amazon.com → amazon.com`.
   - 343 empresas ficam sem domínio válido.
   - Os 10.261 domínios únicos são os que seguem.
2. **Retomada.** Lê o arquivo bruto `02_dns_raw.jsonl` e pula os domínios já resolvidos de forma conclusiva. Timeouts e erros são tentados de novo.
3. **Resolução em paralelo.** Roda 10 threads, e só a thread principal grava o arquivo, para evitar corrida de escrita. Cada domínio vira um registro JSON.
4. **Normalização em tabelas.**
   - `dns_status`: domínios sem NS e o motivo (`no_ns`, `timeout`, `nxdomain`).
   - `ns_hosts`: uma linha por domínio × NS.
   - `ns_ips`: uma linha por NS × IP, com `rtype` (A ou AAAA) e `status`.
5. **Contagens de apoio.** Número de domínios por NS e por `ns_apex` (`ns_apex_counts.csv`, `ns_counts.csv`), contagem de falhas e faltantes por faixa do ranking.

**Resultado:** 10.233 domínios resolvidos, 32.024 linhas domínio × NS e 26.456 linhas NS × IP. Em `data/interim/ns_resolver/` ficam `companies`, `dns_status`, `ns_hosts` e `ns_ips` (parquet), e os CSVs de contagem.

### Módulo `src/dns_utils.py` (parte de NS)
- **Resolver:** usa o 1.1.1.1 e o 8.8.8.8, ignorando o DNS do sistema, com limite de 5 segundos por consulta.
- `to_apex(url)` usa `tldextract` e devolve `None` para URL vazia ou inválida.
- `_query(domain, rtype)` consulta o DNS e devolve uma lista ou um status (`nxdomain`, `no_ns`, `no_nameservers`, `timeout`, `error: …`). O resultado é memoizado com `lru_cache`, então NS compartilhados são consultados uma vez só.
- `resolve_dns(domain)` consulta o NS do apex e depois o A e o AAAA de cada NS. Devolve `domain`, `apex`, `NS`, `NS_apex`, `NS_A` e `NS_AAAA`.
- `is_conclusive(rec)` marca `timeout`, `error` e `no_nameservers` como inconclusivos (tentar de novo). Respostas reais, como `nxdomain`, são conclusivas.

---

## Notebook 03: resolução de ASN (`03_asn_resolver.ipynb`)

**Objetivo:** para cada IP de servidor NS, descobrir qual ASN o origina e qual organização é dona dele.

**Etapas**
1. **IPs únicos.** São 18.889 IPs, porque muitos domínios compartilham os mesmos NS.
2. **Retomada e paralelismo.** Funciona igual ao notebook 02, com o arquivo bruto `03_asn_raw.jsonl`.
3. **Consulta ao Team Cymru.** Usa um serviço DNS com o IP invertido (IPv4 e IPv6).
4. **Tabelas geradas.**
   - `ip_asn`: uma linha por IP, com `asn`, `asn_all`, `prefix`, `cc`, `registry` e `status`. Há 18.876 IPs com ASN e 13 sem rota (nxdomain).
   - `asn_info`: uma linha por ASN, com o nome bruto.
   - `asn_org_info`: o nome bruto separado em `handle`, `org` e `country_code`, por expressão regular. O padrão do nome é `HANDLE - Organização, CC`. Dos 1.430 ASNs, só 1 ficou sem organização.
5. **Sanidade.** Encadeia domínio → NS → IP → ASN e lista os 20 ASNs com mais domínios (Cloudflare, Amazon, GoDaddy, Microsoft e outros).

**Resultado:** `ip_asn.parquet`, `asn_info.parquet` e `asn_org_info.parquet` em `data/interim/asn_resolver/`.

### Módulo `src/dns_utils.py` (parte de ASN)
- `resolve_asn(ip)` valida o IP, monta o nome reverso e consulta o TXT em `origin.asn.cymru.com` (IPv4) ou `origin6.asn.cymru.com` (IPv6). Depois busca o nome do AS em `AS<n>.asn.cymru.com`. O resultado é memoizado.
- Se o prefixo for anunciado por vários ASNs (MOAS), `asn` guarda o primeiro e `asn_all` guarda todos.
- `status` vale `ok` ou o motivo da falha (`nxdomain`, `timeout`, `invalid_ip`).
- `is_conclusive_asn(rec)` aplica a mesma regra de retomada do notebook 02.

---

## Notebook 04: dataset unificado (`04_unified_dataset.ipynb`)

**Objetivo:** juntar todas as tabelas numa só base analítica e agrupar organizações por grupo econômico.

**Etapas**
1. **Leitura e padronização.** Renomeia colunas para evitar colisão de nomes (`status` aparece em várias tabelas) e remove duplicatas:
   - `dns_status`: por `apex`;
   - `ns_hosts`: por `(apex, ns)`;
   - `ip_asn`: por `ip`;
   - `asn_org`: por `asn`.
2. **Encadeamento por left join:** `companies → dns_status → ns_hosts → ns_ips → ip_asn → asn_org`. Os joins "muitos para um" usam `validate="many_to_one"`, que faz o pandas dar erro se houver chave duplicada.
3. **Status de DNS consolidado.** Marca `no_website` para empresas sem domínio e preenche o status faltante com `ok` ou `not_resolved`.
4. **Conferências.** Um `assert` garante que nenhuma empresa foi perdida, e o notebook conta IPs sem ASN e ASNs sem organização.
5. **Salva a base completa** (`full_dns_enriched`). Resultado: 10.664 empresas viram 83.787 linhas.
6. **Auditoria** (`src/pipeline_audit.py`). Gera um relatório com as empresas não resolvidas e a etapa em que cada uma falhou.
7. **Filtro de completos.** Mantém só as linhas com `ns`, `ip`, `asn` e `as_org` preenchidos e salva em `full_clean`. Restam 76.636 linhas e 10.283 empresas. As 8,5% de linhas removidas são guardadas em `full_unresolved` para auditoria, mas não são salvas.
8. **De-para de grupos econômicos** (`src/depara_as_org.py`). Gera `dp_as_org`, `dp_as_country_code` e a flag `as_org_remapped`, e salva em `final_data`. O de-para altera 28,3% das linhas e 2.824 empresas, e reduz as organizações únicas de 1.292 para 1.089.

**Resultado:** `data/final/final_data.parquet` e `.csv`, com 76.636 linhas e 31 colunas.

### Módulo `src/pipeline_audit.py`
- `classify_companies(full)` classifica cada empresa pela primeira etapa em que a resolução IPv4 falhou:
  `1_yfinance → 2_sem_website → 2_apex_nao_extraido → 3_ns_lookup → 4_ns_sem_ip_ipv4 → 5_ip_sem_asn → 6_asn_sem_org → OK`.
  Devolve um DataFrame com uma linha por empresa, com a etapa, o detalhe, o número de NS e se há organização via IPv6.
- `run_audit(out_path)` relê todas as tabelas intermediárias e gera um relatório de texto (funil por tabela e limitações), salvo em `data/analysis/pipeline_limitations_report.txt`.

### Módulo `src/depara_as_org.py`
- O dicionário `DEPARA_AS_ORG` mapeia `{nome do AS: (grupo controlador, país do controlador)}`. Por exemplo, Vercara e Tiggee viram DigiCert/US, e as várias empresas Alibaba viram Alibaba/CN.
- Um grupo só entra se tiver ganho de pelo menos 50 empresas ou receita somada de pelo menos 110% da do maior AS dele.
- Cada linha traz um comentário com a confiança da associação: `[Alta]` para mesma marca ou subsidiária e `[Média]` para controle societário a verificar em fonte primária.

---

## Dicionário do dataset final (`final_data`)

**Unidade de observação:** uma linha por (empresa, servidor NS, IP do NS).

| Grupo | Campos | Significado |
|---|---|---|
| Empresa | `rank`, `company_name`, `ticker_symbol`, `revenue_ttm`, `price_usd`, `company_country` | Dados do ranking. `rank` é a chave da empresa e `revenue_ttm` é a receita dos últimos 12 meses, em USD. |
| Cadastro | `website`, `sector`, `industry`, `country`, `city`, `yf_status` | Dados do Yahoo Finance. `country` é o país da sede. |
| DNS | `apex`, `dns_status`, `ns`, `ns_apex`, `ip_lookup_status`, `ip`, `ip_type` | Domínio, servidor DNS autoritativo, provedor pelo nome do NS e IP (A ou AAAA). |
| Rede | `asn`, `asn_all`, `prefix`, `prefix_cc`, `prefix_registry`, `asn_status` | ASN de origem, prefixo anunciado, país e registro regional do prefixo. |
| Organização | `as_handle`, `as_org`, `as_country_code` | Dono do ASN conforme registrado e país de registro. |
| Grupo econômico | `dp_as_org`, `dp_as_country_code`, `as_org_remapped` | Grupo controlador e país do controlador, depois do de-para, e a flag de alteração. |

## Como usar o dataset na análise

- **Conte empresas por `rank`, não por linha.** Empresas com mais NS ou IPs aparecem em mais linhas.
- **Separe IPv4 e IPv6** com `ip_type`, porque os dois pertencem ao mesmo NS. A auditoria usa só IPv4.
- **Use `dp_as_org`** para concentração por grupo econômico e `as_org` como análise de sensibilidade, sem o de-para.
- **Há quatro conceitos de país.**
  - `country`: sede da empresa.
  - `as_country_code`: país de registro do AS.
  - `dp_as_country_code`: país do controlador.
  - `prefix_cc`: país do prefixo.
- **Pondere por `revenue_ttm`** para comparar a participação por número de empresas com a participação por receita.

## Limitações conhecidas

- **Viés de seleção.** As empresas sem cadeia completa (381 de 10.664) são excluídas do `final_data`, e as causas aparecem no relatório de auditoria.
- **Cobertura IPv6.** Só 79,5% das empresas têm IPv6.
- **Tickers.** Empresas deslistadas ou com ticker alterado dependem do dicionário de correção do notebook 01.
- **MOAS.** Em 1.563 linhas o prefixo tem mais de um ASN de origem, e só o primeiro vai em `asn`.
- **De-para.** As associações marcadas como `[Média]` dependem de conhecimento externo sobre aquisições.
- **Receita.** Há empresas com `revenue_ttm` suspeito, abaixo de US$ 1 milhão (157 empresas).
- **Domínios compartilhados.** 47 domínios aparecem em mais de uma empresa.
- **DNS autoritativo.** O pipeline mede o DNS do domínio raiz, não necessariamente a hospedagem do site nem a de outros serviços da empresa.
