# Estatísticas de segurança do estado do Rio de Janeiro (2014–2026)

![Python](https://img.shields.io/badge/Python-3.12-1f4e79)
![Licença do código](https://img.shields.io/badge/c%C3%B3digo-MIT-2a7f62)
![Licença dos dados e texto](https://img.shields.io/badge/dados%20e%20texto-CC%20BY%204.0-2a7f62)
![FAIR](https://img.shields.io/badge/princ%C3%ADpios-FAIR-d1782f)

**Artigo publicado (GitHub Pages):** <https://bianosorriso.github.io/seguranca-publica-rj-isp/>

| | |
|---|---|
| **Autoria** | [FABIANO BASTOS] |
| **Curso** | Bacharelado em Sistemas de Informação, UniLaSalle · 6º período |
| **Disciplina** | Linguagem de Programação (Análise e Visualização de Dados com Python) |
| **Semestre** | 2026.2 |
| **Natureza** | Projeto final individual de conclusão de disciplina |

## Resumo executivo

Este projeto analisa a série mensal de estatísticas de segurança dos **92 municípios do estado do Rio de Janeiro**
(janeiro de 2014 a setembro de 2026; 14.076 observações município-mês), divulgada pelo ISP-RJ. Um pipeline em Python,
determinístico e **não destrutivo**, valida e trata a base, e três perguntas de pesquisa guiam a análise:

- **RQ1.** Como evoluiu a letalidade violenta e qual a participação das mortes por intervenção de agente do Estado?
- **RQ2.** Roubos e furtos seguiram trajetórias diferentes e como reagiram à pandemia de 2020?
- **RQ3.** Quão concentrada geograficamente é a criminalidade e o perfil das ocorrências difere entre regiões?

**Principais resultados** (acumulado de janeiro a setembro de cada ano, para comparar 2026 em base homogênea):

- A letalidade violenta harmonizada caiu **41,4%** entre 2014 e 2026, mas a participação das mortes por intervenção de
  agente do Estado subiu de 10,0% para um pico de **30,8%** em 2019.
- Os roubos caíram **60,5%** do pico (2018) até 2023; os furtos voltaram a crescer e já são **66,0%** dos registros patrimoniais.
- Cinco municípios concentram **53,7%** dos homicídios dolosos e **81,5%** dos roubos; o perfil muda por região.

> **Cuidado de leitura:** os números são contagens absolutas, **sem normalização por população**. Descrevem o volume de
> registros policiais, e não o risco individual.

**Palavras-chave:** segurança pública; Rio de Janeiro; letalidade violenta; crimes patrimoniais; ciência aberta (FAIR).

## Fonte dos dados

- **Instituto de Segurança Pública do Estado do Rio de Janeiro (ISP-RJ)**, portal **ISPDados**: <https://www.ispdados.rj.gov.br/>
- Conjunto: *Estatísticas de segurança: série histórica mensal por município desde 2014* (`BaseMunicipioMensal.csv`).
- Acesso em: novembro de 2026.
- O significado de cada variável está em [`data/data_dictionary.md`](data/data_dictionary.md).

## Estrutura do repositório

```
seguranca-publica-rj-isp/
├── README.md
├── LICENSE                      # MIT (código)
├── LICENSE-DADOS-E-TEXTO.md     # CC BY 4.0 (dados derivados e texto)
├── requirements.txt             # versões fixadas (pip freeze)
├── .gitignore
├── data/
│   ├── raw/                     # BaseMunicipioMensal.csv (cópia original, nunca alterada)
│   ├── processed/               # .parquet, .csv.gz e etl_log.json (rastreabilidade)
│   └── data_dictionary.md       # dicionário de variáveis (FAIR)
├── notebooks/
│   └── analise_exploratoria.ipynb
├── src/
│   ├── etl.py                   # leitura, validação, tratamento e métricas
│   ├── analise.py               # métricas das RQs e figuras
│   ├── gerar_dicionario.py      # gera data_dictionary.md e confere cobertura
│   └── build_artigo.py          # gera docs/index.html
└── docs/                        # artigo publicado via GitHub Pages
    ├── index.html
    └── assets/                  # figuras e biblioteca Plotly local
```

## Como reproduzir

Requer Python 3.12 e Git.

```bash
git clone https://github.com/BianoSorriso/seguranca-publica-rj-isp.git
cd seguranca-publica-rj-isp

python -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.etl                  # lê data/raw e grava data/processed
python -m src.gerar_dicionario     # regenera data/data_dictionary.md
python -m src.build_artigo         # regenera figuras e docs/index.html
jupyter nbconvert --to notebook --execute --inplace notebooks/analise_exploratoria.ipynb
```

O pipeline é **determinístico**: executar `python -m src.etl` novamente (inclusive em um ambiente novo, criado a partir do
`requirements.txt`) produz arquivos `.parquet` e `.csv.gz` idênticos byte a byte. Cada execução registra em
`data/processed/etl_log.json` o SHA-256 do arquivo bruto, as validações, as decisões de tratamento e a data da execução.

## Decisões de tratamento (resumo)

| Situação encontrada | Decisão |
|---|---|
| Feminicídio só existe desde out/2024 | Mantido como ausente (NA), sem imputar zero |
| `letalidade_violenta` muda de definição em out/2024 | Criada `letalidade_harmonizada` (comparável em toda a série) |
| Totais de roubos e furtos divergem da soma das partes (2014–2018) | Dados originais mantidos, com colunas recalculadas e *flags*; testada a sensibilidade (impacto máximo de 2,3%) |
| Dados de jul a set/2026 são preliminares | Mantidos e sinalizados em `dado_preliminar` |
| Linhas removidas | **Nenhuma** |

## Conformidade FAIR

| Princípio | Atendimento |
|---|---|
| **Findable** | Este README com resumo, palavras-chave e link da fonte; identificação de autoria, disciplina, semestre e instituição |
| **Accessible** | Repositório público; ingestão sem credenciais; artigo no GitHub Pages com layout responsivo |
| **Interoperable** | Dicionário de dados completo; dados tratados em Parquet e CSV comprimido |
| **Reusable** | Licenças MIT e CC BY 4.0; dependências fixadas; ETL rastreável |

## Licenças

- **Código** (`src/`, `notebooks/`): [MIT](LICENSE).
- **Dados derivados, dicionário, texto e figuras:** [CC BY 4.0](LICENSE-DADOS-E-TEXTO.md).
- **Dados brutos:** autoria do ISP-RJ. Consulte os termos de uso do portal ISPDados antes de redistribuir.

## Como citar

[FABIANO BASTOS]. *Estatísticas de segurança do estado do Rio de Janeiro (2014–2026)*. Repositório GitHub, 2026.
Disponível em: <https://github.com/BianoSorriso/seguranca-publica-rj-isp>.
