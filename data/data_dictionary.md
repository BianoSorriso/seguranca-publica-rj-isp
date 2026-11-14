# Dicionário de dados

Base: **Estatísticas de segurança: série histórica mensal por município desde 2014** — Instituto de Segurança Pública do Estado do Rio de Janeiro (ISP-RJ), portal ISPDados (<https://www.ispdados.rj.gov.br/>).

- **Arquivo bruto:** `data/raw/BaseMunicipioMensal.csv` (separador `;`, codificação Latin-1).
- **Arquivos processados:** `data/processed/base_municipio_mensal.parquet` e `base_municipio_mensal.csv.gz` (UTF-8).
- **Granularidade:** uma linha por município e mês (92 municípios × 153 meses = 14.076 linhas, de jan/2014 a set/2026).
- **Chave primária:** (`fmun_cod`, `ano`, `mes`), sem duplicatas.
- **Unidade das contagens:** registros mensais conforme a metodologia do ISP (ocorrências ou vítimas, a depender do indicador). Os valores **não** estão normalizados por população.

> **Como ler esta tabela.** As descrições seguem a nomenclatura do ISP-RJ. Relações marcadas com ✔ foram **verificadas empiricamente** nos dados por `src/etl.py` (ver `data/processed/etl_log.json`). Siglas institucionais (APF, AAAPAI, CMP, CMBA) e o significado exato de `fase` devem ser conferidos no glossário oficial do ISPDados antes de serem citados em publicações.

## 1. Variáveis originais (62)

| Variável | Significado | Tipo (arquivo processado) | Formato / unidade | Observações e verificações |
|---|---|---|---|---|
| `fmun_cod` | Código do município (padrão IBGE de 7 dígitos). | int32 | 7 dígitos | Chave junto com `ano` e `mes`; 92 valores distintos. |
| `fmun` | Nome do município. | string | texto | Base lida em Latin-1; nomes com acentos preservados. |
| `ano` | Ano de referência. | int16 | AAAA (2014 a 2026) | 2026 é parcial (janeiro a setembro). |
| `mes` | Mês de referência. | int8 | 1 a 12 |  |
| `mes_ano` | Rótulo do período no formato do ISP. | string | AAAAmMM (ex.: `2014m01`) | Verificado: coerente com `ano` e `mes` em 100% das linhas. |
| `regiao` | Região de segurança do município. | category | Capital, Grande Niterói, Baixada Fluminense, Interior | Capital = 1 município; Grande Niterói = 3; Baixada = 13; Interior = 75. |
| `hom_doloso` | Homicídio doloso (com intenção de matar). | Int32 (anulável) | contagem mensal |  |
| `lesao_corp_morte` | Lesão corporal seguida de morte. | Int32 (anulável) | contagem mensal |  |
| `latrocinio` | Roubo seguido de morte (latrocínio). | Int32 (anulável) | contagem mensal |  |
| `cvli` | Crimes violentos letais intencionais. | Int32 (anulável) | contagem mensal | ✔ Verificado: `cvli` = `hom_doloso` + `lesao_corp_morte` + `latrocinio` em 100% das linhas. |
| `hom_por_interv_policial` | Mortes por intervenção de agente do Estado (policial). | Int32 (anulável) | contagem mensal |  |
| `feminicidio` | Feminicídio. | Int32 (anulável) | contagem mensal | Série disponível somente a partir de out/2024; antes disso o valor é **ausente (NA)**, não zero. |
| `letalidade_violenta` | Mortes violentas (CVLI e mortes por intervenção de agente do Estado). | Int32 (anulável) | contagem mensal | ✔ Até set/2024: `cvli` + `hom_por_interv_policial`. ✔ Desde out/2024: soma também `feminicidio` (100% das linhas). **A definição muda na série**; para comparar períodos use `letalidade_harmonizada`. |
| `tentat_hom` | Tentativa de homicídio. | Int32 (anulável) | contagem mensal |  |
| `tentativa_feminicidio` | Tentativa de feminicídio. | Int32 (anulável) | contagem mensal | Disponível somente a partir de out/2024 (NA antes). |
| `lesao_corp_dolosa` | Lesão corporal dolosa. | Int32 (anulável) | contagem mensal |  |
| `estupro` | Estupro. | Int32 (anulável) | contagem mensal |  |
| `hom_culposo` | Homicídio culposo (sem intenção de matar). | Int32 (anulável) | contagem mensal |  |
| `lesao_corp_culposa` | Lesão corporal culposa. | Int32 (anulável) | contagem mensal |  |
| `roubo_transeunte` | Roubo a transeunte (pessoa a pé em via pública). | Int32 (anulável) | contagem mensal | Faz parte de `roubo_rua`. |
| `roubo_celular` | Roubo de aparelho celular. | Int32 (anulável) | contagem mensal | Faz parte de `roubo_rua`. |
| `roubo_em_coletivo` | Roubo em transporte coletivo. | Int32 (anulável) | contagem mensal | Faz parte de `roubo_rua`. |
| `roubo_rua` | Roubos em via pública. | Int32 (anulável) | contagem mensal | ✔ Verificado: `roubo_rua` = `roubo_transeunte` + `roubo_celular` + `roubo_em_coletivo` em 100% das linhas. |
| `roubo_veiculo` | Roubo de veículo. | Int32 (anulável) | contagem mensal |  |
| `roubo_carga` | Roubo de carga. | Int32 (anulável) | contagem mensal |  |
| `roubo_comercio` | Roubo a estabelecimento comercial. | Int32 (anulável) | contagem mensal |  |
| `roubo_residencia` | Roubo a residência. | Int32 (anulável) | contagem mensal |  |
| `roubo_banco` | Roubo a banco. | Int32 (anulável) | contagem mensal |  |
| `roubo_cx_eletronico` | Roubo a caixa eletrônico. | Int32 (anulável) | contagem mensal |  |
| `roubo_conducao_saque` | Roubo com condução da vítima para saque. | Int32 (anulável) | contagem mensal |  |
| `roubo_apos_saque` | Roubo após saque. | Int32 (anulável) | contagem mensal |  |
| `roubo_bicicleta` | Roubo de bicicleta. | Int32 (anulável) | contagem mensal |  |
| `outros_roubos` | Outros roubos. | Int32 (anulável) | contagem mensal |  |
| `total_roubos` | Total de roubos. | Int32 (anulável) | contagem mensal | Difere da soma dos componentes (`roubo_rua` e demais, sem dupla contagem) em 708 linhas (5,0%). Em 707 delas (2014–2018 e 2021) a diferença é exatamente oposta à de `total_furtos`, o que sugere reclassificação entre roubo e furto nos totais. Ver `inconsist_total_roubos`. |
| `furto_veiculos` | Furto de veículos. | Int32 (anulável) | contagem mensal |  |
| `furto_transeunte` | Furto a transeunte. | Int32 (anulável) | contagem mensal |  |
| `furto_coletivo` | Furto em transporte coletivo. | Int32 (anulável) | contagem mensal |  |
| `furto_celular` | Furto de aparelho celular. | Int32 (anulável) | contagem mensal |  |
| `furto_bicicleta` | Furto de bicicleta. | Int32 (anulável) | contagem mensal |  |
| `outros_furtos` | Outros furtos. | Int32 (anulável) | contagem mensal |  |
| `total_furtos` | Total de furtos. | Int32 (anulável) | contagem mensal | Difere da soma dos seis componentes em 738 linhas (5,2%): 707 espelham `total_roubos` (2014–2018 e 2021) e 31 são isoladas (2025). Ver `inconsist_total_furtos`. |
| `sequestro` | Sequestro. | Int32 (anulável) | contagem mensal |  |
| `extorsao` | Extorsão. | Int32 (anulável) | contagem mensal |  |
| `sequestro_relampago` | Sequestro relâmpago. | Int32 (anulável) | contagem mensal |  |
| `estelionato` | Estelionato. | Int32 (anulável) | contagem mensal |  |
| `apreensao_drogas` | Apreensão de drogas (ocorrências). | Int32 (anulável) | contagem mensal |  |
| `posse_drogas` | Registros de posse de drogas. | Int32 (anulável) | contagem mensal |  |
| `trafico_drogas` | Registros de tráfico de drogas. | Int32 (anulável) | contagem mensal |  |
| `apreensao_drogas_sem_autor` | Apreensão de drogas sem autoria identificada. | Int32 (anulável) | contagem mensal |  |
| `recuperacao_veiculos` | Veículos recuperados. | Int32 (anulável) | contagem mensal |  |
| `apf` | Autos de prisão em flagrante (APF). | Int32 (anulável) | contagem mensal | Sigla institucional: conferir no glossário do ISP. |
| `aaapai` | Autos de apreensão de adolescente por prática de ato infracional (AAAPAI). | Int32 (anulável) | contagem mensal | Sigla institucional: conferir no glossário do ISP. |
| `cmp` | Cumprimentos de mandado de prisão (CMP). | Int32 (anulável) | contagem mensal | Sigla institucional: conferir no glossário do ISP. |
| `cmba` | Cumprimentos de mandado de busca e apreensão de adolescente (CMBA). | Int32 (anulável) | contagem mensal | Sigla institucional: conferir no glossário do ISP. |
| `ameaca` | Ameaça. | Int32 (anulável) | contagem mensal |  |
| `pessoas_desaparecidas` | Pessoas desaparecidas. | Int32 (anulável) | contagem mensal |  |
| `encontro_cadaver` | Encontro de cadáver. | Int32 (anulável) | contagem mensal |  |
| `encontro_ossada` | Encontro de ossada. | Int32 (anulável) | contagem mensal |  |
| `pol_militares_mortos_serv` | Policiais militares mortos em serviço. | Int32 (anulável) | contagem mensal |  |
| `pol_civis_mortos_serv` | Policiais civis mortos em serviço. | Int32 (anulável) | contagem mensal |  |
| `registro_ocorrencias` | Total de registros de ocorrência de todos os tipos. | Int32 (anulável) | contagem mensal | Medida geral de volume de registros policiais, não de criminalidade efetiva. |
| `fase` | Fase de consolidação do dado. | int8 | 2 ou 3 | Observado: 3 em 13.800 linhas; 2 nos três últimos meses (jul–set/2026), ainda em consolidação. Interpretação a conferir no glossário do ISP. |

## 2. Variáveis derivadas (criadas pelo ETL)

| Variável | Significado | Tipo (arquivo processado) | Formato / unidade | Observações e verificações |
|---|---|---|---|---|
| `data` | Primeiro dia do mês de referência (datetime), obtido de `mes_ano`. | datetime64 | AAAA-MM-DD (primeiro dia do mês) | Criada em `src/etl.py`. |
| `trimestre` | Trimestre do ano (1 a 4). | int8 | 1 a 4 | Criada em `src/etl.py`. |
| `dado_preliminar` | Verdadeiro quando `fase` = 2 (dados ainda em consolidação). | bool | verdadeiro/falso | Criada em `src/etl.py`. |
| `letalidade_harmonizada` | `cvli` + `hom_por_interv_policial`: definição comparável em toda a série (exclui feminicídio). | Int32 (anulável) | contagem mensal | Criada em `src/etl.py`. |
| `total_roubos_recalc` | Soma dos componentes de roubo (sem dupla contagem), para teste de sensibilidade. | Int32 (anulável) | contagem mensal | Criada em `src/etl.py`. |
| `total_furtos_recalc` | Soma dos componentes de furto, para teste de sensibilidade. | Int32 (anulável) | contagem mensal | Criada em `src/etl.py`. |
| `inconsist_total_roubos` | Verdadeiro quando `total_roubos` difere da soma dos componentes. | bool | verdadeiro/falso | Criada em `src/etl.py`. |
| `inconsist_total_furtos` | Verdadeiro quando `total_furtos` difere da soma dos componentes. | bool | verdadeiro/falso | Criada em `src/etl.py`. |

## 3. Tratamento aplicado

| Situação | Decisão | Rastreabilidade |
|---|---|---|
| Valores ausentes em `feminicidio` e `tentativa_feminicidio` (11.868 linhas) | Mantidos como NA: a série não existia antes de out/2024. Não foram imputados. | `etl_log.json` → `decisao_nulos` |
| Totais de roubos/furtos diferentes da soma dos componentes | Valores oficiais **mantidos**; criadas colunas `*_recalc` e flags `inconsist_*`. A análise usa os oficiais e testa a sensibilidade com os recalculados. | `etl_log.json` → `linhas_inconsist_*` |
| Mudança de definição de `letalidade_violenta` em out/2024 | Criada `letalidade_harmonizada` (= `cvli` + `hom_por_interv_policial`). | `etl_log.json` → `identidades_verificadas` |
| Dados preliminares (`fase` = 2) | Mantidos e sinalizados em `dado_preliminar`. | `etl_log.json` → `linhas_dado_preliminar` |
| Linhas removidas | **Nenhuma.** | `etl_log.json` → `linhas_removidas` |

## 4. Fonte, licença e citação

- **Fonte primária:** ISP-RJ — <https://www.ispdados.rj.gov.br/> (conferir os termos de uso do portal para o arquivo bruto).
- **Dados derivados e este dicionário:** CC BY 4.0 (ver `LICENSE-DADOS-E-TEXTO.md`).
- **Como citar:** INSTITUTO DE SEGURANÇA PÚBLICA DO ESTADO DO RIO DE JANEIRO. *Estatísticas de segurança: série histórica mensal por município desde 2014*. Rio de Janeiro: ISP-RJ. Disponível em: <https://www.ispdados.rj.gov.br/>.
