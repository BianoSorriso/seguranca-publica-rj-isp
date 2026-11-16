"""Gera o artigo acadêmico estático ``docs/index.html`` a partir da base tratada.

Todos os números do texto vêm de ``src.analise.calcular_metricas``; as figuras são as mesmas do
notebook. Uso (raiz do repositório): ``python -m src.build_artigo``
"""
from __future__ import annotations

import html
import inspect
import json
import re
from pathlib import Path

from src import analise, etl

DOCS = etl.RAIZ / "docs"
ASSETS = DOCS / "assets"

# ---- identificação (ajuste aqui, se necessário, e rode novamente) ----------------------------
AUTOR = "FABIANO BASTOS"
USUARIO_GITHUB = "BianoSorriso"
REPOSITORIO = "seguranca-publica-rj-isp"
REPO_URL = f"https://github.com/{USUARIO_GITHUB}/{REPOSITORIO}"
PAGES_URL = f"https://{USUARIO_GITHUB.lower()}.github.io/{REPOSITORIO}/"
SEMESTRE = "2026.2"
FONTE_URL = "https://www.ispdados.rj.gov.br/"

CSS = """
:root{--tx:#1c2433;--mut:#5f6b7c;--az:#17456f;--az2:#2563a8;--la:#d1782f;--ve:#2a7f62;--rd:#b4443a;--bg:#fbfaf7;--card:#fff;--bg2:#f1f3f7;--bd:#dde2ea;--sh:0 1px 2px rgba(16,24,40,.05),0 4px 14px rgba(16,24,40,.06);--hero1:#10345a;--hero2:#1d5a94}
@media (prefers-color-scheme:dark){:root{--tx:#e6e9ef;--mut:#9aa6b8;--az:#8fbce6;--az2:#8fbce6;--la:#f0a56a;--ve:#6fcfa8;--rd:#f08a80;--bg:#0f1520;--card:#17202e;--bg2:#1b2636;--bd:#2c3a4f;--sh:0 1px 2px rgba(0,0,0,.4),0 4px 14px rgba(0,0,0,.3);--hero1:#0b2542;--hero2:#14426d}}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:20px}
body{margin:0;background:var(--bg);color:var(--tx);font:18px/1.75 Georgia,'Times New Roman',serif;-webkit-font-smoothing:antialiased}
.sans,.meta,.badges,.btn,.toc,.kpi,figcaption,table,.nota,.kw,footer,.eyebrow{font-family:system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
#progress{position:fixed;top:0;left:0;height:3px;width:0;background:var(--la);z-index:50}
/* hero */
.hero{background:linear-gradient(135deg,var(--hero1),var(--hero2));color:#fff;padding:56px 20px 76px}
.hero .in{max-width:1120px;margin:0 auto}
.eyebrow{display:inline-block;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;background:rgba(255,255,255,.14);padding:5px 12px;border-radius:99px;margin-bottom:18px}
.hero h1{font:700 clamp(1.7rem,3.6vw,2.7rem)/1.18 Georgia,serif;margin:0 0 10px;max-width:880px;color:#fff}
.hero .sub{font:1.1rem/1.5 system-ui,sans-serif;opacity:.88;max-width:760px;margin:0 0 24px}
.meta{display:flex;flex-wrap:wrap;gap:10px 28px;font-size:.9rem;opacity:.95;margin-bottom:22px}
.meta span b{display:block;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;opacity:.7;font-weight:600}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px;font-size:.76rem}
.badge{display:inline-flex;border-radius:5px;overflow:hidden;text-decoration:none;border:1px solid rgba(255,255,255,.28)}
.badge span{padding:3px 9px}.badge .k{background:rgba(255,255,255,.12);color:#fff}.badge .v{background:#fff;color:var(--hero1);font-weight:600}
.btns{display:flex;flex-wrap:wrap;gap:10px}
.btn{display:inline-block;padding:10px 18px;background:#fff;color:var(--hero1);border-radius:8px;text-decoration:none;font-size:.92rem;font-weight:600}
.btn.ghost{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.5)}
.btn:hover{transform:translateY(-1px)}
/* kpis */
.kpis{max-width:1120px;margin:-46px auto 0;padding:0 20px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;position:relative}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px;box-shadow:var(--sh);border-top:4px solid var(--az2)}
.kpi.o{border-top-color:var(--la)}.kpi.g{border-top-color:var(--ve)}.kpi.r{border-top-color:var(--rd)}
.kpi .n{font-size:2rem;font-weight:800;line-height:1.1;color:var(--az);letter-spacing:-.02em}
.kpi.o .n{color:var(--la)}.kpi.g .n{color:var(--ve)}.kpi.r .n{color:var(--rd)}
.kpi .l{font-size:.84rem;color:var(--mut);margin-top:6px;line-height:1.4}
/* layout */
.layout{max-width:1120px;margin:40px auto 0;padding:0 20px;display:grid;grid-template-columns:230px minmax(0,1fr);gap:48px}
.toc{position:sticky;top:24px;align-self:start;font-size:.88rem;max-height:calc(100vh - 48px);overflow:auto}
.toc h4{margin:0 0 10px;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.toc a{display:block;padding:6px 12px;color:var(--mut);text-decoration:none;border-left:2px solid var(--bd);line-height:1.35}
.toc a:hover{color:var(--az)}
.toc a.on{color:var(--az);border-left-color:var(--la);font-weight:600;background:var(--bg2)}
main{min-width:0;padding-bottom:40px}
main>p,main>ul,main>ol,main>h3,main>.tw,main>pre,main>.nota{max-width:720px}
h2{font:700 1.65rem/1.25 Georgia,serif;margin:2.6em 0 .7em;color:var(--az);padding-top:.2em;display:flex;align-items:baseline;gap:12px}
h2::after{content:"";flex:1;height:1px;background:var(--bd)}
h3{font:700 1.15rem/1.3 system-ui,sans-serif;margin:2em 0 .5em;color:var(--tx)}
p{margin:.9em 0}
ul{padding-left:1.2em}li{margin:.3em 0}
a{color:var(--az2);text-underline-offset:3px}
strong{color:var(--tx)}
/* resumo */
.resumo{background:var(--card);border:1px solid var(--bd);border-left:5px solid var(--az2);border-radius:10px;padding:20px 26px;margin:0 0 20px;box-shadow:var(--sh);max-width:none}
.resumo h2{display:block;font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;font-family:system-ui,sans-serif;margin:0 0 8px;color:var(--mut);padding:0}
.resumo h2::after{display:none}
.resumo p{margin:.5em 0;font-size:1.02rem;line-height:1.7}
.kw{font-size:.86rem;color:var(--mut)}
/* figuras */
figure{margin:2em 0;background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px;box-shadow:var(--sh);text-align:center}
figure img{max-width:100%;height:auto;border-radius:6px;background:#fff}
figcaption{font-size:.84rem;color:var(--mut);margin-top:10px;text-align:left;line-height:1.5;padding:0 4px}
figcaption strong{color:var(--az)}
.pl{text-align:left}
/* tabelas */
.tw{overflow-x:auto;margin:1.4em 0;border:1px solid var(--bd);border-radius:10px;background:var(--card);box-shadow:var(--sh)}
table{border-collapse:collapse;width:100%;font-size:.88rem;margin:0}
caption{caption-side:top;text-align:left;font-weight:700;padding:12px 14px 8px;color:var(--az)}
th,td{padding:10px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--bd)}
th{background:var(--bg2);font-size:.76rem;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}
tbody tr:nth-child(even){background:var(--bg2)}tbody tr:last-child td{border-bottom:0}
/* codigo */
pre{background:#0d1626;color:#e2e8f0;padding:16px 18px;border-radius:10px;overflow-x:auto;font-size:.8rem;line-height:1.55;border:1px solid #1e2c44}
code{font-family:ui-monospace,SFMono-Regular,Consolas,Menlo,monospace}
p code,td code,li code{background:var(--bg2);border:1px solid var(--bd);padding:1px 6px;border-radius:4px;font-size:.84em}
.nota{font-size:.9rem;background:var(--bg2);border-left:4px solid var(--la);padding:12px 16px;border-radius:0 8px 8px 0;margin:1.4em 0}
ol.ref{padding-left:1.4em}ol.ref li{margin:.7em 0;font-size:.94rem;line-height:1.55;padding-left:.2em}
footer{border-top:1px solid var(--bd);margin-top:48px;padding-top:18px;font-size:.84rem;color:var(--mut)}
#top{position:fixed;right:18px;bottom:18px;width:42px;height:42px;border-radius:50%;background:var(--az2);color:#fff;border:0;font-size:1.2rem;cursor:pointer;box-shadow:var(--sh);opacity:0;pointer-events:none;transition:opacity .2s}
#top.show{opacity:1;pointer-events:auto}
@media (max-width:980px){.layout{grid-template-columns:1fr;gap:0}.toc{display:none}.kpis{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){body{font-size:17px}.hero{padding:40px 16px 70px}.kpis{gap:10px;padding:0 14px}.kpi .n{font-size:1.6rem}.layout{padding:0 14px}}
@media print{.toc,#progress,#top,.btns,.badges{display:none}.layout{display:block}.hero{background:none;color:#000;padding:0}.hero h1{color:#000}body{font-size:12pt;background:#fff}.kpis{margin-top:10px}figure,.kpi,.tw{box-shadow:none;break-inside:avoid}}
"""


# ------------------------------------------------------------------------------ formatação
def formatar(m: dict) -> dict[str, str]:
    """Converte as métricas em textos prontos (padrão numérico brasileiro)."""
    r1, r2, r3 = m["rq1"], m["rq2"], m["rq3"]
    cc, p = r3["conc"], r3["perfil"]
    ml, pc, nb = analise.milhar, analise.pct_br, analise.num_br
    mes = analise.MESES_EXTENSO[m["mes_fim"] - 1]
    v = {
        "autor": AUTOR, "semestre": SEMESTRE, "repo": REPO_URL, "pages": PAGES_URL, "fonte": FONTE_URL,
        "n_linhas": ml(m["n_linhas"]), "n_mun": str(m["n_municipios"]), "a0": str(m["a0"]), "a1": str(m["a1"]),
        "mes_fim": mes,
        # RQ1
        "let_ini": ml(r1["let_ini"]), "let_fim": ml(r1["let_fim"]), "var_let": pc(abs(r1["var_let"])),
        "pico_let_ano": str(r1["pico_let_ano"]), "pico_let": ml(r1["pico_let"]),
        "var_cvli": pc(abs(r1["var_cvli"])), "cvli_ini": ml(r1["cvli_ini"]), "cvli_fim": ml(r1["cvli_fim"]),
        "interv_ini": ml(r1["interv_ini"]), "interv_fim": ml(r1["interv_fim"]),
        "pct_ini": pc(r1["pct_ini"]), "pct_fim": pc(r1["pct_fim"]), "pct_pico": pc(r1["pct_pico"]),
        "pct_pico_ano": str(r1["pct_pico_ano"]), "interv_2019": ml(r1["interv_2019"]), "interv_2020": ml(r1["interv_2020"]),
        "var_interv_2020": pc(abs(r1["var_interv_2020"])), "rho1": nb(r1["rho"]), "p1": nb(r1["p"], 3),
        "fem_total": ml(r1["fem_total"]),
        # RQ2
        "pico_rou_ano": str(r2["pico_rou_ano"]), "pico_rou": ml(r2["pico_rou"]), "menor_rou_ano": str(r2["menor_rou_ano"]),
        "menor_rou": ml(r2["menor_rou"]), "queda_rou": pc(abs(r2["queda_rou"])), "var_rou": pc(abs(r2["var_rou"])),
        "var_fur": pc(abs(r2["var_fur"])), "share_ini": pc(r2["share_ini"]), "share_fim": pc(r2["share_fim"]),
        "share_min": pc(r2["share_min"]), "share_min_ano": str(r2["share_min_ano"]),
        "abr_2020": ml(r2["abr_2020"]), "media_2019": ml(r2["media_2019"]), "razao_abr": pc(r2["razao_abr2020"] * 100, 0),
        "rho2": nb(r2["rho"]), "p2": nb(r2["p"], 3), "dif_rou_max": pc(r2["dif_rou_max"]), "dif_fur_max": pc(r2["dif_fur_max"]),
        "n_inc_rou": ml(r2["n_incons_rou"]), "n_inc_fur": ml(r2["n_incons_fur"]),
        # RQ3
        "top5_hom": pc(cc["hom_doloso"]["top5"] * 100), "top5_rou": pc(cc["total_roubos"]["top5"] * 100),
        "top5_fur": pc(cc["total_furtos"]["top5"] * 100), "top1_hom": pc(cc["hom_doloso"]["top1"] * 100),
        "top1_rou": pc(cc["total_roubos"]["top1"] * 100), "top10_hom": pc(cc["hom_doloso"]["top10"] * 100),
        "gini_hom": nb(cc["hom_doloso"]["gini"]), "gini_rou": nb(cc["total_roubos"]["gini"]), "gini_fur": nb(cc["total_furtos"]["gini"]),
        "rph_cap": f"{p.loc['Capital', 'roubos_por_homicidio']:.0f}", "rph_gn": f"{p.loc['Grande Niterói', 'roubos_por_homicidio']:.0f}",
        "rph_bx": f"{p.loc['Baixada Fluminense', 'roubos_por_homicidio']:.0f}", "rph_int": nb(p.loc["Interior", "roubos_por_homicidio"], 1),
        "hom_int": pc(p.loc["Interior", "pct_homicidios"]), "hom_bx": pc(p.loc["Baixada Fluminense", "pct_homicidios"]),
        "hom_cap": pc(p.loc["Capital", "pct_homicidios"]), "rou_int": pc(p.loc["Interior", "pct_roubos"]),
        "reg_bx": pc(p.loc["Baixada Fluminense", "pct_registros"]), "reg_cap": pc(p.loc["Capital", "pct_registros"]),
        "n_out": str(len(r3["outliers"])), "lim_iqr": ml(r3["limite_iqr"]), "mediana_mun": ml(r3["mediana_mun"]),
        "zeros_hom": pc(r3["zeros_hom"], 0),
    }
    return v


def trecho(funcao) -> str:
    """Código-fonte real de uma função, escapado para HTML."""
    return html.escape(inspect.getsource(funcao).rstrip())


TRECHO_TRATAR = """def tratar(df):
    out = df.copy()
    out["data"] = pd.to_datetime(out["mes_ano"].str.replace("m", "-") + "-01")
    out["regiao"] = pd.Categorical(out["regiao"], categories=ORDEM_REGIOES)
    for col in COLUNAS_CONTAGEM:               # Int32 anulável: preserva o NA do feminicídio
        out[col] = out[col].astype("Int32")

    out["dado_preliminar"] = out["fase"].eq(2)
    out["total_roubos_recalc"] = out[COMPONENTES_ROUBOS].sum(axis=1).astype("Int32")
    out["inconsist_total_roubos"] = out["total_roubos"] != out["total_roubos_recalc"]
    out["letalidade_harmonizada"] = out["cvli"] + out["hom_por_interv_policial"]
    return out      # nenhuma linha removida, nenhum valor original sobrescrito"""


# --------------------------------------------------------------------------- plotly
def bloco_plotly(fig, identificador: str, legenda: str) -> str:
    """Embute uma figura Plotly com legenda. A biblioteca é carregada de docs/assets/plotly.min.js."""
    corpo = fig.to_html(full_html=False, include_plotlyjs=False, div_id=identificador,
                        config={"responsive": True, "displaylogo": False})
    return f'<figure class="pl">{corpo}<figcaption>{legenda}</figcaption></figure>'


def figura(arquivo: str, legenda: str, alt: str) -> str:
    return (f'<figure><img src="assets/{arquivo}" alt="{html.escape(alt)}" loading="lazy">'
            f'<figcaption>{legenda}</figcaption></figure>')


# ------------------------------------------------------------------------------ texto
RESUMO_PT = (
    "Este trabalho analisa a série histórica mensal de estatísticas de segurança dos [[n_mun]] municípios do estado do "
    "Rio de Janeiro, divulgada pelo Instituto de Segurança Pública (ISP-RJ), de janeiro de [[a0]] a setembro de [[a1]] "
    "([[n_linhas]] observações município-mês). Um pipeline em Python, determinístico e não destrutivo, validou a base, "
    "preservou a ausência estrutural das séries de feminicídio, sinalizou divergências de classificação entre roubos e "
    "furtos e harmonizou a definição de letalidade violenta, alterada em outubro de 2024. Comparando janeiro a [[mes_fim]] "
    "de cada ano, a letalidade violenta harmonizada caiu [[var_let]] entre [[a0]] e [[a1]], mas a participação das mortes "
    "por intervenção de agente do Estado subiu de [[pct_ini]] para um pico de [[pct_pico]] em [[pct_pico_ano]]. Os roubos "
    "recuaram [[queda_rou]] do pico de [[pico_rou_ano]] até [[menor_rou_ano]], enquanto os furtos voltaram a crescer e "
    "passaram a representar [[share_fim]] dos registros patrimoniais em [[a1]]. A criminalidade é muito concentrada: cinco "
    "municípios reúnem [[top5_hom]] dos homicídios dolosos e [[top5_rou]] dos roubos, e o perfil das ocorrências difere "
    "entre as regiões. Por trabalhar com contagens absolutas, sem normalização populacional, os resultados descrevem o "
    "volume de registros policiais, e não o risco individual. Código, dados tratados e dicionário de variáveis seguem os "
    "princípios FAIR."
)
ABSTRACT_EN = (
    "This study analyzes the monthly series of public security statistics for the [[n_mun]] municipalities of the state of "
    "Rio de Janeiro, Brazil, published by the state Public Security Institute (ISP-RJ), from January [[a0]] to September "
    "[[a1]] ([[n_linhas]] municipality-month observations). A deterministic, non-destructive Python pipeline validated the "
    "data, kept the structural absence of the femicide series as missing values, flagged robbery/theft classification "
    "mismatches, and harmonized the definition of violent lethality, which changed in October 2024. Comparing January to "
    "September of each year, harmonized violent lethality fell [[var_let]] between [[a0]] and [[a1]], yet the share of "
    "deaths caused by state agents rose from [[pct_ini]] to a peak of [[pct_pico]] in [[pct_pico_ano]]. Robberies dropped "
    "[[queda_rou]] from the [[pico_rou_ano]] peak to [[menor_rou_ano]], while thefts grew again and reached [[share_fim]] "
    "of property-crime records in [[a1]]. Crime is highly concentrated: five municipalities account for [[top5_hom]] of "
    "intentional homicides and [[top5_rou]] of robberies, and the offense profile differs across regions. Because the "
    "analysis uses absolute counts without population adjustment, results describe the volume of police records rather "
    "than individual risk. Code, processed data, and data dictionary follow the FAIR principles."
)

CORPO = """
<h2 id="introducao">1. Introdução</h2>
<p>A segurança pública é um dos temas de maior peso na agenda social brasileira, e o estado do Rio de Janeiro reúne
características que tornam seus dados particularmente instrutivos: uma metrópole de grande porte, uma região
metropolitana densa e dezenas de municípios do interior com realidades distintas. O Instituto de Segurança Pública
(ISP-RJ) divulga, por meio do portal ISPDados, séries mensais por município que permitem examinar como a violência letal
e os crimes patrimoniais evoluíram ao longo de mais de uma década (ISP-RJ, 2026).</p>
<p>Duas questões tornam a leitura desses números menos óbvia do que parece. A primeira é que a <em>letalidade violenta</em>
reúne mortes de natureza distinta, como os homicídios e as mortes causadas por intervenção de agentes do Estado, que
podem seguir trajetórias diferentes. A segunda é que reduções em um tipo de crime podem coexistir com aumentos em outro,
o que sugere deslocamento do perfil de ocorrências, e não necessariamente melhoria geral. Este estudo trata ambas com
uma abordagem reprodutível, aderente aos princípios FAIR (WILKINSON et al., 2016): tudo o que aparece aqui pode ser
refeito a partir do repositório.</p>
<p>O trabalho responde a três perguntas de pesquisa:</p>
<ul>
<li><strong>RQ1.</strong> Como evoluiu a letalidade violenta no estado entre [[a0]] e [[a1]], e qual a participação das
mortes por intervenção de agente do Estado nela?</li>
<li><strong>RQ2.</strong> Roubos e furtos seguiram trajetórias diferentes e como reagiram à pandemia de 2020?</li>
<li><strong>RQ3.</strong> Quão concentrada geograficamente é a criminalidade e o perfil das ocorrências difere entre as
regiões do estado?</li>
</ul>

<h2 id="metodologia">2. Metodologia e pipeline de dados</h2>
<h3>2.1 Fonte e granularidade</h3>
<p>Os dados vêm do arquivo <code>BaseMunicipioMensal.csv</code>, obtido no portal ISPDados do ISP-RJ
(<a href="[[fonte]]">[[fonte]]</a>). A unidade de observação é o par <strong>município × mês</strong>: [[n_mun]]
municípios, de janeiro de [[a0]] a setembro de [[a1]], totalizando [[n_linhas]] linhas e 62 variáveis, entre elas
homicídios, roubos, furtos, apreensões e prisões. Os três últimos meses (jul a set de [[a1]]) estão marcados pela fonte
como dados ainda em consolidação (<code>fase</code> = 2) e podem ser revisados. O significado de cada variável está em
<code>data/data_dictionary.md</code>. Os valores são contagens absolutas, <strong>sem normalização por população</strong>.</p>

<h3>2.2 Tratamento dos dados</h3>
<p>O pipeline (<code>src/etl.py</code>) é determinístico e não destrutivo: lê o arquivo bruto (separador <code>;</code>,
codificação Latin-1), valida o esquema e a chave (município, ano, mês), converte tipos e grava Parquet e CSV comprimido.
Nenhuma linha é descartada e nenhum valor original é sobrescrito; cada decisão fica registrada em
<code>data/processed/etl_log.json</code>, junto do SHA-256 do arquivo bruto. A validação encontrou quatro
particularidades, tratadas como a Tabela 1 resume.</p>
<div class="tw"><table>
<caption>Tabela 1 — Inconsistências da base e decisão de tratamento</caption>
<thead><tr><th>Achado</th><th>Decisão</th></tr></thead><tbody>
<tr><td>Feminicídio e tentativa de feminicídio só existem a partir de out/2024 (11.868 valores ausentes).</td>
<td>Mantidos como ausentes (<code>NA</code>), pois a série não existia. Imputar zero criaria 129 meses de "nenhum caso".</td></tr>
<tr><td>A <code>letalidade_violenta</code> passa a somar o feminicídio em out/2024 (verificado em 100% das linhas).</td>
<td>Criada a <code>letalidade_harmonizada</code> (CVLI + mortes por intervenção de agente do Estado), comparável em toda a série.</td></tr>
<tr><td>Totais de roubos ([[n_inc_rou]] linhas) e de furtos ([[n_inc_fur]]) diferem da soma dos componentes, quase sempre em 2014–2018 e de forma espelhada.</td>
<td>Totais oficiais mantidos; criadas colunas recalculadas e <em>flags</em>. A seção 3.2 testa a sensibilidade.</td></tr>
<tr><td>Dados de jul a set/[[a1]] são preliminares.</td><td>Mantidos e sinalizados (<code>dado_preliminar</code>).</td></tr>
</tbody></table></div>
<p>O trecho a seguir resume o núcleo do tratamento (versão completa em <code>src/etl.py</code>):</p>
<pre><code>[[codigo_tratar]]</code></pre>

<h3>2.3 Métodos de análise</h3>
<p><strong>Comparabilidade temporal.</strong> Como [[a1]] cobre apenas janeiro a [[mes_fim]], os comparativos anuais usam sempre o
acumulado de janeiro a [[mes_fim]] de cada ano, evitando comparar um ano parcial com anos completos:</p>
<pre><code>[[codigo_ytd]]</code></pre>
<p><strong>Associação.</strong> A correlação de Spearman (SPEARMAN, 1904), apropriada para contagens assimétricas,
mede se duas séries mensais variam juntas. <strong>Concentração.</strong> A distribuição entre municípios é descrita pela
participação dos maiores e pelo coeficiente de Gini, calculado como abaixo e ilustrado pela curva de Lorenz (LORENZ, 1905):</p>
<pre><code>[[codigo_gini]]</code></pre>
<p><strong>Valores atípicos.</strong> Municípios atípicos são identificados pelo critério do intervalo interquartil (IQR) sobre
o volume mensal médio de registros. <strong>Sensibilidade.</strong> Repetimos as comparações com os totais recalculados para medir
quanto as divergências de classificação poderiam alterar as conclusões. A análise usa pandas (MCKINNEY, 2010), NumPy
(HARRIS et al., 2020), SciPy (VIRTANEN et al., 2020), Matplotlib (HUNTER, 2007), seaborn (WASKOM, 2021) e Plotly
(PLOTLY TECHNOLOGIES INC., 2015).</p>

<h2 id="resultados">3. Resultados e discussão</h2>

<h3>3.1 RQ1: letalidade violenta e intervenção de agentes do Estado</h3>
<p>No acumulado de janeiro a [[mes_fim]], a letalidade violenta harmonizada passou de [[let_ini]] vítimas em [[a0]] para
[[let_fim]] em [[a1]], queda de <strong>[[var_let]]</strong>, com pico em [[pico_let_ano]] ([[pico_let]]). O CVLI, isolado,
recuou [[var_cvli]] ([[cvli_ini]] para [[cvli_fim]]). As mortes por intervenção de agente do Estado, porém, foram de
[[interv_ini]] para [[interv_fim]], e por isso sua <strong>participação</strong> na letalidade foi de [[pct_ini]] em [[a0]] para
um pico de <strong>[[pct_pico]]</strong> em [[pct_pico_ano]], recuando para [[pct_fim]] em [[a1]] (Figuras 1 e 2).</p>
[[fig1]]
[[plot_letalidade]]
<p>Em 2020 as mortes por intervenção caíram [[var_interv_2020]] ([[interv_2019]] para [[interv_2020]]). O ano coincide com a
liminar da ADPF 635, concedida em 5 de junho de 2020, que restringiu operações policiais em favelas do Rio de Janeiro durante
a pandemia (BRASIL, 2020). A coincidência temporal é compatível com um efeito dessa decisão, mas os dados aqui analisados
<strong>não permitem atribuir causalidade</strong>: não há controle de operações, de mobilidade nem de outros fatores
simultâneos. A correlação mensal de Spearman entre CVLI e intervenções é fraca (ρ = [[rho1]]; p = [[p1]]), ou seja, as duas
séries não se movem juntas, o que reforça a pertinência de analisá-las separadamente.</p>
<p>Desde outubro de 2024 a base registra feminicídios: foram [[fem_total]] casos até set/[[a1]]. Como a série não existe antes disso,
o uso da letalidade harmonizada evita atribuir à queda do período uma mudança que é apenas de definição.</p>

<h3>3.2 RQ2: roubos, furtos e a pandemia</h3>
<p>Os roubos atingiram o pico anual em [[pico_rou_ano]] ([[pico_rou]] registros) e o menor valor em [[menor_rou_ano]]
([[menor_rou]]), queda de <strong>[[queda_rou]]</strong>. Na comparação de janeiro a [[mes_fim]], a redução entre [[a0]] e [[a1]]
é de [[var_rou]]. Os furtos tiveram variação de apenas [[var_fur]] (queda) no mesmo comparativo, mas a trajetória é
reveladora: recuaram entre 2014 e 2018, caíram de novo em 2020–2021, no auge da pandemia, e <strong>voltaram a crescer a partir de 2022</strong> (Figuras 3 e 4). Com isso, a participação dos
furtos no total de crimes patrimoniais (roubos + furtos) foi de [[share_ini]] em [[a0]], mínima de [[share_min]] em
[[share_min_ano]] e <strong>[[share_fim]]</strong> em [[a1]]: o perfil migrou do roubo para o furto.</p>
[[fig2]]
[[plot_rf]]
<p>O efeito da pandemia aparece de forma abrupta: em abril de 2020 houve [[abr_2020]] roubos, apenas [[razao_abr]] da média mensal
de 2019 ([[media_2019]]). Os roubos não voltaram aos patamares anteriores, enquanto os furtos se recuperaram, o que é
compatível com a hipótese de que o isolamento reduziu a exposição à abordagem em via pública. Essa explicação, porém,
<strong>não foi testada</strong> neste estudo. A correlação mensal entre roubos e furtos é fraca e negativa
(ρ = [[rho2]]; p = [[p2]]), e portanto os dois crimes não oscilam em conjunto.</p>
[[fig3]]
<p><strong>Valor atípico temporal.</strong> O mapa de calor (Figura 5) destaca fevereiro de 2017 com apenas 9,7 mil roubos, ante 14,2 mil em
janeiro e 19,5 mil em março. Furtos e total de registros caem juntos, em cerca de metade do mês seguinte, e a queda se
concentra na capital. O padrão, simultâneo em todas as categorias, sugere falha de registro ou de coleta, e não queda real, mas
a base não permite confirmar a causa; o ponto foi mantido e é tratado como limitação.</p>
<p><strong>Sensibilidade.</strong> Usar a soma dos componentes em vez dos totais oficiais altera os totais anuais em no máximo
[[dif_rou_max]] (roubos) e [[dif_fur_max]] (furtos). Pico, vale e a migração de roubo para furto permanecem, de modo que as
conclusões não dependem da escolha.</p>

<h3>3.3 RQ3: concentração geográfica e perfil regional</h3>
<p>A criminalidade é muito concentrada. Os cinco maiores municípios reúnem <strong>[[top5_hom]]</strong> dos homicídios
dolosos, <strong>[[top5_fur]]</strong> dos furtos e <strong>[[top5_rou]]</strong> dos roubos, com coeficientes de Gini de
[[gini_hom]], [[gini_fur]] e [[gini_rou]], respectivamente (Figura 6). Como a distribuição é muito assimétrica (a mediana municipal é
de [[mediana_mun]] registros por mês e [[zeros_hom]] das observações têm zero homicídio), a análise usa participações e
razões, e não médias simples entre municípios.</p>
[[fig4]]
[[plot_top]]
<p>O padrão muda conforme o tipo de crime. A capital responde por [[top1_rou]] dos roubos e por [[hom_cap]] dos homicídios; já o
Interior, com 75 municípios, concentra [[hom_int]] dos homicídios, mas só [[rou_int]] dos roubos, e a Baixada Fluminense,
[[hom_bx]] dos homicídios com [[reg_bx]] do total de registros (Figuras 7 e 8). A razão entre roubos e homicídios, que não
depende do tamanho da população por ser um quociente de duas contagens do mesmo local, ilustra a diferença de perfil:
<strong>[[rph_cap]]</strong> roubos por homicídio na Capital, [[rph_gn]] em Grande Niterói, [[rph_bx]] na Baixada e
<strong>[[rph_int]]</strong> no Interior. Em termos de política pública, isso sugere que a violência letal e a criminalidade
patrimonial exigem leituras territoriais distintas.</p>
[[plot_regional]]
[[fig5]]
<p>Pelo critério do IQR (limite de [[lim_iqr]] registros mensais; Figura 9), há [[n_out]] municípios atípicos: [[outliers]]. É preciso
cautela com a leitura: municípios maiores registram mais ocorrências por terem mais habitantes, e as comparações aqui descrevem
<em>volume</em>, e não risco.</p>

<h2 id="conclusao">4. Conclusão</h2>
<p>Entre [[a0]] e [[a1]], a letalidade violenta harmonizada no estado do Rio de Janeiro caiu [[var_let]] (janeiro a [[mes_fim]]),
mas a participação das mortes por intervenção de agentes do Estado chegou a [[pct_pico]] em [[pct_pico_ano]], o que mostra que
o total esconde trajetórias distintas. Os roubos caíram [[queda_rou]] do pico até [[menor_rou_ano]], ao passo que os furtos voltaram a
crescer e hoje respondem por cerca de dois terços dos registros patrimoniais. A criminalidade é fortemente concentrada em poucos
municípios, e o perfil das ocorrências varia entre as regiões.</p>
<p><strong>Limitações.</strong> (i) Os números são absolutos, sem taxa por 100 mil habitantes, o que limita comparações entre
municípios; (ii) [[a1]] é parcial e seus três últimos meses são preliminares; (iii) a definição de letalidade violenta mudou em
out/2024; (iv) há reclassificações entre roubo e furto em 2014–2018; (v) fevereiro de 2017 apresenta possível falha de registro;
(vi) a base mede registros policiais, que dependem também da disposição de a população registrar a ocorrência; (vii) as
interpretações sobre pandemia e ADPF 635 são hipóteses compatíveis com os dados, não efeitos estimados.</p>
<p><strong>Trabalhos futuros.</strong> Normalizar os indicadores por população (Censo e estimativas do IBGE), modelar as séries com
sazonalidade e quebras estruturais, incluir dados sobre operações policiais e mobilidade para testar as hipóteses levantadas e
estender a análise a outros estados.</p>

<h2 id="fair">5. Disponibilidade dos dados e declaração FAIR</h2>
<p>Este trabalho segue os princípios FAIR (WILKINSON et al., 2016). Todo o material está em
<a href="[[repo]]">[[repo]]</a>.</p>
<div class="tw"><table>
<thead><tr><th>Princípio</th><th>Como é atendido</th></tr></thead><tbody>
<tr><td><strong>Findable</strong></td><td><code>README.md</code> com resumo, palavras-chave e link da fonte original; autoria, disciplina, semestre e instituição no cabeçalho; metadados estruturados (JSON-LD) nesta página.</td></tr>
<tr><td><strong>Accessible</strong></td><td>Repositório público; ingestão sem credenciais; artigo publicado no GitHub Pages (pasta <code>docs/</code>), com layout responsivo.</td></tr>
<tr><td><strong>Interoperable</strong></td><td><code>data/data_dictionary.md</code> descreve as 62 variáveis originais e 8 derivadas; dados tratados em Parquet e CSV comprimido (<code>.csv.gz</code>).</td></tr>
<tr><td><strong>Reusable</strong></td><td>Código sob licença MIT; dados derivados e texto sob CC BY 4.0; <code>requirements.txt</code> com versões fixadas; ETL com registro de decisões e SHA-256 do bruto.</td></tr>
</tbody></table></div>
<p>Para reproduzir integralmente o pipeline e esta página:</p>
<pre><code>git clone [[repo]].git
cd [[nome_repo]]
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.etl                # gera data/processed/*
python -m src.gerar_dicionario   # regenera data/data_dictionary.md
python -m src.build_artigo       # regenera docs/index.html e as figuras
jupyter nbconvert --to notebook --execute --inplace notebooks/analise_exploratoria.ipynb</code></pre>
<div class="nota"><strong>Licenças.</strong> Código: MIT. Dados derivados, dicionário e texto: CC BY 4.0. Os dados brutos pertencem ao ISP-RJ;
consulte os termos de uso do portal ISPDados antes de redistribuí-los.</div>

<h2 id="referencias">6. Referências</h2>
<ol class="ref">
<li>BRASIL. Supremo Tribunal Federal. <strong>Arguição de Descumprimento de Preceito Fundamental n. 635 (ADPF 635)</strong>. Relator: Min. Edson Fachin. Medida cautelar incidental concedida em 5 jun. 2020 e referendada pelo Plenário em ago. 2020. Brasília: STF, 2020.</li>
<li>HARRIS, C. R. et al. Array programming with NumPy. <strong>Nature</strong>, v. 585, p. 357–362, 2020. DOI: 10.1038/s41586-020-2649-2.</li>
<li>HUNTER, J. D. Matplotlib: a 2D graphics environment. <strong>Computing in Science &amp; Engineering</strong>, v. 9, n. 3, p. 90–95, 2007.</li>
<li>INSTITUTO DE SEGURANÇA PÚBLICA DO ESTADO DO RIO DE JANEIRO (ISP-RJ). <strong>ISPDados: estatísticas de segurança, série histórica mensal por município desde 2014</strong> (BaseMunicipioMensal.csv). Rio de Janeiro: ISP-RJ, 2026. Disponível em: <a href="[[fonte]]">[[fonte]]</a>. Acesso em: nov. 2026.</li>
<li>LORENZ, M. O. Methods of measuring the concentration of wealth. <strong>Publications of the American Statistical Association</strong>, v. 9, n. 70, p. 209–219, 1905.</li>
<li>McKINNEY, W. Data structures for statistical computing in Python. In: PYTHON IN SCIENCE CONFERENCE, 9., 2010, Austin. <strong>Proceedings</strong> [...]. Austin: SciPy, 2010. p. 56–61.</li>
<li>PLOTLY TECHNOLOGIES INC. <strong>Collaborative data science</strong>. Montreal: Plotly Technologies Inc., 2015. Disponível em: <a href="https://plot.ly">https://plot.ly</a>.</li>
<li>SPEARMAN, C. The proof and measurement of association between two things. <strong>The American Journal of Psychology</strong>, v. 15, n. 1, p. 72–101, 1904.</li>
<li>VIRTANEN, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. <strong>Nature Methods</strong>, v. 17, p. 261–272, 2020. DOI: 10.1038/s41592-019-0686-2.</li>
<li>WASKOM, M. L. seaborn: statistical data visualization. <strong>Journal of Open Source Software</strong>, v. 6, n. 60, 3021, 2021. DOI: 10.21105/joss.03021.</li>
<li>WILKINSON, M. D. et al. The FAIR Guiding Principles for scientific data management and stewardship. <strong>Scientific Data</strong>, v. 3, 160018, 2016. DOI: 10.1038/sdata.2016.18.</li>
</ol>
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estatísticas de segurança do estado do Rio de Janeiro (2014–2026): letalidade, crimes patrimoniais e concentração territorial</title>
<meta name="description" content="Análise reprodutível (FAIR) da série mensal de segurança pública do ISP-RJ por município, de 2014 a 2026.">
<meta name="author" content="[[autor]]">
<meta name="keywords" content="segurança pública, Rio de Janeiro, letalidade violenta, crimes patrimoniais, ciência aberta">
<script src="assets/plotly.min.js"></script>
<style>[[css]]</style>
<script type="application/ld+json">[[jsonld]]</script>
</head>
<body>
<div id="progress"></div>
<header class="hero"><div class="in">
<span class="eyebrow">Artigo · Análise de dados com Python</span>
<h1>Estatísticas de segurança do estado do Rio de Janeiro (2014–2026)</h1>
<p class="sub">Letalidade violenta, crimes patrimoniais e concentração territorial nos [[n_mun]] municípios fluminenses, a partir da série mensal do ISP-RJ.</p>
<div class="meta">
<span><b>Autoria</b>[[autor]]</span>
<span><b>Curso</b>Sistemas de Informação, UniLaSalle · 6º período</span>
<span><b>Disciplina</b>Linguagem de Programação · [[semestre]]</span>
</div>
<div class="badges">
<a class="badge" href="[[repo]]"><span class="k">código</span><span class="v">MIT</span></a>
<a class="badge" href="https://creativecommons.org/licenses/by/4.0/"><span class="k">dados e texto</span><span class="v">CC BY 4.0</span></a>
<span class="badge"><span class="k">princípios</span><span class="v">FAIR</span></span>
<span class="badge"><span class="k">linguagem</span><span class="v">Python 3.12</span></span>
<span class="badge"><span class="k">fonte</span><span class="v">ISP-RJ</span></span>
</div>
<div class="btns"><a class="btn" href="[[repo]]">Ver repositório no GitHub</a><a class="btn ghost" href="#resultados">Ir aos resultados</a></div>
</div></header>
<section class="kpis" aria-label="Principais resultados">
<div class="kpi g"><div class="n">−[[var_let]]</div><div class="l">letalidade violenta harmonizada, [[a0]] a [[a1]] (jan–[[mes_fim]])</div></div>
<div class="kpi r"><div class="n">[[pct_pico]]</div><div class="l">pico da participação das mortes por intervenção de agente do Estado ([[pct_pico_ano]])</div></div>
<div class="kpi"><div class="n">−[[queda_rou]]</div><div class="l">queda dos roubos, do pico de [[pico_rou_ano]] a [[menor_rou_ano]]</div></div>
<div class="kpi o"><div class="n">[[top5_hom]]</div><div class="l">dos homicídios dolosos estão em apenas 5 municípios</div></div>
</section>
<div class="layout">
<nav class="toc" aria-label="Índice"><h4>Nesta página</h4>
<a href="#resumo">Resumo</a><a href="#introducao">1. Introdução</a><a href="#metodologia">2. Metodologia</a><a href="#resultados">3. Resultados</a><a href="#conclusao">4. Conclusão</a><a href="#fair">5. FAIR e reprodução</a><a href="#referencias">6. Referências</a></nav>
<main>
<section class="resumo" aria-labelledby="resumo">
<h2 id="resumo">Resumo</h2>
<p>[[resumo]]</p>
<p class="kw"><strong>Palavras-chave:</strong> segurança pública; Rio de Janeiro; letalidade violenta; crimes patrimoniais; ciência aberta (FAIR).</p>
</section>
<section class="resumo" aria-labelledby="abstract" lang="en" style="border-left-color:var(--la)">
<h2 id="abstract">Abstract</h2>
<p>[[abstract]]</p>
<p class="kw"><strong>Keywords:</strong> public security; Rio de Janeiro; violent lethality; property crime; open science (FAIR).</p>
</section>
[[corpo]]
<footer>
<p>[[autor]] · UniLaSalle · Linguagem de Programação, [[semestre]]. Texto e dados derivados sob
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>; código sob licença MIT.
Fonte dos dados brutos: <a href="[[fonte]]">ISP-RJ / ISPDados</a>. Página gerada por <code>src/build_artigo.py</code>.</p>
</footer>
</main>
</div>
<button id="top" aria-label="Voltar ao topo">↑</button>
<script>
(function(){
var bar=document.getElementById('progress'),top=document.getElementById('top');
var links=[].slice.call(document.querySelectorAll('.toc a'));
var secs=links.map(function(a){return document.querySelector(a.getAttribute('href'));});
function upd(){
var h=document.documentElement,st=h.scrollTop||document.body.scrollTop,mx=h.scrollHeight-h.clientHeight;
bar.style.width=(mx>0?st/mx*100:0)+'%';top.classList.toggle('show',st>600);
var cur=0;secs.forEach(function(s,i){if(s&&s.getBoundingClientRect().top<120)cur=i;});
links.forEach(function(a,i){a.classList.toggle('on',i===cur);});}
window.addEventListener('scroll',upd,{passive:true});upd();
top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
})();
</script>
</body>
</html>
"""


def contar_palavras(texto: str) -> int:
    return len(re.findall(r"\S+", texto))


def montar(df) -> tuple[str, dict]:
    """Monta o HTML completo e devolve também informações de verificação."""
    m = analise.calcular_metricas(df)
    v = formatar(m)
    v["nome_repo"] = REPOSITORIO
    v["outliers"] = ", ".join(m["rq3"]["outliers"])
    v["codigo_tratar"] = html.escape(TRECHO_TRATAR)
    v["codigo_ytd"] = trecho(etl.acumulado_ate_mes)
    v["codigo_gini"] = trecho(etl.gini)

    # figuras estáticas (gravadas em docs/assets) e interativas (embutidas)
    ASSETS.mkdir(parents=True, exist_ok=True)
    analise.fig_letalidade_composicao(df, ASSETS / "fig1_letalidade_composicao.png")
    analise.fig_roubos_furtos_anual(df, ASSETS / "fig2_roubos_furtos_anual.png")
    analise.fig_sazonalidade_roubos(df, ASSETS / "fig3_sazonalidade_roubos.png")
    analise.fig_lorenz(df, ASSETS / "fig4_lorenz.png")
    analise.fig_boxplot_regioes(df, ASSETS / "fig5_boxplot_regioes.png")
    import matplotlib.pyplot as plt
    plt.close("all")
    from plotly.offline import get_plotlyjs
    (ASSETS / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")

    fonte = "Fonte: elaboração própria a partir de ISP-RJ (2026)."
    v["fig1"] = figura("fig1_letalidade_composicao.png", f"<strong>Figura 1.</strong> Letalidade violenta harmonizada, acumulado de janeiro a {v['mes_fim']}, e participação das mortes por intervenção de agente do Estado. {fonte}", "Barras empilhadas de CVLI e mortes por intervenção policial por ano, com linha do percentual de intervenção")
    v["fig2"] = figura("fig2_roubos_furtos_anual.png", f"<strong>Figura 3.</strong> Roubos e furtos (janeiro a {v['mes_fim']}) e participação dos furtos nos crimes patrimoniais. {fonte}", "Linhas de roubos e furtos por ano e barras da participação dos furtos")
    v["fig3"] = figura("fig3_sazonalidade_roubos.png", f"<strong>Figura 5.</strong> Mapa de calor dos roubos por mês e ano (milhares). Fevereiro de 2017 destoa dos meses vizinhos. {fonte}", "Mapa de calor de roubos por mês e ano")
    v["fig4"] = figura("fig4_lorenz.png", f"<strong>Figura 6.</strong> Curvas de Lorenz da distribuição de homicídios, roubos e furtos entre os 92 municípios. {fonte}", "Curvas de Lorenz de homicídios, roubos e furtos")
    v["fig5"] = figura("fig5_boxplot_regioes.png", f"<strong>Figura 9.</strong> Dispersão do volume mensal médio de registros por município, por região (escala logarítmica). {fonte}", "Boxplot do volume de registros por município em cada região")
    v["plot_letalidade"] = bloco_plotly(analise.plot_letalidade_mensal(df), "plot-letalidade", f"<strong>Figura 2.</strong> Versão interativa: CVLI e mortes por intervenção de agente do Estado por mês, com média móvel de 12 meses (passe o mouse para ver os valores; clique na legenda para ocultar séries). {fonte}")
    v["plot_rf"] = bloco_plotly(analise.plot_roubos_furtos_mensal(df), "plot-roubos-furtos", f"<strong>Figura 4.</strong> Versão interativa: roubos e furtos mensais no estado. A linha pontilhada marca março de 2020. {fonte}")
    v["plot_top"] = bloco_plotly(analise.plot_top_municipios(df), "plot-top-municipios", f"<strong>Figura 7.</strong> Os dez municípios com mais homicídios dolosos no período, coloridos pela região; o texto de apoio mostra a participação acumulada no ranking. {fonte}")
    v["plot_regional"] = bloco_plotly(analise.plot_perfil_regional(df), "plot-perfil-regional", f"<strong>Figura 8.</strong> Participação de cada região no total do estado, por tipo de ocorrência. {fonte}")

    v["resumo"] = RESUMO_PT
    v["abstract"] = ABSTRACT_EN
    v["css"] = CSS
    v["jsonld"] = json.dumps({
        "@context": "https://schema.org", "@type": "ScholarlyArticle",
        "name": "Estatísticas de segurança do estado do Rio de Janeiro (2014–2026)",
        "author": {"@type": "Person", "name": AUTOR, "affiliation": "UniLaSalle"},
        "inLanguage": "pt-BR", "license": "https://creativecommons.org/licenses/by/4.0/",
        "codeRepository": REPO_URL, "url": PAGES_URL,
        "isBasedOn": {"@type": "Dataset", "name": "ISPDados: série histórica mensal por município desde 2014", "url": FONTE_URL},
        "keywords": "segurança pública, Rio de Janeiro, letalidade violenta, crimes patrimoniais, FAIR",
    }, ensure_ascii=False)

    def preencher(texto: str) -> str:
        # repete até não haver mais marcadores (marcadores podem aparecer dentro de outros blocos)
        for _ in range(4):
            texto = re.sub(r"\[\[(\w+)\]\]", lambda mt: v.get(mt.group(1), mt.group(0)), texto)
        return texto

    v["corpo"] = preencher(CORPO)
    v["resumo"] = preencher(RESUMO_PT)
    v["abstract"] = preencher(ABSTRACT_EN)
    pagina = preencher(TEMPLATE)
    restantes = sorted(set(re.findall(r"\[\[(\w+)\]\]", pagina)))
    info = {"marcadores_sem_valor": restantes,
            "palavras_resumo": contar_palavras(v["resumo"]),
            "palavras_abstract": contar_palavras(v["abstract"])}
    return pagina, info


def main() -> int:
    df = etl.carregar_processado()
    pagina, info = montar(df)
    if info["marcadores_sem_valor"]:
        raise SystemExit(f"Marcadores sem valor: {info['marcadores_sem_valor']}")
    (DOCS / "index.html").write_text(pagina, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"docs/index.html gerado ({len(pagina) / 1024:.0f} KB) | resumo: {info['palavras_resumo']} palavras | "
          f"abstract: {info['palavras_abstract']} palavras")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
