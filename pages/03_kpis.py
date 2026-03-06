"""
03_kpis.py
----------
Página 3: KPIs analíticos com visualizações narrativas (Storytelling).
"""

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.etl import (
    kpi_adocao_digital,
    kpi_volume_canal,
    kpi_perfil_risco,
    gold_fact_transactions,
)
from src.viz import plot_adocao_digital, plot_volume_canal, plot_perfil_risco

st.set_page_config(page_title="KPIs Analíticos", page_icon="📈", layout="wide")

st.title("📈 KPIs Analíticos — Storytelling com Dados")
st.markdown(
    """
Cada visualização segue os princípios de **Cole Nussbaumer Knaflic**:
título narrativo, cor como foco, e anotações em pontos críticos.
"""
)
st.markdown("---")

# ── KPI 1: Adoção Digital ──────────────────────────────────────────────────
st.subheader("KPI 1 — Adoção Digital ao Longo do Tempo")

with st.spinner("Calculando adoção digital..."):
    df_adocao = kpi_adocao_digital()

fig1 = plot_adocao_digital(df_adocao)
st.pyplot(fig1)

import matplotlib.pyplot as plt

plt.close()

# Métricas de apoio
m1, m2, m3 = st.columns(3)
ultimo = df_adocao.iloc[-1]
primeiro = df_adocao.iloc[0]
m1.metric(
    "% Digital Atual",
    f"{ultimo['pct_digital']:.1f}%",
    f"+{ultimo['pct_digital'] - primeiro['pct_digital']:.1f}pp desde 2000",
)
m2.metric("Meses com > 50% Digital", f"{(df_adocao['pct_digital'] > 50).sum():,}")
m3.metric("Total de Transações Analisadas", f"{df_adocao['total_tx'].sum():,}")

st.markdown("---")


# ── KPI 2: Volume por Canal ────────────────────────────────────────────────
st.subheader("KPI 2 — Volume Financeiro por Canal")

with st.spinner("Calculando volume por canal..."):
    df_canal = kpi_volume_canal()

# Filtro interativo por ano
anos_disponiveis = sorted(df_canal["ano"].unique())
col_filtro, _ = st.columns([1, 3])
ano_sel = col_filtro.selectbox(
    "Selecionar ano:", options=["Todos"] + list(anos_disponiveis), index=0
)

fig2 = plot_volume_canal(df_canal, ano_sel if ano_sel != "Todos" else None)
st.pyplot(fig2)
plt.close()

st.markdown("---")


# ── KPI 3: Perfil de Risco ─────────────────────────────────────────────────
st.subheader("KPI 3 — Perfil de Risco da Carteira")

with st.spinner("Calculando perfil de risco..."):
    df_risco = kpi_perfil_risco()

col_graf, col_tabela = st.columns([3, 1])

with col_graf:
    fig3 = plot_perfil_risco(df_risco)
    st.pyplot(fig3)
    plt.close()

with col_tabela:
    st.markdown("**Detalhe por Faixa**")
    df_risco_display = df_risco.copy()
    df_risco_display["% Carteira"] = (
        df_risco_display["qtd_clientes"] / df_risco_display["qtd_clientes"].sum() * 100
    ).round(1).astype(str) + "%"
    df_risco_display.columns = ["Faixa", "Clientes", "% Carteira"]
    st.dataframe(df_risco_display, use_container_width=True, hide_index=True)
