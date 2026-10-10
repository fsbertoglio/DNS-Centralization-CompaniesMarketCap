---
chave: tagat2024netloss
titulo: "Net Loss: An econometric method to measure the impact of Internet shutdowns"
autores: [Anirudh Tagat, Amreesh Phokeer, Hanna Kreitem]
ano: 2024
veiculo: ACM Journal on Computing and Sustainable Societies (versão "Just Accepted")
doi: 10.1145/3659466
tipo: artigo empírico (econometria, dados em painel)
data_leitura: 2026-09-26
status: lido
relevancia: alta
tags: [shutdowns, economia-digital, concentracao, HHI, AS-hegemony, soberania-digital, metodologia]
---

# Fichamento: Tagat, Phokeer & Kreitem (2024), *Net Loss*

## 1. Referência

**ABNT**

TAGAT, Anirudh; PHOKEER, Amreesh; KREITEM, Hanna. Net Loss: an econometric method to measure the impact of Internet shutdowns. *ACM Journal on Computing and Sustainable Societies*, 2024. DOI: 10.1145/3659466.

**BibTeX**

```bibtex
@article{tagat2024netloss,
  author  = {Tagat, Anirudh and Phokeer, Amreesh and Kreitem, Hanna},
  title   = {Net Loss: An econometric method to measure the impact of Internet shutdowns},
  journal = {ACM Journal on Computing and Sustainable Societies},
  year    = {2024},
  doi     = {10.1145/3659466},
  note    = {Just Accepted}
}
```

Os três autores são da Internet Society (ISOC). A mesma instituição mantém o Pulse e o Internet Resilience Index, que o artigo usa como fonte de dados.

---

## 2. Resumo em uma frase

Os autores estimam, com dados públicos de 92 países entre 2019 e 2022 e um modelo de variáveis instrumentais em dois estágios, que fatores explicam a ocorrência de shutdowns de internet e qual a associação desses eventos com PIB, desemprego e investimento estrangeiro. Chegam a efeitos negativos relevantes no PIB, mas explicitamente não causais.

## 3. Resumo estruturado

| Item | Conteúdo |
|---|---|
| **Problema** | As estimativas de custo de shutdowns vêm de métodos baseados em fórmula (Brookings/West 2016, CIPESA, NetBlocks COST). Esses métodos não controlam outros fatores, não modelam a capacidade do governo de desligar a rede, têm baixa transparência e provavelmente superestimam os custos. |
| **Perguntas** | **RQ1:** que fatores estão associados à ocorrência de shutdowns? **RQ2:** qual a associação dos shutdowns com PIB, IED (investimento estrangeiro direto) e desemprego? |
| **Dados** | ISOC Pulse (shutdowns), V-Dem/Digital Society Project (capacidade de shutdown), ACLED (conflitos), CLEA (eleições), Banco Mundial/WDI (indicadores econômicos), ISOC Internet Resilience Index (HHI de mercado e AS Hegemony). |
| **Método** | IV em dois estágios com efeitos fixos e erros-padrão clusterizados por país. O 1º estágio prevê o shutdown; o 2º associa o shutdown previsto aos desfechos econômicos. Há também um Tobit para a duração dos shutdowns e, como robustez, estudo de evento com efeitos fixos duplos (TWFE) e pareamento por escore de propensão (PSM). |
| **Resultados-chave** | Shutdown anterior é o preditor mais forte. Mais probabilidade de shutdown está associada a PIB per capita menor e desemprego maior (sobretudo masculino); o efeito sobre IED não é significativo. Um dia adicional de shutdown custa cerca de US$ 86,58 por pessoa, ou cerca de US$ 19,74 bi por ano no agregado. |
| **Heterogeneidade** | A associação com shutdowns passados e com conflitos aparece nos países de **rede centralizada** (AS Hegemony alto) e **mercado de acesso concentrado** (HHI alto). |
| **Conclusão** | A correlação entre shutdowns e resultados econômicos é forte. A estimativa dos autores para a Índia é cerca de 21 vezes menor que a da Brookings, o que sugere que as fórmulas superestimam os custos. |
| **Limitações declaradas** | Não é causal; a frequência dos dados é baixa; ficam de fora as interrupções não governamentais (clima, cortes de cabo). |

---

## 4. Estrutura do artigo

| Seção | Páginas | Conteúdo | Interesse para mim |
|---|---|---|---|
| 1. Introdução | 1–3 | Tipos de shutdown, crítica às fórmulas, RQs | ★★ motivação |
| 2.1 Histórico | 3–4 | Dados do #KeepItOn, tipologia de Feldstein (Tabela 1) | ★ contexto |
| 2.2 Medição de custos | 4–5 | Brookings, CIPESA, NetBlocks COST e suas falhas | ★★★ revisão de literatura / justificativa |
| 3. Dados | 5–8 | Fontes, dicionário (Tabela 2), comparação entre grupos (Tabela 3) | ★★★ fontes + modelo de tabela |
| 4.1 Questões metodológicas | 8–10 | Identificação, causalidade reversa, escolha dos instrumentos | ★★ limitações |
| 4.2–4.3 Equações | 10–11 | Eq. 1 (1º estágio), Tobit, Eq. 2 (2º estágio), COVID | ★★ desenho |
| 5.1 Incidência | 11–13 | Preditores; Figuras 3–5 (heterogeneidade) | ★★★ argumento de concentração |
| 5.2 Duração / impactos | 12–14 | Tobit, Tabela 4, custo por dia | ★ números |
| 5.3 Robustez | 14–15 | TWFE, PSM | ★★ métodos alternativos |
| 6–7. Conclusão / futuro | 16–18 | Limitações, ML, outages não governamentais | ★★★ lacuna |
| Apêndices | 19–22 | Fórmula NetLoss (Eq. 3), Tabelas 5–7 | ★★ exposição econômica |

---

## 5. Metodologia em detalhe

**Unidade de análise:** país × mês/ano, 2019–2022, 92 países.

**Equação 1 (1º estágio), probabilidade de shutdown**

```
Shutdown_it = α + ω·Shutdown_i,t−1 + τ·ShutdownCapacity_it
              + β1·Conflicts_it + β2·Election_it + β3·Country_it + ε_it
```

Os instrumentos são as eleições (argumento: não há "ciclo político de negócios") e a capacidade de shutdown medida pelo V-Dem/DSP (escala de 0 a 4, média dos especialistas).

**Duração:** Tobit censurado em zero, com as mesmas variáveis explicativas.

**Equação 2 (2º estágio), desfechos econômicos**

```
Y_it = γ + δ1·Shutdown_hat_it + δ2·Country_it + η_it
```

`Y` é o log do PIB per capita (PPP), o log do IED/PIB ou o desemprego (total, masculino e feminino). Os controles são inflação, razão de dependência, educação da força de trabalho e urbanização.

**Detalhes técnicos:**
- Efeitos fixos de país e de tempo.
- Erro-padrão clusterizado por país.
- Controle de COVID com o log de casos por milhão.

**Heterogeneidade:** median split por usuários móveis, servidores, AS Hegemony (Gini) e HHI de mercado.

**Robustez:**
- TWFE (estudo de evento): efeito de −0,011 (erro-padrão 0,0192), não significativo.
- PSM com 5 vizinhos mais próximos: ATT de −0,038 (erro-padrão 0,075); ATE de −0,924.

**Apêndice B, Eq. 3 (ilustração):**

```
NetLoss_i = GDP_i × PredDuration_i × InternetUse_i     (PredDuration = −0,003)
```

---

## 6. Resultados numéricos principais

| Resultado | Valor | Fonte |
|---|---|---|
| Shutdown anterior → shutdown atual | coef. 0,457*** (Tab. 7); o texto fala em +21,1 p.p. | p. 11, 22 |
| Distúrbios (riots) → shutdown | coef. 0,0171* (Tab. 7); o texto fala em +3,4% | p. 11, 22 |
| Shutdown → ln(PIB per capita) | −0,156*** (0,0583) | Tab. 4, p. 16 |
| Shutdown → desemprego total | +2,220** (0,955) | Tab. 4 |
| Shutdown → desemprego masculino | +2,054*** (0,716) | Tab. 4 |
| Shutdown → desemprego feminino | +1,438 (n.s.) | Tab. 4 |
| Shutdown → ln(IED/PIB) | −0,907 (n.s.) | Tab. 4 |
| +1 dia de shutdown → PIB | −0,003 p.p. (sig. a 10%), cerca de US$ 86,58 por pessoa | p. 13 |
| Custo agregado | cerca de US$ 19,74 bi/ano (2019–2021) | p. 14 |
| Índia, 1 dia | US$ 67,9 mi (autores) vs. US$ 1,43 bi (Brookings/COST), cerca de 21× | p. 14 |
| Duração (Tobit) | shutdown anterior +96,67***; capacidade +67,09**; mês eleitoral −628,3***; fatalidades +1,576** | Tab. 6, p. 21 |

---

## 7. Avaliação crítica

### Pontos fortes
- Usa exclusivamente dados públicos, com as equações explicitadas. É reprodutível, ao contrário do COST.
- Vai além do PIB e inclui emprego e IED.
- A análise de heterogeneidade por estrutura de rede (HHI e AS Hegemony) é original e é a parte mais aproveitável para o meu projeto.
- A crítica aos métodos baseados em fórmula é bem fundamentada.

### Pontos fracos e inconsistências (anotar, **não reproduzir os números sem ressalva**)
- **Causalidade:** os próprios autores dizem que não é causal. A restrição de exclusão dos instrumentos é frágil: eleições e capacidade estatal podem afetar a economia diretamente.
- **Instrumento fraco?** O Stock-Wright só é significativo a 10% no modelo do PIB. O F do 1º estágio aparece como 80,11 na Tab. 4 e como 11,7 na Tab. 7.
- **Interpretação do coeficiente:** o texto alterna entre "1%" e "1 ponto percentual". O resumo diz "15,6 p.p." de redução no PIB, mas o coeficiente está em log, então a leitura correta seria algo como −15,6%.
- **Coeficientes vs. texto:** a Tab. 7 traz 0,457 para shutdown anterior, mas o texto fala em 21,1 p.p. A Tab. 7 traz 0,0171 para riots, mas o texto fala em 3,4%.
- **Índia:** o texto diz US$ 67,9 mi por dia, mas a Tabela 5 traz US$ 8.025 mi por dia. Pode ser uma diferença de ponderação, mas não é explicada.
- **Período:** os dados são descritos como 2019–2022, enquanto a conclusão fala em 2019–2021.
- **Número de observações:** cerca de 312 mil observações para 92 países é incompatível com um painel país-mês (daria cerca de 4,4 mil). A unidade real parece ser o evento ou a combinação evento × país, e o artigo não esclarece.
- **Robustez fraca:** tanto o TWFE quanto o PSM dão efeitos não significativos. "Mesmo sinal" não é "resultado robusto".

**Veredito:** é uma boa fonte de **enquadramento, dados e desenho**. É uma fonte fraca de **números** para citar como fato.

---

## 8. Citações

### 8.1 Literais (originais em inglês)

> "every additional day of an Internet shutdown costs $86.58 per person on average" (p. 1)

Uso: exemplo de estimativa de custo econômico de interrupções. Citar com a ressalva de não causalidade.

> "such a model precludes careful investigation of channels, mechanisms, and heterogeneity in economic impact" (p. 2)

Uso: justificar uma abordagem empírica baseada em dados, e não em fórmula.

> "Using open datasets makes our methodology fully reproducible." (p. 5)

Uso: justificar o pipeline aberto e documentado.

> "they may be overestimating the economic impacts of Internet shutdowns" (p. 5, sobre Brookings e CIPESA)

Uso: revisão dos métodos de custo.

> "scores closer to 0 imply low market concentration" (p. 6, sobre o HHI)

Uso: definição do HHI na metodologia.

> "the more control a government exerts over the Internet, the more likely […] an Internet shutdown" (p. 9, citando a Freedom House)

Uso: relação entre controle de infraestrutura e soberania.

> "this paper does not address Internet shutdowns that were not imposed by governments" (p. 10, nota 10)

Uso: **lacuna** que posiciona a pesquisa sobre DNS.

> "it may affect the ease with which shutdowns can be imposed" (p. 12, sobre redes com poucos provedores)

Uso: argumento central de que concentração implica vulnerabilidade e controle.

> "there are specific dimensions of the Internet that matter for how much at-risk countries face" (p. 12)

Uso: justificar a medição de estrutura, e não só de uso.

> "we are unable to provide causal estimates of the impact of Internet shutdowns" (p. 16)

Uso: citar ao usar os números do artigo.

> "richer countries are overweighted in this estimation" (p. 20)

Uso: ressalva se eu ponderar a exposição por receita.

### 8.2 Interpretadas (paráfrases)

- **p. 1–2:** Os custos de um shutdown vão além da comunicação e atingem transações financeiras, comércio, mercado de trabalho, investimento e remessas. Os efeitos se prolongam e aprofundam desigualdades.
- **p. 4–5:** As ferramentas existentes (NetBlocks COST, CIPESA) aplicam variações da fórmula de West (2016). Falta transparência sobre como são implementadas, e os dados do COST pararam em 2021.
- **p. 5:** As fórmulas falham por dois motivos: não controlam outros determinantes do produto econômico e ignoram tanto a capacidade técnica do governo quanto o histórico de shutdowns.
- **p. 8:** Países com shutdown têm menos provedores de serviço, menos usuários de internet e renda per capita muito menor (cerca de US$ 7,5 mil contra US$ 23,3 mil). Os grupos diferem sistematicamente, o que exige controles.
- **p. 8–9:** Há risco de causalidade reversa: países com certas características econômicas e de internet podem ser os que mais recorrem a shutdowns. Por isso os autores usam IV.
- **p. 12:** Nos países com alto AS Hegemony e alto HHI, a internet tende a ser controlada por poucos provedores. É justamente nesses países que o histórico de shutdowns e os conflitos se associam a novos shutdowns. Nos países com mercado competitivo e rede descentralizada, essa associação enfraquece.
- **p. 14:** A estimativa dos autores para um dia de shutdown na Índia é cerca de 21 vezes menor que a da Brookings, indício de que as fórmulas inflam os custos.
- **p. 17:** Dados de maior frequência (luzes noturnas, velocidade medida pela Ookla) poderiam melhorar a inferência, mas trazem seus próprios ruídos e a falta de covariáveis na mesma frequência.
- **p. 18:** Os autores propõem, como agenda futura, modelar o risco de interrupções não impostas por governos, como cortes de cabo e danos à infraestrutura.

---

## 9. Notas de leitura (conexão com o meu projeto)

### Paralelos conceituais
- **Unidade:** país → empresa. **Fenômeno:** shutdown → dependência de provedor de DNS. **Métrica de concentração:** HHI de ISPs → HHI de provedores de DNS (consolidados por organização-mãe).
- O achado de heterogeneidade do artigo (concentração associada a risco) é **evidência adjacente**, na camada de acesso, para a tese de que concentração na camada de DNS é um vetor de vulnerabilidade e perda de autonomia.
- **Lacuna explorável:** o artigo trata só do Estado como agente da interrupção. A dependência de poucos provedores privados, muitas vezes estrangeiros, é outra fonte de risco sistêmico (caso Dyn, 2016). Isso fica fora do escopo declarado deles.

### O que aplicar
1. **Tabela de comparação entre grupos**, no estilo da Tab. 3: empresas com DNS em hyperscaler vs. DNS próprio, com teste t de Welch.
2. **Modelo associativo**, análogo ao 1º estágio: logit de "usa hyperscaler/provedor estrangeiro" sobre porte, setor e covariáveis do país-sede, com **erro-padrão clusterizado por país**.
3. **Median split**, como nas Figs. 4 e 5: repetir o modelo em países com HHI de acesso e capacidade de shutdown acima e abaixo da mediana.
4. **Coefficient plots** em vez de tabelas longas de regressão.
5. **Estudo de evento financeiro:** retorno anormal das ações de empresas dependentes de um provedor durante incidentes (Dyn 2016, quedas de Cloudflare e AWS). Usa o `yfinance` que já está no pipeline. Exige DNS histórico (ex.: OpenINTEL).
6. **Dicionário de variáveis** no formato da Tab. 2, derivado do `COLUMN_STANDARDS.md`.
7. **Tabela de exposição**, no formato da Tab. 5: receita dependente de cada provedor, com a ressalva sobre ponderação.

### O que NÃO aplicar
- A estratégia de IV: não há instrumento plausível para a escolha de provedor de DNS.
- Os coeficientes do artigo como parâmetros (ex.: −0,003 por dia). Eles valem para outro fenômeno e têm as inconsistências anotadas acima.

### Covariáveis de país a incorporar (fontes públicas citadas)
- Capacidade de shutdown (V-Dem/DSP).
- HHI de acesso e AS Hegemony (ISOC IRI / IHR).
- Histórico de shutdowns (ISOC Pulse).

---

## 10. Onde usar na minha escrita

| Seção do PEP/artigo | O que usar |
|---|---|
| Introdução / motivação | Custos econômicos de interrupções (p. 1–2); controle e soberania (p. 9) |
| Revisão de literatura | Métodos de custo e suas limitações (p. 4–5, 14); tipologia de shutdowns (p. 1, 4) |
| Lacuna / contribuição | Interrupções não governamentais fora do escopo (p. 10, 18) |
| Referencial de métricas | HHI e AS Hegemony (p. 6) |
| Metodologia | Dados públicos e reprodutibilidade (p. 5); cluster por país; median split; tabela de comparação entre grupos |
| Limitações | Causalidade reversa (p. 8–9); frequência dos dados (p. 17); ponderação por riqueza (p. 20) |

---

## 11. Referências para buscar

### Citadas no artigo
| Prioridade | Nº | Referência | Por quê |
|---|---|---|---|
| ★★★ | [26] | Fontugne, Shah & Aben (2018). *The (thin) bridges of AS connectivity: measuring dependency using AS hegemony*. PAM 2018. | Métrica de dependência de rede, adaptável para DNS |
| ★★★ | [27] | ISOC (2021). *Internet Resilience Index: methodology document*. | Definição dos indicadores de concentração |
| ★★★ | [23] | Mechkova et al. (2022). *Digital Society Project (DSP) Dataset*. | Covariável de capacidade de shutdown |
| ★★ | [17] | Marchant & Stremlau (2020). *A spectrum of shutdowns*. Int. J. of Communication. | Tratar interrupção/dependência como gradiente |
| ★★ | [3] | Björksten (2022). *A taxonomy of Internet shutdowns*. Access Now. | Situar o DNS entre as camadas técnicas de interferência |
| ★★ | [5] | West (2016). *Internet shutdowns cost countries $2.4 billion last year*. Brookings. | Método de fórmula criticado |
| ★★ | [7] | Kathuria et al. (2018). *The anatomy of an internet blackout*. Telecommunications Policy. | Estudo de caso de custo (Índia) |
| ★★ | [31] | de Chaisemartin & D'Haultfœuille (2023). *Two-way fixed effects and DiD estimators with several treatments*. J. of Econometrics. | Base para estudo de evento/DiD |
| ★ | [32] | Rosenbaum & Rubin (1983). *The central role of the propensity score…*. Biometrika. | PSM |
| ★ | [1] | Dainotti et al. (2011). *Analysis of country-wide Internet outages caused by censorship*. IMC. | Medição técnica de outages |
| ★ | [2] | Raman et al. (2020). *Censored Planet*. CCS. | Observatório de censura |
| ★ | [21] [22] | NetBlocks COST; CIPESA (2022). | Métodos de custo criticados |
| ★ | [20] | Chiplunkar & Goldberg (2022). *The employment effects of mobile Internet*. NBER. | Internet e emprego |

### Fora do artigo, sugeridas para o tema DNS (verificar dados bibliográficos antes de citar)
- Kashaf, Sekar & Agarwal (2020). *Analyzing third party service dependencies in modern web services: have we learned from the Mirai-Dyn incident?* IMC 2020. Dependência de DNS de terceiros em sites populares.
- Bates, Bowers, Greenstein, Weinstock, Xu & Zittrain (2018). *Evidence of decreasing Internet entropy: the lack of redundancy in DNS resolution by major websites and services*. NBER Working Paper. Concentração de DNS e HHI, muito próximo do meu recorte.

---

## 12. Próximos passos
- [ ] Ler Fontugne et al. (2018) e o documento metodológico do IRI.
- [ ] Baixar o DSP/V-Dem e o IRI e avaliar a cobertura de países frente à minha amostra.
- [ ] Verificar a disponibilidade de DNS histórico (OpenINTEL) para o estudo de evento.
- [ ] Levar aos orientadores a proposta de estudo de evento financeiro como contribuição.
