"""ETL da base de estatísticas de segurança do ISP-RJ (série mensal por município).

Fonte: Instituto de Segurança Pública do Estado do Rio de Janeiro (ISP-RJ), portal ISPDados.
O pipeline é determinístico e NÃO destrutivo: o arquivo bruto nunca é alterado, nenhuma linha
é descartada e toda decisão de tratamento fica registrada em ``data/processed/etl_log.json``.

Uso (a partir da raiz do repositório)::

    python -m src.etl
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

LOG = logging.getLogger("etl")

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO_BRUTO = RAIZ / "data" / "raw" / "BaseMunicipioMensal.csv"
PASTA_PROCESSADOS = RAIZ / "data" / "processed"

# O arquivo do ISP usa ponto e vírgula como separador e codificação Latin-1.
CODIFICACAO = "latin-1"
SEPARADOR = ";"

COLUNAS_ID = ["fmun_cod", "fmun", "ano", "mes", "mes_ano", "regiao", "fase"]
COLUNAS_CHAVE = ["fmun_cod", "ano", "mes"]

COLUNAS_ESPERADAS = [
    "fmun_cod", "fmun", "ano", "mes", "mes_ano", "regiao", "hom_doloso", "lesao_corp_morte",
    "latrocinio", "cvli", "hom_por_interv_policial", "feminicidio", "letalidade_violenta",
    "tentat_hom", "tentativa_feminicidio", "lesao_corp_dolosa", "estupro", "hom_culposo",
    "lesao_corp_culposa", "roubo_transeunte", "roubo_celular", "roubo_em_coletivo", "roubo_rua",
    "roubo_veiculo", "roubo_carga", "roubo_comercio", "roubo_residencia", "roubo_banco",
    "roubo_cx_eletronico", "roubo_conducao_saque", "roubo_apos_saque", "roubo_bicicleta",
    "outros_roubos", "total_roubos", "furto_veiculos", "furto_transeunte", "furto_coletivo",
    "furto_celular", "furto_bicicleta", "outros_furtos", "total_furtos", "sequestro", "extorsao",
    "sequestro_relampago", "estelionato", "apreensao_drogas", "posse_drogas", "trafico_drogas",
    "apreensao_drogas_sem_autor", "recuperacao_veiculos", "apf", "aaapai", "cmp", "cmba",
    "ameaca", "pessoas_desaparecidas", "encontro_cadaver", "encontro_ossada",
    "pol_militares_mortos_serv", "pol_civis_mortos_serv", "registro_ocorrencias", "fase",
]
COLUNAS_CONTAGEM = [c for c in COLUNAS_ESPERADAS if c not in COLUNAS_ID]

# Componentes dos totais. ``roubo_rua`` já agrega transeunte + celular + coletivo (verificado
# em 100% das linhas), por isso esses três não entram na soma para evitar contagem dupla.
COMPONENTES_ROUBOS = [
    "roubo_rua", "roubo_veiculo", "roubo_carga", "roubo_comercio", "roubo_residencia",
    "roubo_banco", "roubo_cx_eletronico", "roubo_conducao_saque", "roubo_apos_saque",
    "roubo_bicicleta", "outros_roubos",
]
COMPONENTES_FURTOS = [
    "furto_veiculos", "furto_transeunte", "furto_coletivo", "furto_celular",
    "furto_bicicleta", "outros_furtos",
]
# Séries que só passam a ser coletadas em out/2024; antes disso o valor é AUSENTE, não zero.
COLUNAS_COLETA_RECENTE = ["feminicidio", "tentativa_feminicidio"]
ORDEM_REGIOES = ["Capital", "Grande Niterói", "Baixada Fluminense", "Interior"]

COLUNAS_DERIVADAS = {
    "data": "Primeiro dia do mês de referência (datetime), obtido de `mes_ano`.",
    "trimestre": "Trimestre do ano (1 a 4).",
    "dado_preliminar": "Verdadeiro quando `fase` = 2 (dados ainda em consolidação).",
    "letalidade_harmonizada": "`cvli` + `hom_por_interv_policial`: definição comparável em toda a série (exclui feminicídio).",
    "total_roubos_recalc": "Soma dos componentes de roubo (sem dupla contagem), para teste de sensibilidade.",
    "total_furtos_recalc": "Soma dos componentes de furto, para teste de sensibilidade.",
    "inconsist_total_roubos": "Verdadeiro quando `total_roubos` difere da soma dos componentes.",
    "inconsist_total_furtos": "Verdadeiro quando `total_furtos` difere da soma dos componentes.",
}


# --------------------------------------------------------------------------- leitura
def ler_base_bruta(caminho: Path = ARQUIVO_BRUTO) -> pd.DataFrame:
    """Lê o CSV bruto do ISP-RJ (separador ``;`` e codificação Latin-1)."""
    return pd.read_csv(caminho, sep=SEPARADOR, encoding=CODIFICACAO)


def hash_arquivo(caminho: Path) -> str:
    """SHA-256 do arquivo, para rastrear exatamente qual versão do dado foi processada."""
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ------------------------------------------------------------------------- validação
def validar_esquema(df: pd.DataFrame) -> dict:
    """Valida estrutura e integridade. Falha (ValueError) em problemas graves."""
    faltantes = [c for c in COLUNAS_ESPERADAS if c not in df.columns]
    extras = [c for c in df.columns if c not in COLUNAS_ESPERADAS]
    if faltantes:
        raise ValueError(f"Colunas ausentes na base: {faltantes}")

    duplicadas = int(df.duplicated(COLUNAS_CHAVE).sum())
    if duplicadas:
        raise ValueError(f"{duplicadas} linhas com chave (município, ano, mês) duplicada")

    negativos = {c: int((df[c] < 0).sum()) for c in COLUNAS_CONTAGEM if (df[c] < 0).any()}
    if negativos:
        raise ValueError(f"Valores negativos em contagens: {negativos}")

    por_mes = df.groupby(["ano", "mes"]).size()
    return {
        "colunas_extras": extras,
        "chaves_duplicadas": duplicadas,
        "municipios": int(df["fmun_cod"].nunique()),
        "painel_balanceado": bool(por_mes.nunique() == 1),
        "linhas_por_mes": int(por_mes.iloc[0]),
        "periodo": [str(df["mes_ano"].iloc[0]), str(df["mes_ano"].iloc[-1])],
    }


# ------------------------------------------------------------------------- tratamento
def tratar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Converte tipos, sinaliza inconsistências e cria métricas derivadas.

    Nenhuma linha é removida e nenhum valor original é sobrescrito; as correções são
    expressas por colunas novas (flags e valores recalculados).
    """
    n_entrada = len(df)
    nulos_antes = {c: int(v) for c, v in df.isna().sum().items() if v}
    out = df.copy()

    # tipos
    out["data"] = pd.to_datetime(out["mes_ano"].str.replace("m", "-", regex=False) + "-01")
    coerente = ((out["data"].dt.year == out["ano"]) & (out["data"].dt.month == out["mes"])).all()
    if not coerente:
        raise ValueError("`mes_ano` inconsistente com `ano` e `mes`")
    out["trimestre"] = out["data"].dt.quarter.astype("int8")
    out["fmun_cod"] = out["fmun_cod"].astype("int32")
    out["ano"] = out["ano"].astype("int16")
    out["mes"] = out["mes"].astype("int8")
    out["fase"] = out["fase"].astype("int8")
    out["regiao"] = pd.Categorical(out["regiao"], categories=ORDEM_REGIOES, ordered=False)
    # Int32 anulável: preserva o ausente (NA) das séries de coleta recente em vez de virar 0.
    for col in COLUNAS_CONTAGEM:
        out[col] = out[col].astype("Int32")

    # sinalizações e recálculos
    out["dado_preliminar"] = out["fase"].eq(2)
    out["total_roubos_recalc"] = out[COMPONENTES_ROUBOS].sum(axis=1).astype("Int32")
    out["total_furtos_recalc"] = out[COMPONENTES_FURTOS].sum(axis=1).astype("Int32")
    out["inconsist_total_roubos"] = (out["total_roubos"] != out["total_roubos_recalc"]).astype(bool)
    out["inconsist_total_furtos"] = (out["total_furtos"] != out["total_furtos_recalc"]).astype(bool)
    out["letalidade_harmonizada"] = (out["cvli"] + out["hom_por_interv_policial"]).astype("Int32")

    # verificação de identidades (documentadas no dicionário de dados)
    ident_cvli = bool((out["cvli"] == out["hom_doloso"] + out["lesao_corp_morte"] + out["latrocinio"]).all())
    com_fem = out["feminicidio"].notna()
    ident_letal = bool(
        (out.loc[com_fem, "letalidade_violenta"]
         == out.loc[com_fem, "cvli"] + out.loc[com_fem, "hom_por_interv_policial"] + out.loc[com_fem, "feminicidio"]).all()
    )
    ident_letal_antiga = bool(
        (out.loc[~com_fem, "letalidade_violenta"]
         == out.loc[~com_fem, "cvli"] + out.loc[~com_fem, "hom_por_interv_policial"]).all()
    )
    ident_rua = bool((out["roubo_rua"] == out["roubo_transeunte"] + out["roubo_celular"] + out["roubo_em_coletivo"]).all())

    inicio_fem = out.loc[com_fem, "data"].min()
    log = {
        "linhas_entrada": n_entrada,
        "linhas_saida": len(out),
        "linhas_removidas": n_entrada - len(out),
        "colunas_entrada": len(df.columns),
        "colunas_saida": len(out.columns),
        "nulos_antes": nulos_antes,
        "decisao_nulos": "feminicidio e tentativa_feminicidio mantidos como NA antes de "
                         f"{inicio_fem:%Y-%m}: série inexistente, não igual a zero.",
        "linhas_dado_preliminar": int(out["dado_preliminar"].sum()),
        "linhas_inconsist_total_roubos": int(out["inconsist_total_roubos"].sum()),
        "linhas_inconsist_total_furtos": int(out["inconsist_total_furtos"].sum()),
        "identidades_verificadas": {
            "cvli = hom_doloso + lesao_corp_morte + latrocinio": ident_cvli,
            "letalidade_violenta = cvli + interv. policial + feminicidio (desde out/2024)": ident_letal,
            "letalidade_violenta = cvli + interv. policial (antes de out/2024)": ident_letal_antiga,
            "roubo_rua = transeunte + celular + coletivo": ident_rua,
        },
    }
    return out, log


# --------------------------------------------------------------------- métricas puras
def ultimo_mes(df: pd.DataFrame) -> tuple[int, int]:
    """(ano, mês) mais recente presente na base."""
    d = df["data"].max()
    return int(d.year), int(d.month)


def serie_estado_mensal(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Soma estadual por mês (índice = data)."""
    return df.groupby("data")[colunas].sum().astype("int64")


def acumulado_ate_mes(df: pd.DataFrame, ate_mes: int, colunas: list[str]) -> pd.DataFrame:
    """Soma estadual por ano considerando só os meses 1..ate_mes.

    Permite comparar 2026 (ano parcial) com os demais anos em base homogênea.
    """
    return df[df["mes"] <= ate_mes].groupby("ano")[colunas].sum().astype("int64")


def gini(valores) -> float:
    """Coeficiente de Gini (0 = distribuição igual; 1 = concentração total)."""
    v = np.sort(np.asarray(valores, dtype=float))
    n = v.size
    if n == 0 or v.sum() == 0:
        return float("nan")
    idx = np.arange(1, n + 1)
    return float(2 * np.sum(idx * v) / (n * v.sum()) - (n + 1) / n)


def curva_lorenz(valores) -> tuple[np.ndarray, np.ndarray]:
    """Pontos (x, y) da curva de Lorenz."""
    v = np.sort(np.asarray(valores, dtype=float))
    x = np.r_[0.0, np.arange(1, v.size + 1) / v.size]
    y = np.r_[0.0, np.cumsum(v) / v.sum()]
    return x, y


def concentracao(df: pd.DataFrame, coluna: str) -> dict:
    """Participação dos maiores municípios e Gini do total do período."""
    por_mun = df.groupby("fmun")[coluna].sum().astype("int64").sort_values(ascending=False)
    acum = por_mun.cumsum() / por_mun.sum()
    return {
        "top1": float(acum.iloc[0]), "top5": float(acum.iloc[4]), "top10": float(acum.iloc[9]),
        "gini": gini(por_mun.values), "municipio_top1": str(por_mun.index[0]),
    }


def perfil_regional(df: pd.DataFrame) -> pd.DataFrame:
    """Totais, participações (%) e razão roubos/homicídios por região."""
    cols = ["hom_doloso", "letalidade_violenta", "total_roubos", "total_furtos", "registro_ocorrencias"]
    r = df.groupby("regiao", observed=True)[cols].sum().astype("int64")
    for c, nome in [("hom_doloso", "pct_homicidios"), ("total_roubos", "pct_roubos"),
                    ("total_furtos", "pct_furtos"), ("registro_ocorrencias", "pct_registros")]:
        r[nome] = r[c] / r[c].sum() * 100
    r["roubos_por_homicidio"] = r["total_roubos"] / r["hom_doloso"]
    r["n_municipios"] = df.groupby("regiao", observed=True)["fmun"].nunique()
    return r


# ------------------------------------------------------------------------- persistência
def salvar(df: pd.DataFrame, log: dict, pasta: Path = PASTA_PROCESSADOS) -> dict:
    """Grava Parquet, CSV comprimido (.csv.gz) e o log do ETL."""
    pasta.mkdir(parents=True, exist_ok=True)
    pq, gz, js = (pasta / n for n in ("base_municipio_mensal.parquet",
                                       "base_municipio_mensal.csv.gz", "etl_log.json"))
    df.to_parquet(pq, index=False, compression="zstd")
    # mtime=0 e nome vazio no cabeçalho: o .gz fica idêntico a cada execução (determinístico)
    texto_csv = df.to_csv(index=False, date_format="%Y-%m-%d")
    with open(gz, "wb") as bruto_gz, gzip.GzipFile(filename="", mode="wb", fileobj=bruto_gz, mtime=0) as f:
        f.write(texto_csv.encode("utf-8"))
    log["saidas"] = {p.name: p.stat().st_size for p in (pq, gz)}
    js.write_text(json.dumps(log, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return log


def carregar_processado(pasta: Path = PASTA_PROCESSADOS) -> pd.DataFrame:
    """Carrega a base tratada (Parquet) pronta para análise."""
    return pd.read_parquet(pasta / "base_municipio_mensal.parquet")


def executar_pipeline(bruto: Path = ARQUIVO_BRUTO, saida: Path = PASTA_PROCESSADOS) -> tuple[pd.DataFrame, dict]:
    """Executa leitura → validação → tratamento → persistência."""
    LOG.info("Lendo %s", bruto)
    df = ler_base_bruta(bruto)
    verificacao = validar_esquema(df)
    LOG.info("Validação ok: %s municípios, período %s a %s",
             verificacao["municipios"], *verificacao["periodo"])
    tratado, log = tratar(df)
    log.update({
        "validacao": verificacao,
        "arquivo_bruto": bruto.name,
        "sha256_bruto": hash_arquivo(bruto),
        "executado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ambiente": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
    })
    log = salvar(tratado, log, saida)
    LOG.info("Processado: %s linhas, %s colunas, %s removidas",
             log["linhas_saida"], log["colunas_saida"], log["linhas_removidas"])
    return tratado, log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ETL ISP-RJ — base mensal por município")
    ap.add_argument("--bruto", type=Path, default=ARQUIVO_BRUTO)
    ap.add_argument("--saida", type=Path, default=PASTA_PROCESSADOS)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    executar_pipeline(args.bruto, args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
