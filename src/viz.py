import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ─── Identidade visual ───────────────────────────────
CORES = {
    "primaria": "#1F3A93",  # azul institucional
    "destaque": "#E74C3C",  # vermelho para alertas
    "digital": "#2ECC71",  # verde para digital
    "fisico": "#95A5A6",  # cinza para físico
    "neutro": "#ECF0F1",
    "texto": "#2C3E50",
    "fundo": "#FFFFFF",
}

CANAIS_CORES = {
    "Agência": "#95A5A6",
    "Caixa Eletrônico": "#7F8C8D",
    "Internet Banking": "#3498DB",
    "Mobile App": "#2ECC71",
}


def _limpar_eixos(ax, manter_x: bool = True, manter_y: bool = False):
    """Remove ruído visual — técnica central do storytelling."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if not manter_y:
        ax.spines["left"].set_visible(False)
        ax.yaxis.set_visible(False)
    if not manter_x:
        ax.spines["bottom"].set_visible(False)


def _titulo_subtitulo(ax, titulo: str, subtitulo: str):
    """Título narrativo + subtítulo explicativo — padrão do storytelling."""
    ax.set_title(
        titulo, fontsize=14, fontweight="bold", color=CORES["texto"], pad=20, loc="left"
    )
    ax.text(
        0,
        1.03,
        subtitulo,
        transform=ax.transAxes,
        fontsize=9,
        color="#7F8C8D",
        ha="left",
    )


def _rodape(fig, fonte: str = "Fonte: Simulação sintética — Banco Fictício Brasileiro"):
    fig.text(0.01, -0.01, fonte, fontsize=7, color="#95A5A6", ha="left")


# ─────────────────────────────────────────────────────────
# VIZ 1 — ADOÇÃO DIGITAL
# ─────────────────────────────────────────────────────────
def plot_adocao_digital(df: pd.DataFrame) -> plt.Figure:
    """
    Evolução da adoção digital ao longo do tempo.
    Aplica técnicas do storytelling: anotação de evento (PIX 2020),
    destaque no ponto máximo, linha vertical de evento, título narrativo.
    """
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=CORES["fundo"])
    ax.set_facecolor(CORES["fundo"])

    x = np.arange(len(df))
    y = df["pct_digital"].values

    # Linha principal — cinza neutro (versão simples)
    ax.plot(x, y, color=CORES["fisico"], linewidth=1.5, alpha=0.4, zorder=1)

    # TÉCNICA STORYTELLING: destacar tendência com linha suavizada
    from scipy.ndimage import uniform_filter1d

    y_smooth = uniform_filter1d(y, size=6)
    ax.plot(x, y_smooth, color=CORES["digital"], linewidth=2.5, zorder=2)

    # TÉCNICA: Linha vertical para marcar evento (PIX)
    pix_label = "2020-11"
    if pix_label in df["ano_mes"].values:
        idx_pix = df[df["ano_mes"] == pix_label].index[0]
        idx_pix_x = (
            df.index.get_loc(idx_pix)
            if hasattr(df.index, "get_loc")
            else df.reset_index().index[df.reset_index()["ano_mes"] == pix_label][0]
        )
        ax.axvline(
            x=idx_pix_x,
            color=CORES["destaque"],
            linestyle="--",
            linewidth=1.2,
            alpha=0.8,
        )
        ax.annotate(
            "Lançamento\ndo PIX",
            xy=(idx_pix_x, y_smooth[idx_pix_x]),
            xytext=(idx_pix_x + 3, y_smooth[idx_pix_x] + 8),
            fontsize=8,
            color=CORES["destaque"],
            arrowprops=dict(arrowstyle="->", color=CORES["destaque"], lw=1.2),
        )

    # TÉCNICA: destacar ponto final (último mês)
    ax.scatter([x[-1]], [y_smooth[-1]], color=CORES["digital"], s=60, zorder=5)
    ax.annotate(
        f"{y_smooth[-1]:.0f}%",
        xy=(x[-1], y_smooth[-1]),
        xytext=(x[-1] - 8, y_smooth[-1] + 5),
        fontsize=9,
        color=CORES["digital"],
        fontweight="bold",
    )

    # Eixo X — mostrar apenas alguns anos
    anos_exibir = df[df["ano_mes"].str.endswith("-01")]["ano_mes"].values
    idx_exibir = [
        df.reset_index(drop=True)
        .index[df.reset_index(drop=True)["ano_mes"] == a]
        .tolist()
        for a in anos_exibir
    ]
    idx_flat = [i[0] for i in idx_exibir if i]
    labels_flat = [a[:4] for a in anos_exibir]
    ax.set_xticks(idx_flat)
    ax.set_xticklabels(labels_flat, fontsize=8, color=CORES["texto"])

    _limpar_eixos(ax, manter_x=True, manter_y=False)
    _titulo_subtitulo(
        ax,
        "📱 A virada digital: de 5% para mais de 90% em 25 anos",
        "Percentual de transações realizadas por canais digitais (Internet Banking + Mobile App) | Mensal",
    )
    _rodape(fig)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────
# VIZ 2 — VOLUME POR CANAL (barras empilhadas com storytelling)
# ─────────────────────────────────────────────────────────
def plot_volume_canal(df: pd.DataFrame) -> plt.Figure:
    """
    Volume financeiro por canal ao longo dos anos.
    Barras empilhadas com identidade visual por canal.
    """
    fig, ax = plt.subplots(figsize=(13, 5), facecolor=CORES["fundo"])
    ax.set_facecolor(CORES["fundo"])

    canais = ["Agência", "Caixa Eletrônico", "Internet Banking", "Mobile App"]
    pivot = df.pivot_table(
        index="ano", columns="canal", values="volume_total", aggfunc="sum"
    ).fillna(0)
    pivot = pivot.reindex(columns=canais, fill_value=0)

    anos = pivot.index.values
    x = np.arange(len(anos))
    bottom = np.zeros(len(anos))

    bars_refs = {}
    for canal in canais:
        vals = pivot[canal].values / 1e6  # em Milhões
        bars = ax.bar(
            x,
            vals,
            bottom=bottom,
            color=CANAIS_CORES[canal],
            label=canal,
            width=0.7,
            alpha=0.92,
        )
        bars_refs[canal] = bars
        bottom += vals

    # TÉCNICA STORYTELLING: rótulo somente no topo da barra total
    for i, total in enumerate(bottom):
        if total > 0:
            ax.text(
                i,
                total + 5,
                f"R${total:.0f}M",
                ha="center",
                va="bottom",
                fontsize=6.5,
                color=CORES["texto"],
            )

    ax.set_xticks(x)
    ax.set_xticklabels(anos, rotation=45, fontsize=7.5)
    ax.legend(loc="upper left", fontsize=8, frameon=False)

    _limpar_eixos(ax, manter_x=True, manter_y=True)
    ax.spines["left"].set_visible(True)
    ax.yaxis.set_visible(True)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:.0f}M"))
    ax.set_ylabel("Volume (R$ Milhões)", fontsize=9, color=CORES["texto"])

    _titulo_subtitulo(
        ax,
        "💰 O dinheiro migrou para o digital: crescimento 20x em transações mobile",
        "Volume financeiro total por canal de atendimento | Anual (em R$ Milhões)",
    )
    _rodape(fig)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────
# VIZ 3 — PERFIL DE RISCO (barras horizontais)
# ─────────────────────────────────────────────────────────
def plot_perfil_risco(df: pd.DataFrame) -> plt.Figure:
    """
    Distribuição de clientes por faixa de risco.
    Barras horizontais — recomendação de Cole Knaflic para dados categóricos.
    Destaque na categoria de maior atenção (Alto Risco).
    """
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=CORES["fundo"])
    ax.set_facecolor(CORES["fundo"])

    cores_risco = {
        "Alto": CORES["destaque"],
        "Médio": "#F39C12",
        "Bom": "#3498DB",
        "Excelente": CORES["digital"],
    }

    # Ordem de baixo para cima no gráfico horizontal
    df_plot = df.sort_values("faixa_risco", ascending=True)
    y = np.arange(len(df_plot))

    for i, row in enumerate(df_plot.itertuples()):
        cor = cores_risco.get(row.faixa_risco, CORES["primaria"])
        alpha = 1.0 if row.faixa_risco == "Alto" else 0.55

        bar = ax.barh(y[i], row.pct, color=cor, alpha=alpha, height=0.55)

        # TÉCNICA: rótulo dentro da barra
        ax.text(
            row.pct + 0.5,
            y[i],
            f"{row.pct}% ({row.n_clientes:,} clientes)",
            va="center",
            fontsize=9,
            color=CORES["texto"],
        )

    ax.set_yticks(y)
    ax.set_yticklabels(df_plot["faixa_risco"].values, fontsize=10)
    ax.set_xlim(0, df_plot["pct"].max() + 18)

    # TÉCNICA STORYTELLING: anotação de alerta
    alto = df_plot[df_plot["faixa_risco"] == "Alto"]
    if not alto.empty:
        ax.annotate(
            "⚠ Requer atenção\nem política de crédito",
            xy=(alto["pct"].values[0], 0),
            xytext=(alto["pct"].values[0] + 8, 0.3),
            fontsize=8,
            color=CORES["destaque"],
            arrowprops=dict(arrowstyle="->", color=CORES["destaque"]),
        )

    _limpar_eixos(ax, manter_x=False, manter_y=True)
    _titulo_subtitulo(
        ax,
        "🎯 Perfil de crédito da base: oportunidade e risco em equilíbrio",
        "Distribuição dos clientes por faixa de score de crédito | Base total",
    )
    _rodape(fig)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────
# VIZ 4 — CORRELAÇÃO MACROECONÔMICA (dois eixos narrativos)
# ─────────────────────────────────────────────────────────
def plot_correlacao_macro(df: pd.DataFrame) -> plt.Figure:
    """
    Volume transacionado vs. SELIC e Desemprego.
    Gráficos separados verticalmente (padrão recomendado vs. eixo y secundário).
    Técnica: Evita eixo y duplo — usa subplots com eixo x compartilhado.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(
        3,
        1,
        figsize=(13, 9),
        sharex=True,
        facecolor=CORES["fundo"],
        gridspec_kw={"height_ratios": [3, 2, 2]},
    )
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor(CORES["fundo"])

    x = np.arange(len(df))

    # ── Painel 1: Volume ──
    ax1.fill_between(x, df["volume_total"] / 1e6, alpha=0.25, color=CORES["primaria"])
    ax1.plot(x, df["volume_total"] / 1e6, color=CORES["primaria"], linewidth=1.8)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"R${v:.0f}M"))
    ax1.set_ylabel("Volume (R$ M)", fontsize=8, color=CORES["texto"])
    _limpar_eixos(ax1, manter_x=False, manter_y=True)
    ax1.set_title(
        "📊 Macro vs. Comportamento Bancário: a SELIC e o desemprego moldaram o uso do banco",
        fontsize=13,
        fontweight="bold",
        color=CORES["texto"],
        pad=15,
        loc="left",
    )
    ax1.text(
        0,
        1.02,
        "Volume total transacionado, Taxa SELIC e Taxa de Desemprego | Mensal",
        transform=ax1.transAxes,
        fontsize=8,
        color="#7F8C8D",
    )

    # ── Painel 2: SELIC ──
    ax2.plot(x, df["selic"], color="#E67E22", linewidth=1.5)
    ax2.fill_between(x, df["selic"], alpha=0.15, color="#E67E22")
    ax2.set_ylabel("SELIC (%)", fontsize=8, color="#E67E22")
    ax2.yaxis.label.set_color("#E67E22")
    ax2.tick_params(axis="y", colors="#E67E22")
    _limpar_eixos(ax2, manter_x=False, manter_y=True)

    # ── Painel 3: Desemprego ──
    ax3.plot(x, df["desemprego"], color=CORES["destaque"], linewidth=1.5)
    ax3.fill_between(x, df["desemprego"], alpha=0.15, color=CORES["destaque"])
    ax3.set_ylabel("Desemprego (%)", fontsize=8, color=CORES["destaque"])
    ax3.yaxis.label.set_color(CORES["destaque"])
    ax3.tick_params(axis="y", colors=CORES["destaque"])
    _limpar_eixos(ax3, manter_x=True, manter_y=True)

    # Eixo X compartilhado
    anos_mostrar = df[df["ano_mes"].str.endswith("-01")]["ano_mes"].values
    idx_exibir = [
        df.reset_index(drop=True)
        .index[df.reset_index(drop=True)["ano_mes"] == a]
        .tolist()
        for a in anos_mostrar
    ]
    idx_flat = [i[0] for i in idx_exibir if i]
    labels_flat = [a[:4] for a in anos_mostrar]
    ax3.set_xticks(idx_flat)
    ax3.set_xticklabels(labels_flat, fontsize=8, rotation=45)

    _rodape(fig)
    plt.tight_layout(h_pad=0.5)
    return fig
