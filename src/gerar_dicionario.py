"""Gera ``data/data_dictionary.md`` e falha se alguma coluna da base ficar sem descrição.

Uso: ``python -m src.gerar_dicionario``
"""
from __future__ import annotations

from pathlib import Path

from src import etl

SAIDA = etl.RAIZ / "data" / "data_dictionary.md"

# (descrição, tipo no arquivo processado, formato/unidade, observações)
CONT = "Int32 (anulável)"
UNID = "contagem mensal"
DEFINICOES: dict[str, tuple[str, str, str, str]] = {
    # identificação e tempo
    "fmun_cod": ("Código do município (padrão IBGE de 7 dígitos).", "int32", "7 dígitos", "Chave junto com `ano` e `mes`; 92 valores distintos."),
    "fmun": ("Nome do município.", "string", "texto", "Base lida em Latin-1; nomes com acentos preservados."),
    "ano": ("Ano de referência.", "int16", "AAAA (2014 a 2026)", "2026 é parcial (janeiro a setembro)."),
    "mes": ("Mês de referência.", "int8", "1 a 12", ""),
    "mes_ano": ("Rótulo do período no formato do ISP.", "string", "AAAAmMM (ex.: `2014m01`)", "Verificado: coerente com `ano` e `mes` em 100% das linhas."),
    "regiao": ("Região de segurança do município.", "category", "Capital, Grande Niterói, Baixada Fluminense, Interior", "Capital = 1 município; Grande Niterói = 3; Baixada = 13; Interior = 75."),
    "fase": ("Fase de consolidação do dado.", "int8", "2 ou 3", "Observado: 3 em 13.800 linhas; 2 nos três últimos meses (jul–set/2026), ainda em consolidação. Interpretação a conferir no glossário do ISP."),
    # letalidade
    "hom_doloso": ("Homicídio doloso (com intenção de matar).", CONT, UNID, ""),
    "lesao_corp_morte": ("Lesão corporal seguida de morte.", CONT, UNID, ""),
    "latrocinio": ("Roubo seguido de morte (latrocínio).", CONT, UNID, ""),
    "cvli": ("Crimes violentos letais intencionais.", CONT, UNID, "✔ Verificado: `cvli` = `hom_doloso` + `lesao_corp_morte` + `latrocinio` em 100% das linhas."),
    "hom_por_interv_policial": ("Mortes por intervenção de agente do Estado (policial).", CONT, UNID, ""),
    "feminicidio": ("Feminicídio.", CONT, UNID, "Série disponível somente a partir de out/2024; antes disso o valor é **ausente (NA)**, não zero."),
    "letalidade_violenta": ("Mortes violentas (CVLI e mortes por intervenção de agente do Estado).", CONT, UNID, "✔ Até set/2024: `cvli` + `hom_por_interv_policial`. ✔ Desde out/2024: soma também `feminicidio` (100% das linhas). **A definição muda na série**; para comparar períodos use `letalidade_harmonizada`."),
    "tentat_hom": ("Tentativa de homicídio.", CONT, UNID, ""),
    "tentativa_feminicidio": ("Tentativa de feminicídio.", CONT, UNID, "Disponível somente a partir de out/2024 (NA antes)."),
    "lesao_corp_dolosa": ("Lesão corporal dolosa.", CONT, UNID, ""),
    "estupro": ("Estupro.", CONT, UNID, ""),
    "hom_culposo": ("Homicídio culposo (sem intenção de matar).", CONT, UNID, ""),
    "lesao_corp_culposa": ("Lesão corporal culposa.", CONT, UNID, ""),
    # roubos
    "roubo_transeunte": ("Roubo a transeunte (pessoa a pé em via pública).", CONT, UNID, "Faz parte de `roubo_rua`."),
    "roubo_celular": ("Roubo de aparelho celular.", CONT, UNID, "Faz parte de `roubo_rua`."),
    "roubo_em_coletivo": ("Roubo em transporte coletivo.", CONT, UNID, "Faz parte de `roubo_rua`."),
    "roubo_rua": ("Roubos em via pública.", CONT, UNID, "✔ Verificado: `roubo_rua` = `roubo_transeunte` + `roubo_celular` + `roubo_em_coletivo` em 100% das linhas."),
    "roubo_veiculo": ("Roubo de veículo.", CONT, UNID, ""),
    "roubo_carga": ("Roubo de carga.", CONT, UNID, ""),
    "roubo_comercio": ("Roubo a estabelecimento comercial.", CONT, UNID, ""),
    "roubo_residencia": ("Roubo a residência.", CONT, UNID, ""),
    "roubo_banco": ("Roubo a banco.", CONT, UNID, ""),
    "roubo_cx_eletronico": ("Roubo a caixa eletrônico.", CONT, UNID, ""),
    "roubo_conducao_saque": ("Roubo com condução da vítima para saque.", CONT, UNID, ""),
    "roubo_apos_saque": ("Roubo após saque.", CONT, UNID, ""),
    "roubo_bicicleta": ("Roubo de bicicleta.", CONT, UNID, ""),
    "outros_roubos": ("Outros roubos.", CONT, UNID, ""),
    "total_roubos": ("Total de roubos.", CONT, UNID, "Difere da soma dos componentes (`roubo_rua` e demais, sem dupla contagem) em 708 linhas (5,0%). Em 707 delas (2014–2018 e 2021) a diferença é exatamente oposta à de `total_furtos`, o que sugere reclassificação entre roubo e furto nos totais. Ver `inconsist_total_roubos`."),
    # furtos
    "furto_veiculos": ("Furto de veículos.", CONT, UNID, ""),
    "furto_transeunte": ("Furto a transeunte.", CONT, UNID, ""),
    "furto_coletivo": ("Furto em transporte coletivo.", CONT, UNID, ""),
    "furto_celular": ("Furto de aparelho celular.", CONT, UNID, ""),
    "furto_bicicleta": ("Furto de bicicleta.", CONT, UNID, ""),
    "outros_furtos": ("Outros furtos.", CONT, UNID, ""),
    "total_furtos": ("Total de furtos.", CONT, UNID, "Difere da soma dos seis componentes em 738 linhas (5,2%): 707 espelham `total_roubos` (2014–2018 e 2021) e 31 são isoladas (2025). Ver `inconsist_total_furtos`."),
    # outros crimes
    "sequestro": ("Sequestro.", CONT, UNID, ""),
    "extorsao": ("Extorsão.", CONT, UNID, ""),
    "sequestro_relampago": ("Sequestro relâmpago.", CONT, UNID, ""),
    "estelionato": ("Estelionato.", CONT, UNID, ""),
    "apreensao_drogas": ("Apreensão de drogas (ocorrências).", CONT, UNID, ""),
    "posse_drogas": ("Registros de posse de drogas.", CONT, UNID, ""),
    "trafico_drogas": ("Registros de tráfico de drogas.", CONT, UNID, ""),
    "apreensao_drogas_sem_autor": ("Apreensão de drogas sem autoria identificada.", CONT, UNID, ""),
    "recuperacao_veiculos": ("Veículos recuperados.", CONT, UNID, ""),
    "apf": ("Autos de prisão em flagrante (APF).", CONT, UNID, "Sigla institucional: conferir no glossário do ISP."),
    "aaapai": ("Autos de apreensão de adolescente por prática de ato infracional (AAAPAI).", CONT, UNID, "Sigla institucional: conferir no glossário do ISP."),
    "cmp": ("Cumprimentos de mandado de prisão (CMP).", CONT, UNID, "Sigla institucional: conferir no glossário do ISP."),
    "cmba": ("Cumprimentos de mandado de busca e apreensão de adolescente (CMBA).", CONT, UNID, "Sigla institucional: conferir no glossário do ISP."),
    "ameaca": ("Ameaça.", CONT, UNID, ""),
    "pessoas_desaparecidas": ("Pessoas desaparecidas.", CONT, UNID, ""),
    "encontro_cadaver": ("Encontro de cadáver.", CONT, UNID, ""),
    "encontro_ossada": ("Encontro de ossada.", CONT, UNID, ""),
    "pol_militares_mortos_serv": ("Policiais militares mortos em serviço.", CONT, UNID, ""),
    "pol_civis_mortos_serv": ("Policiais civis mortos em serviço.", CONT, UNID, ""),
    "registro_ocorrencias": ("Total de registros de ocorrência de todos os tipos.", CONT, UNID, "Medida geral de volume de registros policiais, não de criminalidade efetiva."),
}

TIPOS_DERIVADAS = {
    "data": ("datetime64", "AAAA-MM-DD (primeiro dia do mês)"),
    "trimestre": ("int8", "1 a 4"),
    "dado_preliminar": ("bool", "verdadeiro/falso"),
    "letalidade_harmonizada": (CONT, UNID),
    "total_roubos_recalc": (CONT, UNID),
    "total_furtos_recalc": (CONT, UNID),
    "inconsist_total_roubos": ("bool", "verdadeiro/falso"),
    "inconsist_total_furtos": ("bool", "verdadeiro/falso"),
}


def linha(nome: str, desc: str, tipo: str, formato: str, obs: str) -> str:
    return f"| `{nome}` | {desc} | {tipo} | {formato} | {obs} |"


def gerar() -> str:
    faltam = [c for c in etl.COLUNAS_ESPERADAS if c not in DEFINICOES]
    sobram = [c for c in DEFINICOES if c not in etl.COLUNAS_ESPERADAS]
    sem_tipo = [c for c in etl.COLUNAS_DERIVADAS if c not in TIPOS_DERIVADAS]
    if faltam or sobram or sem_tipo:
        raise SystemExit(f"Dicionário inconsistente. Sem definição: {faltam}; a mais: {sobram}; derivadas sem tipo: {sem_tipo}")

    cab = "| Variável | Significado | Tipo (arquivo processado) | Formato / unidade | Observações e verificações |\n|---|---|---|---|---|"
    orig = "\n".join(linha(c, *DEFINICOES[c]) for c in etl.COLUNAS_ESPERADAS)
    der = "\n".join(linha(c, etl.COLUNAS_DERIVADAS[c], *TIPOS_DERIVADAS[c], "Criada em `src/etl.py`.") for c in etl.COLUNAS_DERIVADAS)
    return f"""# Dicionário de dados

Base: **Estatísticas de segurança: série histórica mensal por município desde 2014** — Instituto de Segurança Pública do Estado do Rio de Janeiro (ISP-RJ), portal ISPDados (<https://www.ispdados.rj.gov.br/>).

- **Arquivo bruto:** `data/raw/BaseMunicipioMensal.csv` (separador `;`, codificação Latin-1).
- **Arquivos processados:** `data/processed/base_municipio_mensal.parquet` e `base_municipio_mensal.csv.gz` (UTF-8).
- **Granularidade:** uma linha por município e mês (92 municípios × 153 meses = {format(92 * 153, ',').replace(',', '.')} linhas, de jan/2014 a set/2026).
- **Chave primária:** (`fmun_cod`, `ano`, `mes`), sem duplicatas.
- **Unidade das contagens:** registros mensais conforme a metodologia do ISP (ocorrências ou vítimas, a depender do indicador). Os valores **não** estão normalizados por população.

> **Como ler esta tabela.** As descrições seguem a nomenclatura do ISP-RJ. Relações marcadas com ✔ foram **verificadas empiricamente** nos dados por `src/etl.py` (ver `data/processed/etl_log.json`). Siglas institucionais (APF, AAAPAI, CMP, CMBA) e o significado exato de `fase` devem ser conferidos no glossário oficial do ISPDados antes de serem citados em publicações.

## 1. Variáveis originais (62)

{cab}
{orig}

## 2. Variáveis derivadas (criadas pelo ETL)

{cab}
{der}

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
"""


if __name__ == "__main__":
    SAIDA.write_text(gerar(), encoding="utf-8")
    print(f"Dicionário gerado: {SAIDA} ({len(etl.COLUNAS_ESPERADAS)} originais + {len(etl.COLUNAS_DERIVADAS)} derivadas)")
