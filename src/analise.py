"""Métricas e figuras das perguntas de pesquisa (RQ1, RQ2 e RQ3).

Todas as funções recebem a base tratada (``src.etl.carregar_processado``) e são usadas tanto
pelo notebook quanto pelo gerador do artigo (``src/build_artigo.py``), garantindo que os
números do texto sejam exatamente os das figuras.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from scipy import stats

from src import etl

# Paleta sóbria e legível por daltônicos (evita o vermelho de "alerta" em dados de violência).
AZUL, LARANJA, VERDE, CINZA, ROXO = "#1f4e79", "#d1782f", "#2a7f62", "#6b7280", "#6a4c93"
PALETA_REGIOES = {
    "Capital": AZUL, "Grande Niterói": LARANJA, "Baixada Fluminense": VERDE, "Interior": CINZA,
}
MES_PANDEMIA = pd.Timestamp("2020-03-01")
MES_FEMINICIDIO = pd.Timestamp("2024-10-01")
NOMES_MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_EXTENSO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
                 "setembro", "outubro", "novembro", "dezembro"]


def estilo() -> None:
    """Estilo único para todas as figuras estáticas."""
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 160, "axes.spines.top": False,
        "axes.spines.right": False, "axes.titleweight": "bold", "font.size": 10.5,
    })


def milhar(x, _pos=None) -> str:
    """Formata inteiros com ponto de milhar (padrão brasileiro)."""
    return f"{x:,.0f}".replace(",", ".")


def num_br(x: float, casas: int = 2) -> str:
    """Formata números com vírgula decimal."""
    return f"{x:.{casas}f}".replace(".", ",")


def pct_br(x: float, casas: int = 1) -> str:
    """Formata percentuais com vírgula decimal."""
    return f"{x:.{casas}f}".replace(".", ",") + "%"


# --------------------------------------------------------------------------- métricas
def calcular_metricas(df: pd.DataFrame) -> dict:
    """Calcula todos os números citados no artigo."""
    ano_fim, mes_fim = etl.ultimo_mes(df)
    cols = ["cvli", "hom_por_interv_policial", "letalidade_harmonizada", "total_roubos", "total_furtos"]
    ytd = etl.acumulado_ate_mes(df, mes_fim, cols)
    ytd["pct_interv"] = ytd["hom_por_interv_policial"] / ytd["letalidade_harmonizada"] * 100
    ytd["share_furto"] = ytd["total_furtos"] / (ytd["total_roubos"] + ytd["total_furtos"]) * 100

    anual = etl.acumulado_ate_mes(df, 12, cols)  # anos completos (2026 é parcial)
    anos_completos = [a for a in anual.index if a < ano_fim]
    mensal = etl.serie_estado_mensal(df, cols + ["hom_doloso", "registro_ocorrencias"])

    a0, a1 = int(ytd.index.min()), int(ytd.index.max())
    pico_let = int(ytd["letalidade_harmonizada"].idxmax())
    pico_pct = int(ytd["pct_interv"].idxmax())
    pico_rou = int(anual.loc[anos_completos, "total_roubos"].idxmax())
    menor_rou = int(anual.loc[anos_completos, "total_roubos"].idxmin())

    rho_ci, p_ci = stats.spearmanr(mensal["cvli"], mensal["hom_por_interv_policial"])
    rho_rf, p_rf = stats.spearmanr(mensal["total_roubos"], mensal["total_furtos"])
    media_2019 = mensal.loc["2019", "total_roubos"].mean()
    abr_2020 = int(mensal.loc["2020-04-01", "total_roubos"])

    # sensibilidade: totais oficiais x recalculados (anos completos)
    rec = df.groupby("ano")[["total_roubos", "total_roubos_recalc", "total_furtos", "total_furtos_recalc"]].sum().astype("int64")
    dif_rou = ((rec["total_roubos_recalc"] - rec["total_roubos"]) / rec["total_roubos"] * 100)
    dif_fur = ((rec["total_furtos_recalc"] - rec["total_furtos"]) / rec["total_furtos"] * 100)

    sazonal = df[df["ano"].between(2014, ano_fim - 1)].groupby("mes")["total_roubos"].sum()
    pior_mes, melhor_mes = int(sazonal.idxmax()), int(sazonal.idxmin())

    por_mun_mensal = df.groupby(["fmun", "regiao"], observed=True)["registro_ocorrencias"].mean().reset_index()
    q1, q3 = por_mun_mensal["registro_ocorrencias"].quantile([0.25, 0.75])
    limite = q3 + 1.5 * (q3 - q1)
    outliers = por_mun_mensal[por_mun_mensal["registro_ocorrencias"] > limite]["fmun"].tolist()

    return {
        "ano_fim": ano_fim, "mes_fim": mes_fim, "a0": a0, "a1": a1,
        "n_linhas": len(df), "n_municipios": int(df["fmun"].nunique()),
        "ytd": ytd, "anual": anual,
        "rq1": {
            "let_ini": int(ytd.loc[a0, "letalidade_harmonizada"]), "let_fim": int(ytd.loc[a1, "letalidade_harmonizada"]),
            "var_let": float((ytd.loc[a1, "letalidade_harmonizada"] / ytd.loc[a0, "letalidade_harmonizada"] - 1) * 100),
            "pico_let_ano": pico_let, "pico_let": int(ytd.loc[pico_let, "letalidade_harmonizada"]),
            "cvli_ini": int(ytd.loc[a0, "cvli"]), "cvli_fim": int(ytd.loc[a1, "cvli"]),
            "var_cvli": float((ytd.loc[a1, "cvli"] / ytd.loc[a0, "cvli"] - 1) * 100),
            "pct_ini": float(ytd.loc[a0, "pct_interv"]), "pct_fim": float(ytd.loc[a1, "pct_interv"]),
            "pct_pico": float(ytd.loc[pico_pct, "pct_interv"]), "pct_pico_ano": pico_pct,
            "interv_2019": int(ytd.loc[2019, "hom_por_interv_policial"]), "interv_2020": int(ytd.loc[2020, "hom_por_interv_policial"]),
            "var_interv_2020": float((ytd.loc[2020, "hom_por_interv_policial"] / ytd.loc[2019, "hom_por_interv_policial"] - 1) * 100),
            "interv_ini": int(ytd.loc[a0, "hom_por_interv_policial"]), "interv_fim": int(ytd.loc[a1, "hom_por_interv_policial"]),
            "rho": float(rho_ci), "p": float(p_ci),
            "fem_total": int(df["feminicidio"].sum()),
        },
        "rq2": {
            "pico_rou_ano": pico_rou, "pico_rou": int(anual.loc[pico_rou, "total_roubos"]),
            "menor_rou_ano": menor_rou, "menor_rou": int(anual.loc[menor_rou, "total_roubos"]),
            "queda_rou": float((anual.loc[menor_rou, "total_roubos"] / anual.loc[pico_rou, "total_roubos"] - 1) * 100),
            "ytd_rou_ini": int(ytd.loc[a0, "total_roubos"]), "ytd_rou_fim": int(ytd.loc[a1, "total_roubos"]),
            "var_rou": float((ytd.loc[a1, "total_roubos"] / ytd.loc[a0, "total_roubos"] - 1) * 100),
            "ytd_fur_ini": int(ytd.loc[a0, "total_furtos"]), "ytd_fur_fim": int(ytd.loc[a1, "total_furtos"]),
            "var_fur": float((ytd.loc[a1, "total_furtos"] / ytd.loc[a0, "total_furtos"] - 1) * 100),
            "share_ini": float(ytd.loc[a0, "share_furto"]), "share_fim": float(ytd.loc[a1, "share_furto"]),
            "share_min": float(ytd["share_furto"].min()), "share_min_ano": int(ytd["share_furto"].idxmin()),
            "razao_abr2020": float(abr_2020 / media_2019), "abr_2020": abr_2020, "media_2019": float(media_2019),
            "rho": float(rho_rf), "p": float(p_rf),
            "pior_mes": NOMES_MES[pior_mes - 1], "melhor_mes": NOMES_MES[melhor_mes - 1],
            "dif_rou_max": float(dif_rou.abs().max()), "dif_fur_max": float(dif_fur.abs().max()),
            "dif_rou_total": float((rec["total_roubos_recalc"].sum() / rec["total_roubos"].sum() - 1) * 100),
            "n_incons_rou": int(df["inconsist_total_roubos"].sum()), "n_incons_fur": int(df["inconsist_total_furtos"].sum()),
        },
        "rq3": {
            "conc": {c: etl.concentracao(df, c) for c in ["hom_doloso", "total_roubos", "total_furtos", "registro_ocorrencias"]},
            "perfil": etl.perfil_regional(df),
            "outliers": outliers, "limite_iqr": float(limite),
            "mediana_mun": float(por_mun_mensal["registro_ocorrencias"].median()),
            "zeros_hom": float((df["hom_doloso"] == 0).mean() * 100),
        },
    }


# ----------------------------------------------------------------------- figuras estáticas
def _salvar(fig, destino: Path | None) -> None:
    fig.tight_layout()
    if destino is not None:
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(destino, bbox_inches="tight", facecolor="white")


def fig_letalidade_composicao(df: pd.DataFrame, destino: Path | None = None):
    """RQ1 — composição da letalidade harmonizada (jan–mês final de cada ano) e % de intervenção."""
    estilo()
    _, mes_fim = etl.ultimo_mes(df)
    ytd = etl.acumulado_ate_mes(df, mes_fim, ["cvli", "hom_por_interv_policial", "letalidade_harmonizada"])
    pct = ytd["hom_por_interv_policial"] / ytd["letalidade_harmonizada"] * 100
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(ytd))
    ax.bar(x, ytd["cvli"], color=AZUL, label="CVLI (homicídio doloso, latrocínio e lesão seguida de morte)")
    ax.bar(x, ytd["hom_por_interv_policial"], bottom=ytd["cvli"], color=LARANJA,
           label="Mortes por intervenção de agente do Estado")
    ax.set_xticks(x, [str(a) for a in ytd.index])
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(milhar))
    ax.set_ylabel(f"Vítimas (acumulado jan–{NOMES_MES[mes_fim - 1]})")
    ax.set_title(f"Letalidade violenta no estado do RJ, acumulado de janeiro a {MESES_EXTENSO[mes_fim - 1]}")
    ax2 = ax.twinx()
    ax2.plot(x, pct, color=VERDE, marker="o", linewidth=2.2, label="% de intervenção policial (eixo direito)")
    ax2.set_ylim(0, 40)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=1, frameon=False, fontsize=9)
    _salvar(fig, destino)
    return fig


def fig_roubos_furtos_anual(df: pd.DataFrame, destino: Path | None = None):
    """RQ2 — roubos e furtos (jan–mês final) e participação dos furtos."""
    estilo()
    _, mes_fim = etl.ultimo_mes(df)
    ytd = etl.acumulado_ate_mes(df, mes_fim, ["total_roubos", "total_furtos"])
    share = ytd["total_furtos"] / (ytd["total_roubos"] + ytd["total_furtos"]) * 100
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.35, 1]})
    axes[0].plot(ytd.index, ytd["total_roubos"], marker="o", color=AZUL, linewidth=2.2, label="Roubos")
    axes[0].plot(ytd.index, ytd["total_furtos"], marker="s", color=LARANJA, linewidth=2.2, label="Furtos")
    axes[0].axvline(2020, color=CINZA, linestyle=":", linewidth=1.3)
    axes[0].text(2020.1, axes[0].get_ylim()[1] * 0.97, "pandemia", color=CINZA, fontsize=9, va="top")
    axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(milhar))
    axes[0].set_xticks(ytd.index, [str(a) for a in ytd.index], rotation=45)
    axes[0].set_ylim(0, None)
    axes[0].set_ylabel(f"Registros (acumulado jan–{NOMES_MES[mes_fim - 1]})")
    axes[0].set_title("Roubos e furtos")
    axes[0].legend(frameon=False)
    sns.barplot(x=[str(a) for a in share.index], y=share.values, color=VERDE, ax=axes[1])
    axes[1].axhline(50, color=CINZA, linestyle="--", linewidth=1)
    axes[1].set_ylim(0, 80)
    axes[1].yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].set_ylabel("Furtos / (roubos + furtos)")
    axes[1].set_xlabel("")
    axes[1].set_title("Participação dos furtos")
    _salvar(fig, destino)
    return fig


def fig_sazonalidade_roubos(df: pd.DataFrame, destino: Path | None = None):
    """RQ2 — mapa de calor de roubos por mês e ano (estado)."""
    estilo()
    t = df.groupby(["ano", "mes"])["total_roubos"].sum().astype("int64").unstack("mes")
    t.columns = NOMES_MES[: t.shape[1]] if t.shape[1] <= 12 else t.columns
    fig, ax = plt.subplots(figsize=(9.5, 5))
    sns.heatmap(t / 1000, cmap=sns.light_palette(AZUL, as_cmap=True), annot=True, fmt=".1f",
                linewidths=0.5, cbar_kws={"label": "Roubos no mês (milhares)"}, ax=ax,
                annot_kws={"size": 8})
    ax.set_title("Roubos por mês e ano no estado do RJ (milhares)")
    ax.grid(False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    _salvar(fig, destino)
    return fig


def fig_lorenz(df: pd.DataFrame, destino: Path | None = None):
    """RQ3 — curvas de Lorenz da distribuição entre municípios."""
    estilo()
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    for col, nome, cor in [("hom_doloso", "Homicídios dolosos", AZUL),
                           ("total_roubos", "Roubos", LARANJA),
                           ("total_furtos", "Furtos", VERDE)]:
        por_mun = df.groupby("fmun")[col].sum().astype("int64")
        x, y = etl.curva_lorenz(por_mun.values)
        ax.plot(x, y, color=cor, linewidth=2.2, label=f"{nome} (Gini = {etl.gini(por_mun.values):.2f})".replace(".", ","))
    ax.plot([0, 1], [0, 1], color=CINZA, linestyle="--", linewidth=1, label="Distribuição igualitária")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("Municípios acumulados (do menor para o maior volume)")
    ax.set_ylabel("Ocorrências acumuladas")
    ax.set_title("Concentração entre os 92 municípios")
    ax.legend(frameon=False, loc="upper left")
    ax.set_aspect("equal")
    _salvar(fig, destino)
    return fig


def fig_boxplot_regioes(df: pd.DataFrame, destino: Path | None = None):
    """RQ3 — dispersão do volume mensal médio de registros por município e região."""
    estilo()
    t = df.groupby(["fmun", "regiao"], observed=True)["registro_ocorrencias"].mean().reset_index()
    t["regiao"] = t["regiao"].astype(str)
    ordem = [r for r in etl.ORDEM_REGIOES if r in t["regiao"].unique()]
    fig, ax = plt.subplots(figsize=(8.6, 5))
    sns.boxplot(data=t, x="regiao", y="registro_ocorrencias", order=ordem, hue="regiao", palette=PALETA_REGIOES,
                legend=False, fliersize=0, width=0.55, ax=ax)
    sns.stripplot(data=t, x="regiao", y="registro_ocorrencias", order=ordem, color="black", size=3.2, alpha=0.55, ax=ax)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(milhar))
    ax.set_xlabel("")
    ax.set_ylabel("Registros por mês, média do município (escala log)")
    ax.set_title("Dispersão do volume de registros entre municípios")
    cap = t[t["fmun"] == "Rio de Janeiro"]
    if len(cap):
        ax.annotate("Rio de Janeiro", (0, float(cap["registro_ocorrencias"].iloc[0])), xytext=(0.35, float(cap["registro_ocorrencias"].iloc[0]) * 1.0),
                    fontsize=9, color=AZUL, va="center")
    _salvar(fig, destino)
    return fig


# ---------------------------------------------------------------------- figuras interativas
def _layout_plotly(fig: go.Figure, titulo: str, altura: int = 440) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, x=0.01, font=dict(size=15)), template="plotly_white", height=altura,
        margin=dict(l=55, r=20, t=60, b=50), hovermode="x unified", autosize=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13),
    )
    return fig


def plot_letalidade_mensal(df: pd.DataFrame) -> go.Figure:
    """RQ1 — CVLI e intervenção policial por mês, com média móvel de 12 meses."""
    m = etl.serie_estado_mensal(df, ["cvli", "hom_por_interv_policial"])
    fig = go.Figure()
    for col, nome, cor in [("cvli", "CVLI", AZUL), ("hom_por_interv_policial", "Intervenção de agente do Estado", LARANJA)]:
        fig.add_trace(go.Scatter(x=m.index, y=m[col], name=f"{nome} (mensal)", mode="lines",
                                 line=dict(color=cor, width=1), opacity=0.35, hovertemplate="%{y:,.0f}"))
        fig.add_trace(go.Scatter(x=m.index, y=m[col].rolling(12).mean(), name=f"{nome} (média móvel 12 meses)",
                                 mode="lines", line=dict(color=cor, width=3), hovertemplate="%{y:,.0f}"))
    fig.add_vline(x=MES_PANDEMIA, line_dash="dot", line_color=CINZA)
    fig.add_annotation(x=MES_PANDEMIA, y=1, yref="paper", text="mar/2020: pandemia", showarrow=False, xanchor="left", font=dict(size=11, color=CINZA))
    fig.update_yaxes(title="Vítimas por mês", rangemode="tozero", separatethousands=True)
    return _layout_plotly(fig, "Letalidade violenta mensal no estado do RJ")


def plot_roubos_furtos_mensal(df: pd.DataFrame) -> go.Figure:
    """RQ2 — roubos e furtos mensais no estado."""
    m = etl.serie_estado_mensal(df, ["total_roubos", "total_furtos"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=m.index, y=m["total_roubos"], name="Roubos", mode="lines", line=dict(color=AZUL, width=2.6), hovertemplate="%{y:,.0f}"))
    fig.add_trace(go.Scatter(x=m.index, y=m["total_furtos"], name="Furtos", mode="lines", line=dict(color=LARANJA, width=2.6), hovertemplate="%{y:,.0f}"))
    fig.add_vline(x=MES_PANDEMIA, line_dash="dot", line_color=CINZA)
    fig.add_annotation(x=MES_PANDEMIA, y=1, yref="paper", text="mar/2020: pandemia", showarrow=False, xanchor="left", font=dict(size=11, color=CINZA))
    fig.update_yaxes(title="Registros por mês", rangemode="tozero", separatethousands=True)
    return _layout_plotly(fig, "Roubos e furtos mensais no estado do RJ")


def plot_perfil_regional(df: pd.DataFrame) -> go.Figure:
    """RQ3 — participação de cada região em cada tipo de ocorrência."""
    p = etl.perfil_regional(df)
    tipos = [("pct_homicidios", "Homicídios dolosos"), ("pct_roubos", "Roubos"),
             ("pct_furtos", "Furtos"), ("pct_registros", "Todos os registros")]
    fig = go.Figure()
    for regiao in p.index:
        fig.add_trace(go.Bar(
            x=[t[1] for t in tipos], y=[float(p.loc[regiao, t[0]]) for t in tipos], name=str(regiao),
            marker_color=PALETA_REGIOES[str(regiao)], hovertemplate="%{y:.1f}%",
        ))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Participação no total do estado (%)", ticksuffix="%", range=[0, 100])
    return _layout_plotly(fig, "Participação de cada região por tipo de ocorrência (2014 a 2026)")


def plot_top_municipios(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """RQ3 — municípios com mais homicídios dolosos e participação acumulada."""
    t = df.groupby(["fmun", "regiao"], observed=True)["hom_doloso"].sum().astype("int64").reset_index()
    t = t.sort_values("hom_doloso", ascending=False)
    t["acum"] = t["hom_doloso"].cumsum() / t["hom_doloso"].sum() * 100
    top = t.head(n).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=top["hom_doloso"], y=top["fmun"], orientation="h",
        marker_color=[PALETA_REGIOES[str(r)] for r in top["regiao"]],
        customdata=np.stack([top["regiao"].astype(str), top["acum"]], axis=-1),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} homicídios dolosos<br>Região: %{customdata[0]}<br>"
                      "Acumulado do ranking: %{customdata[1]:.1f}%<extra></extra>",
    ))
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(title="Homicídios dolosos no período (2014 a 2026)", separatethousands=True)
    return _layout_plotly(fig, f"Os {n} municípios com mais homicídios dolosos", altura=460)
