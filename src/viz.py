import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ─── Identidade visual ───────────────────────────────
CORES = {
    "primaria": "#1F3A93",
    "destaque": "#E74C3C",
    "digital": "#2ECC71",
    "fisico": "#95A5A6",
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


def _apply_storytelling_layout(
    fig: go.Figure, titulo: str, subtitulo: str
) -> go.Figure:
    """Aplica o template de Storytelling (limpeza de eixos e título narrativo)."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br><span style='font-size:13px;color:#7F8C8D'>{subtitulo}</span>",
            font=dict(size=18, color=CORES["texto"]),
            x=0.01,
            y=0.95,
        ),
        plot_bgcolor=CORES["fundo"],
        paper_bgcolor=CORES["fundo"],
        font=dict(color=CORES["texto"]),
        margin=dict(t=90, l=20, r=20, b=40),
        showlegend=False,
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────
# VIZ 1 — ADOÇÃO DIGITAL
# ─────────────────────────────────────────────────────────
def plot_adocao_digital(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # Suavização da linha (substituindo scipy por rolling do pandas para evitar dependências extras)
    y_smooth = df["pct_digital"].rolling(window=6, min_periods=1).mean()

    # Linha principal (fundo neutro)
    fig.add_trace(
        go.Scatter(
            x=df["ano_mes"],
            y=df["pct_digital"],
            mode="lines",
            line=dict(color=CORES["fisico"], width=1.5),
            opacity=0.4,
            name="Realizado",
            hoverinfo="skip",
        )
    )

    # Tendência em destaque
    fig.add_trace(
        go.Scatter(
            x=df["ano_mes"],
            y=y_smooth,
            mode="lines",
            line=dict(color=CORES["digital"], width=3),
            name="Tendência",
            hovertemplate="<b>%{y:.1f}%</b> digitais<extra></extra>",
        )
    )

    # Anotação do evento PIX
    pix_label = "2020-11"
    if pix_label in df["ano_mes"].values:
        y_pix = y_smooth[df[df["ano_mes"] == pix_label].index[0]]
        fig.add_vline(
            x=pix_label, line_width=1.5, line_dash="dash", line_color=CORES["destaque"]
        )
        fig.add_annotation(
            x=pix_label,
            y=y_pix,
            text="Lançamento<br>do PIX",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=CORES["destaque"],
            ax=45,
            ay=-40,
            font=dict(color=CORES["destaque"], size=11, family="Arial"),
        )

    # Destaque no ponto final
    last_x, last_y = df["ano_mes"].iloc[-1], y_smooth.iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[last_x],
            y=[last_y],
            mode="markers+text",
            marker=dict(color=CORES["digital"], size=10),
            text=[f"<b>{last_y:.0f}%</b>"],
            textposition="top left",
            textfont=dict(color=CORES["digital"], size=14),
            hoverinfo="skip",
        )
    )

    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    return _apply_storytelling_layout(
        fig,
        "📱 A virada digital: de 5% para mais de 90% em 25 anos",
        "Percentual de transações realizadas por canais digitais | Mensal",
    )


# ─────────────────────────────────────────────────────────
# VIZ 2 — VOLUME POR CANAL
# ─────────────────────────────────────────────────────────
def plot_volume_canal(df: pd.DataFrame) -> go.Figure:
    canais = ["Agência", "Caixa Eletrônico", "Internet Banking", "Mobile App"]
    pivot = df.pivot_table(
        index="ano", columns="canal", values="volume_total", aggfunc="sum"
    ).fillna(0)
    pivot = pivot.reindex(columns=canais, fill_value=0)

    fig = go.Figure()
    for canal in canais:
        fig.add_trace(
            go.Bar(
                x=pivot.index,
                y=pivot[canal] / 1e6,
                name=canal,
                marker_color=CANAIS_CORES[canal],
                hovertemplate="Ano: %{x}<br>Volume: <b>R$ %{y:,.0f}M</b><extra></extra>",
            )
        )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
        ),
        hovermode="closest",
    )
    fig.update_xaxes(showgrid=False, type="category")
    fig.update_yaxes(showgrid=False, title="Volume (R$ Milhões)")

    fig = _apply_storytelling_layout(
        fig,
        "💰 O dinheiro migrou para o digital: crescimento 20x em transações mobile",
        "Volume financeiro total por canal de atendimento | Anual (em R$ Milhões)",
    )
    fig.update_layout(margin=dict(t=120))  # Espaço extra para a legenda
    return fig


# ─────────────────────────────────────────────────────────
# VIZ 3 — PERFIL DE RISCO
# ─────────────────────────────────────────────────────────
def plot_perfil_risco(df: pd.DataFrame) -> go.Figure:
    df_plot = df.sort_values("faixa_risco", ascending=True)

    cores_risco = {
        "Alto": CORES["destaque"],
        "Médio": "#F39C12",
        "Bom": "#3498DB",
        "Excelente": CORES["digital"],
    }
    colors = [cores_risco.get(r, CORES["primaria"]) for r in df_plot["faixa_risco"]]
    opacities = [1.0 if r == "Alto" else 0.6 for r in df_plot["faixa_risco"]]

    fig = go.Figure(
        go.Bar(
            x=df_plot["pct"],
            y=df_plot["faixa_risco"],
            orientation="h",
            marker=dict(color=colors, opacity=opacities),
            text=[
                f"<b>{pct}%</b> ({n:,} clientes)"
                for pct, n in zip(df_plot["pct"], df_plot["n_clientes"])
            ],
            textposition="outside",
            hovertemplate="Faixa: %{y}<br>Clientes: %{customdata:,} <br>Percentual: %{x}%<extra></extra>",
            customdata=df_plot["n_clientes"],
        )
    )

    alto = df_plot[df_plot["faixa_risco"] == "Alto"]
    if not alto.empty:
        fig.add_annotation(
            x=alto["pct"].values[0] + 5,
            y="Alto",
            text="⚠ Requer atenção<br>em política de crédito",
            showarrow=True,
            arrowhead=2,
            arrowcolor=CORES["destaque"],
            ax=60,
            ay=0,
            font=dict(color=CORES["destaque"], size=11),
        )

    fig.update_xaxes(
        showgrid=False, visible=False, range=[0, df_plot["pct"].max() + 25]
    )
    fig.update_yaxes(showgrid=False, tickfont=dict(size=14, color=CORES["texto"]))

    return _apply_storytelling_layout(
        fig,
        "🎯 Perfil de crédito da base: oportunidade e risco",
        "Distribuição dos clientes por faixa de score de crédito | Base total",
    )


# ─────────────────────────────────────────────────────────
# VIZ 4 — CORRELAÇÃO MACROECONÔMICA
# ─────────────────────────────────────────────────────────
def plot_correlacao_macro(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.5, 0.25, 0.25],
    )

    fig.add_trace(
        go.Scatter(
            x=df["ano_mes"],
            y=df["volume_total"] / 1e6,
            fill="tozeroy",
            fillcolor="rgba(31, 58, 147, 0.15)",
            line=dict(color=CORES["primaria"], width=2),
            name="Volume (R$ M)",
            hovertemplate="R$ %{y:,.0f}M<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["ano_mes"],
            y=df["selic"],
            fill="tozeroy",
            fillcolor="rgba(230, 126, 34, 0.15)",
            line=dict(color="#E67E22", width=2),
            name="SELIC (%)",
            hovertemplate="%{y:.1f}%<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["ano_mes"],
            y=df["desemprego"],
            fill="tozeroy",
            fillcolor="rgba(231, 76, 60, 0.15)",
            line=dict(color=CORES["destaque"], width=2),
            name="Desemprego (%)",
            hovertemplate="%{y:.1f}%<extra></extra>",
        ),
        row=3,
        col=1,
    )

    fig.update_yaxes(title_text="Volume (R$ M)", row=1, col=1, showgrid=False)
    fig.update_yaxes(
        title_text="SELIC (%)",
        row=2,
        col=1,
        showgrid=False,
        title_font=dict(color="#E67E22"),
        tickfont=dict(color="#E67E22"),
    )
    fig.update_yaxes(
        title_text="Desempr. (%)",
        row=3,
        col=1,
        showgrid=False,
        title_font=dict(color=CORES["destaque"]),
        tickfont=dict(color=CORES["destaque"]),
    )
    fig.update_xaxes(showgrid=False)

    fig = _apply_storytelling_layout(
        fig,
        "📊 Macro vs. Comportamento Bancário",
        "Volume total transacionado, Taxa SELIC e Taxa de Desemprego | Mensal",
    )
    fig.update_layout(height=700, hovermode="x unified")
    return fig
