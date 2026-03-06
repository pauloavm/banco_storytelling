"""
01_geracao.py
-------------
Página 1: Visão geral dos dados gerados (camada Bronze).
Mostra estatísticas descritivas e distribuições dos dados sintéticos.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.etl import bronze_customers, bronze_transactions, bronze_macro
from src.viz import CORES

st.set_page_config(page_title="Geração de Dados", page_icon="📊", layout="wide")

st.title("📊 Geração de Dados — Camada Bronze")
st.markdown(
    """
Os dados brutos são gerados por scripts Python usando **Faker** (dados de clientes)
e **bcb** (dados macroeconômicos reais do Banco Central).
"""
)
st.markdown("---")


# ── Carrega dados ──────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    df_cust = bronze_customers()
    df_tx = bronze_transactions()

    # Converte para preview
    df_tx["data_transacao"] = pd.to_datetime(df_tx["data_transacao"], errors="coerce")
    df_tx["valor"] = pd.to_numeric(df_tx["valor"], errors="coerce")


# ── Métricas de topo ───────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

m1.metric("👥 Total de Clientes", f"{len(df_cust):,}")
m2.metric("💳 Total de Transações", f"{len(df_tx):,}")
m3.metric("📅 Período Simulado", "2000 – 2025")
m4.metric("💰 Volume Total (R$)", f"R$ {df_tx['valor'].sum() / 1e9:.1f}B")

st.markdown("---")


# ── Tabs de exploração ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["👥 Clientes", "💳 Transações", "📋 Schemas"])

with tab1:
    st.subheader("Amostra — d_customer.csv (Bronze)")
    st.dataframe(df_cust.head(20), use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Distribuição por Estado**")
        estado_counts = df_cust["estado"].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.barh(
            estado_counts.index,
            estado_counts.values,
            color=CORES["primaria"],
            edgecolor="none",
        )
        ax.set_title(
            "Top 10 Estados — Base de Clientes",
            fontsize=11,
            fontweight="bold",
            loc="left",
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown("**Distribuição por Faixa de Renda**")
        renda_counts = df_cust["faixa_renda"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(
            renda_counts.index,
            renda_counts.values,
            color=[
                CORES["primaria"] if i == 0 else CORES["neutro"]
                for i in range(len(renda_counts))
            ],
            edgecolor="none",
        )
        ax.set_title(
            "Clientes por Faixa de Renda", fontsize=11, fontweight="bold", loc="left"
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.xticks(rotation=20, ha="right", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

with tab2:
    st.subheader("Amostra — f_transactions.csv (Bronze)")
    st.dataframe(df_tx.head(20), use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Transações por Canal**")
        canal_counts = df_tx["canal"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(
            canal_counts.index,
            canal_counts.values,
            color=[
                CORES["primaria"] if i == 0 else CORES["neutro"]
                for i in range(len(canal_counts))
            ],
            edgecolor="none",
        )
        ax.set_title(
            "Volume de Transações por Canal", fontsize=11, fontweight="bold", loc="left"
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown("**Distribuição de Valores (R$)**")
        fig, ax = plt.subplots(figsize=(6, 4))
        valores_filtrados = df_tx["valor"].dropna()
        valores_filtrados = valores_filtrados[
            valores_filtrados < valores_filtrados.quantile(0.99)
        ]
        ax.hist(
            valores_filtrados,
            bins=60,
            color=CORES["primaria"],
            edgecolor="none",
            alpha=0.8,
        )
        ax.set_title(
            "Distribuição dos Valores Transacionados",
            fontsize=11,
            fontweight="bold",
            loc="left",
        )
        ax.set_xlabel("Valor (R$)", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

with tab3:
    st.subheader("Schemas dos Datasets")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("**d_customer.csv**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Campo": df_cust.columns,
                    "Tipo": df_cust.dtypes.astype(str).values,
                    "Exemplo": [str(df_cust[c].iloc[0]) for c in df_cust.columns],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    with col_s2:
        st.markdown("**f_transactions.csv**")
        st.dataframe(
            pd.DataFrame(
                {
                    "Campo": df_tx.columns,
                    "Tipo": df_tx.dtypes.astype(str).values,
                    "Exemplo": [str(df_tx[c].iloc[0]) for c in df_tx.columns],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
