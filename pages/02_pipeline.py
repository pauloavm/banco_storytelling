import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pipeline ETL", page_icon="🔄", layout="wide")
st.title("🔄 Pipeline ETL — Arquitetura Medallion")
st.markdown("Visualize a transformação dos dados brutos **(Bronze → Silver → Gold)**.")

if not all(
    os.path.exists(p)
    for p in [
        "data/d_customer.csv",
        "data/f_transactions.csv",
        "data/d_macro_economic.csv",
    ]
):
    st.error(
        "❌ Dados não encontrados. Execute a página **1. Geração de Dados** primeiro."
    )
    st.stop()

from src.etl import (
    bronze_to_silver_customers,
    bronze_to_silver_transactions,
    bronze_to_silver_macro,
    build_dim_date,
    build_gold_transactions,
)


# ── Carrega Bronze ───────────────────────────────
@st.cache_data
def carregar_bronze():
    return (
        pd.read_csv("data/d_customer.csv"),
        pd.read_csv("data/f_transactions.csv"),
        pd.read_csv("data/d_macro_economic.csv"),
    )


bronze_c, bronze_tx, bronze_m = carregar_bronze()

# ── Diagrama textual do pipeline ─────────────────
st.markdown(
    """
📂 BRONZE (Dados Brutos) ├── d_customer.csv → bronze_customer ├── f_transactions.csv → bronze_transactions └── d_macro_economic.csv → bronze_macro_economic ↓ [Limpeza de tipos, validação, chaves] 🥈 SILVER (Dados Limpos) ├── silver_customers ├── silver_transactions └── silver_macro_economic ↓ [Joins, enriquecimento, modelagem estrela] 🏆 GOLD (Pronto para Análise) ├── d_date (dimensão) └── gold_f_transactions (tabela fato)
            
"""
)
# ── Transforma e exibe ───────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥈 Silver — Clientes")
    silver_c = bronze_to_silver_customers(bronze_c)
    st.dataframe(silver_c.head(5), use_container_width=True)
    st.caption(
        f"Tipos corrigidos. {len(silver_c):,} registros. "
        f"Data mín: {silver_c['data_abertura_conta'].min().date()}"
    )

    st.subheader("🥈 Silver — Transações")
    silver_tx = bronze_to_silver_transactions(bronze_tx)
    st.dataframe(silver_tx.head(5), use_container_width=True)
    st.caption(f"{len(silver_tx):,} transações. Chave anomes_id criada.")

with col2:
    st.subheader("🥈 Silver — Macroeconômico")
    silver_m = bronze_to_silver_macro(bronze_m)
    st.dataframe(silver_m.head(5), use_container_width=True)
    st.caption(f"{len(silver_m):,} meses. SELIC, IPCA, Desemprego tipados.")

    st.subheader("📅 Gold — Dimensão de Datas")
    dim_date = build_dim_date()
    st.dataframe(dim_date.head(5), use_container_width=True)
    st.caption(f"{len(dim_date):,} datas de 2000 a 2025.")

# ── Gold final ───────────────────────────────────
st.divider()
st.subheader("🏆 Gold — Tabela Fato: gold_f_transactions")

with st.spinner("Construindo tabela Gold..."):
    gold = build_gold_transactions(silver_tx, silver_c, silver_m)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(gold):,}")
col2.metric("Colunas", f"{gold.shape[1]}")
col3.metric("Volume total", f"R$ {gold['valor'].sum()/1e9:.2f}B")
col4.metric("Clientes únicos", f"{gold['customer_id'].nunique():,}")

st.dataframe(gold.head(10), use_container_width=True)

# Salvar em cache de sessão para outras páginas
st.session_state["gold"] = gold
st.success("✅ Tabela Gold pronta! Navegue para os KPIs.")
