"""
viz.py
------
Funções de visualização seguindo os princípios de Storytelling com Dados
(Cole Nussbaumer Knaflic / BrunoMeloSlv).

Filosofia aplicada em CADA gráfico:
  ✅ Título narrativo (o quê está acontecendo)
  ✅ Subtítulo de contexto (por quê importa)
  ✅ Cor como foco (cinza = ruído | cor vibrante = sinal)
  ✅ Anotações em pontos críticos (eventos reais: PIX, crises)
  ✅ Remoção de spines desnecessários (menos é mais)
  ✅ Rodapé com fonte de dados
"""

import matplotlib

matplotlib.use("Agg")  # ← Necessário no Streamlit para evitar thread error
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np


# ── Identidade Visual ──────────────────────────────────────────────────────
CORES = {
    "primaria": "#1A6FBF",  # azul bancário
    "destaque": "#E63946",  # vermelho — evento crítico
    "positivo": "#2DC653",  # verde — resultado positivo
    "neutro": "#AAAAAA",  # cinza — séries secundárias
    "fundo": "#F8F9FA",
    "texto": "#1C1C1E",
    "linha_ref": "#FFA500",  # laranja — linha de referência
}

FONTE = "DejaVu Sans"  # Fonte padrão do Matplotlib (sem dependência externa)

# Estilo global
plt.rcParams.update(
    {
        "font.family": FONTE,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": CORES["fundo"],
        "axes.facecolor": CORES["fundo"],
        "text.color": CORES["texto"],
        "axes.labelcolor": CORES["texto"],
        "xtick.color": CORES["texto"],
        "ytick.color": CORES["texto"],
    }
)


def _rodape(
    ax, fonte: str = "Dados sintéticos gerados via Faker | Banco Central do Brasil"
):
    """Adiciona rodapé padronizado com fonte dos dados."""
    ax.figure.text(
        0.01, 0.01, f"Fonte: {fonte}", fontsize=7, color=CORES["neutro"], style="italic"
    )


def _linha_evento(ax, x_val, label: str, cor: str = None):
    """Marca evento relevante com linha vertical anotada."""
    cor = cor or CORES["destaque"]
    ax.axvline(x=x_val, color=cor, linestyle="--", linewidth=1.2, alpha=0.7)
    ax.annotate(
        label,
        xy=(x_val, ax.get_ylim()[1] * 0.92),
        fontsize=8,
        color=cor,
        rotation=90,
        va="top",
        ha="right",
    )


# ══════════════════════════════════════════════════════════════════════════
# KPI 1 — Adoção Digital
# ══════════════════════════════════════════════════════════════════════════


def plot_adocao_digital(df: pd.DataFrame) -> plt.Figure:
    """
    Gráfico de linha: % de transações digitais ao longo do tempo.

    Storytelling:
    - Linha cinza: série histórica completa
    - Destaque verde: últimos 12 meses
    - Linha vermelha: chegada do PIX (nov/2020)
    - Anotação: valor atual (último ponto)
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    # ── Série completa (cinza = contexto) ─────────────────────────────────
    ax.plot(
        df["periodo"],
        df["pct_digital"],
        color=CORES["neutro"],
        linewidth=1.5,
        alpha=0.6,
        zorder=1,
    )

    # ── Últimos 24 meses em destaque ──────────────────────────────────────
    df_recente = df.tail(24)
    ax.plot(
        df_recente["periodo"],
        df_recente["pct_digital"],
        color=CORES["primaria"],
        linewidth=2.5,
        zorder=2,
    )

    # ── Scatter no último ponto ───────────────────────────────────────────
    ultimo = df.iloc[-1]
    ax.scatter(
        ultimo["periodo"],
        ultimo["pct_digital"],
        color=CORES["primaria"],
        s=80,
        zorder=5,
    )
    ax.annotate(
        f"{ultimo['pct_digital']:.1f}%",
        xy=(ultimo["periodo"], ultimo["pct_digital"]),
        xytext=(10, 5),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        color=CORES["primaria"],
    )

    # ── Evento: PIX ───────────────────────────────────────────────────────
    data_pix = pd.Timestamp("2020-11-01")
    _linha_evento(ax, data_pix, "Lançamento\ndo PIX", CORES["destaque"])

    # ── Evento: Pandemia ──────────────────────────────────────────────────
    data_pandemia = pd.Timestamp("2020-03-01")
    _linha_evento(ax, data_pandemia, "COVID-19", CORES["linha_ref"])

    # ── Títulos narrativos ────────────────────────────────────────────────
    ax.set_title(
        "A digitalização bancária acelerou após o PIX",
        fontsize=14,
        fontweight="bold",
        pad=15,
        loc="left",
    )
    ax.text(
        0,
        1.02,
        "% de transações realizadas por canais digitais (Internet Banking, Mobile App, PIX) — 2000 a 2025",
        transform=ax.transAxes,
        fontsize=9,
        color=CORES["neutro"],
    )

    ax.set_ylabel("% Transações Digitais", fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    _rodape(ax)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    return fig


# ══════════════════════════════════════════════════════════════════════════
# KPI 2 — Volume por Canal
# ══════════════════════════════════════════════════════════════════════════


def plot_volume_canal(df: pd.DataFrame, ano_selecionado: int = None) -> plt.Figure:
    """
    Gráfico de barras horizontais: volume financeiro por canal.

    Storytelling:
    - Canal com maior volume em destaque (azul)
    - Demais em cinza
    - Rótulo de valor ao final de cada barra
    """
    if ano_selecionado:
        df = df[df["ano"] == ano_selecionado]

    df_agg = (
        df.groupby("canal")["volume_total"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    max_canal = df_agg["volume_total"].idxmax()
    cores_barras = [
        CORES["primaria"] if i == max_canal else CORES["neutro"] for i in df_agg.index
    ]

    bars = ax.barh(
        df_agg["canal"],
        df_agg["volume_total"],
        color=cores_barras,
        edgecolor="none",
        height=0.6,
    )

    # ── Rótulos de valor ─────────────────────────────────────────────────
    for bar, val in zip(bars, df_agg["volume_total"]):
        ax.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"R$ {val/1e9:.1f}B",
            va="center",
            fontsize=9,
            color=CORES["texto"],
        )

    titulo_ano = f" — {ano_selecionado}" if ano_selecionado else " (acumulado)"
    ax.set_title(
        f"PIX e Mobile concentram o maior volume financeiro{titulo_ano}",
        fontsize=13,
        fontweight="bold",
        pad=12,
        loc="left",
    )
    ax.text(
        0,
        1.02,
        "Volume financeiro total transacionado por canal (R$ bilhões)",
        transform=ax.transAxes,
        fontsize=9,
        color=CORES["neutro"],
    )

    ax.spines["bottom"].set_visible(False)
    ax.xaxis.set_visible(False)

    _rodape(ax)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    return fig


# ══════════════════════════════════════════════════════════════════════════
# KPI 3 — Perfil de Risco
# ══════════════════════════════════════════════════════════════════════════


def plot_perfil_risco(df: pd.DataFrame) -> plt.Figure:
    """
    Gráfico de barras verticais: distribuição de clientes por faixa de risco.

    Storytelling:
    - 'Excelente' e 'Bom' em verde/azul (positivo)
    - 'Alto Risco' em vermelho (alerta)
    - Rótulo de % sobre cada barra
    """
    ORDEM = ["Alto Risco", "Risco Médio", "Bom", "Excelente"]
    COR_MAP = {
        "Alto Risco": CORES["destaque"],
        "Risco Médio": CORES["linha_ref"],
        "Bom": CORES["neutro"],
        "Excelente": CORES["positivo"],
    }

    df["faixa_risco"] = pd.Categorical(
        df["faixa_risco"], categories=ORDEM, ordered=True
    )
    df = df.sort_values("faixa_risco")
    df["pct"] = df["qtd_clientes"] / df["qtd_clientes"].sum() * 100

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        df["faixa_risco"].astype(str),
        df["qtd_clientes"],
        color=[COR_MAP.get(str(c), CORES["neutro"]) for c in df["faixa_risco"]],
        edgecolor="none",
        width=0.6,
    )

    for bar, pct in zip(bars, df["pct"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 50,
            f"{pct:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color=CORES["texto"],
        )

    ax.set_title(
        "Mais de 60% da carteira tem perfil Bom ou Excelente",
        fontsize=13,
        fontweight="bold",
        pad=12,
        loc="left",
    )
    ax.text(
        0,
        1.02,
        "Distribuição de clientes por faixa de score de crédito",
        transform=ax.transAxes,
        fontsize=9,
        color=CORES["neutro"],
    )

    ax.set_ylabel("Número de Clientes", fontsize=9)
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    _rodape(ax)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    return fig


# ══════════════════════════════════════════════════════════════════════════
# KPI 4 — Correlação Macro
# ══════════════════════════════════════════════════════════════════════════


def plot_correlacao_macro(df: pd.DataFrame) -> plt.Figure:
    """
    Gráfico dual-axis: volume transacionado vs SELIC e Desemprego.

    Storytelling:
    - Eixo Y esquerdo: volume (azul)
    - Eixo Y direito: SELIC (laranja) e Desemprego (vermelho tracejado)
    - Destaque visual no período de alta SELIC (2015-2016 e 2022-2023)
    """
    df = df.dropna(subset=["selic", "desemprego"])

    fig, ax1 = plt.subplots(figsize=(13, 5))
    ax2 = ax1.twinx()

    # ── Volume total ──────────────────────────────────────────────────────
    ax1.fill_between(
        df["periodo"], df["volume_total"], alpha=0.25, color=CORES["primaria"]
    )
    ax1.plot(
        df["periodo"],
        df["volume_total"],
        color=CORES["primaria"],
        linewidth=2,
        label="Volume Transacionado (R$)",
    )

    # ── SELIC ─────────────────────────────────────────────────────────────
    ax2.plot(
        df["periodo"],
        df["selic"],
        color=CORES["linha_ref"],
        linewidth=1.5,
        linestyle="-",
        label="SELIC (%)",
        alpha=0.8,
    )

    # ── Desemprego ────────────────────────────────────────────────────────
    ax2.plot(
        df["periodo"],
        df["desemprego"],
        color=CORES["destaque"],
        linewidth=1.5,
        linestyle="--",
        label="Desemprego (%)",
        alpha=0.8,
    )

    # ── Períodos de destaque ──────────────────────────────────────────────
    ax1.axvspan(
        pd.Timestamp("2015-01-01"),
        pd.Timestamp("2017-01-01"),
        alpha=0.07,
        color=CORES["destaque"],
        label="Crise 2015-2016",
    )
    ax1.axvspan(
        pd.Timestamp("2022-01-01"),
        pd.Timestamp("2023-12-01"),
        alpha=0.07,
        color=CORES["linha_ref"],
        label="Aperto monetário 2022",
    )

    # ── Títulos e legendas ────────────────────────────────────────────────
    ax1.set_title(
        "SELIC elevada e desemprego alto coincidem com\nreduções no volume transacionado",
        fontsize=13,
        fontweight="bold",
        pad=12,
        loc="left",
    )
    ax1.text(
        0,
        1.02,
        "Volume mensal transacionado (R$) vs SELIC (%) e Taxa de Desemprego (%) — 2000 a 2025",
        transform=ax1.transAxes,
        fontsize=9,
        color=CORES["neutro"],
    )

    ax1.set_ylabel("Volume Transacionado (R$)", color=CORES["primaria"], fontsize=9)
    ax2.set_ylabel("Taxa (%)", color=CORES["texto"], fontsize=9)

    # Legenda unificada
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper left",
        fontsize=8,
        framealpha=0.5,
    )

    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    _rodape(ax1)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    return fig
