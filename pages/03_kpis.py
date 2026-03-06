import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="KPIs com Storytelling", page_icon="📊", layout="wide")
st.title("📊 KPIs com Storytelling")
st.markdown("Cada visualização conta uma história orientada à tomada de decisão.")


# ── Carrega Gold ─────────────────────────────────
@st.cache_data
def carregar_gold():
    if not all(
        os.path.exists(p)
        for p in [
            "data/d_customer.csv",
            "data/f_transactions.csv",
            "data/d_macro_economic.csv",
        ]
    ):
        return None
    from src.etl import (
        bronze_to_silver_customers,
        bronze_to_silver_transactions,
        bronze_to_silver_macro,
        build_gold_transactions,
    )

    bronze_c = pd.read_csv("data/d_customer.csv")
    bronze_tx = pd.read_csv("data/f_transactions.csv")
    bronze_m = pd.read_csv("data/d_macro_economic.csv")
    sc = bronze_to_silver_customers(bronze_c)
    stx = bronze_to_silver_transactions(bronze_tx)
    sm = bronze_to_silver_macro(bronze_m)
    return build_gold_transactions(stx, sc, sm)


gold = carregar_gold()
if gold is None:
    st.error("❌ Execute a **Geração de Dados** primeiro.")
    st.stop()

from src.etl import kpi_adocao_digital, kpi_volume_por_canal, kpi_perfil_risco
from src.viz import plot_adocao_digital, plot_volume_canal, plot_perfil_risco

# ──────────────────────────────────────────────────
# KPI 1 — Adoção Digital
# ──────────────────────────────────────────────────
st.subheader("📱 KPI 1 — Adoção Digital ao Longo do Tempo")

with st.expander("ℹ️ Sobre este KPI"):
    st.markdown(
        """
    **O que mede:** Percentual de transações realizadas por canais digitais 
    (Internet Banking + Mobile App) em relação ao total, mês a mês.

    **Por que importa:** Indica a maturidade digital da base e guia investimentos 
    em infraestrutura de TI e canais físicos.

    **Técnicas de storytelling aplicadas:**
    - Linha suavizada para revelar tendência real (sem ruído)
    - Linha vertical marcando o lançamento do PIX (evento disruptivo)
    - Anotação do ponto final com o valor atual
    - Título narrativo com insight direto
    """
    )

df_digital = kpi_adocao_digital(gold)
col1, col2, col3 = st.columns(3)
col1.metric("% Digital hoje", f"{df_digital['pct_digital'].iloc[-1]:.1f}%")
col2.metric("% Digital em 2000", f"{df_digital['pct_digital'].iloc[0]:.1f}%")
delta = df_digital["pct_digital"].iloc[-1] - df_digital["pct_digital"].iloc[0]
col3.metric("Crescimento", f"+{delta:.1f} p.p.", delta_color="normal")

fig1 = plot_adocao_digital(df_digital)
st.pyplot(fig1, use_container_width=True)

# ──────────────────────────────────────────────────
# KPI 2 — Volume por Canal
# ──────────────────────────────────────────────────
st.divider()
st.subheader("💰 KPI 2 — Volume Financeiro por Canal")

with st.expander("ℹ️ Sobre este KPI"):
    st.markdown(
        """
    **O que mede:** Volume financeiro total (R$) e número de transações 
    por canal, agrupados por ano.

    **Por que importa:** Subsidia decisões sobre fechamento de agências, 
    alocação de ATMs e expansão de infraestrutura digital.

    **Técnicas de storytelling aplicadas:**
    - Barras empilhadas com paleta consistente por canal
    - Rótulo de total apenas no topo (evita poluição visual)
    - Identidade de cor clara: verde = digital, cinza = físico
    """
    )

df_canal = kpi_volume_por_canal(gold)

# Tabela resumo
col1, col2 = st.columns([2, 1])
with col1:
    fig2 = plot_volume_canal(df_canal)
    st.pyplot(fig2, use_container_width=True)
with col2:
    st.markdown("**Volume por Canal (Total Geral)**")
    resumo = (
        df_canal.groupby("canal")
        .agg(Volume=("volume_total", "sum"), Transações=("n_transacoes", "sum"))
        .reset_index()
    )
    resumo["Volume"] = resumo["Volume"].apply(lambda v: f"R$ {v/1e9:.2f}B")
    resumo["Transações"] = resumo["Transações"].apply(lambda v: f"{v:,}")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────
# KPI 3 — Perfil de Risco
# ──────────────────────────────────────────────────
st.divider()
st.subheader("🎯 KPI 3 — Análise do Perfil de Risco dos Clientes")

with st.expander("ℹ️ Sobre este KPI"):
    st.markdown(
        """
    **O que mede:** Distribuição da base de clientes por faixa de score de crédito.

    **Segmentação:**
    | Score | Faixa |
    |---|---|
    | 800–1000 | Excelente |
    | 650–799  | Bom       |
    | 500–649  | Médio     |
    | 300–499  | Alto Risco|

    **Técnicas de storytelling aplicadas:**
    - Barras horizontais (Cole Knaflic: melhor para dados categóricos com rótulos longos)
    - Destaque visual na categoria de alerta (vermelho, opacidade total)
    - Anotação direta na barra mais crítica
    """
    )

df_risco = kpi_perfil_risco(gold)
col1, col2 = st.columns([3, 2])
with col1:
    fig3 = plot_perfil_risco(df_risco)
    st.pyplot(fig3, use_container_width=True)
with col2:
    st.markdown("**Distribuição Detalhada**")
    st.dataframe(
        df_risco[["faixa_risco", "n_clientes", "pct"]].rename(
            columns={"faixa_risco": "Faixa", "n_clientes": "Clientes", "pct": "%"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    alto = df_risco[df_risco["faixa_risco"] == "Alto"]
    if not alto.empty:
        st.warning(
            f"⚠️ {alto['pct'].values[0]}% da base está em **Alto Risco** — "
            f"equivale a {alto['n_clientes'].values[0]:,} clientes."
        )
