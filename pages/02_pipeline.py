import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Pipeline ETL", layout="wide")
st.title("Pipeline ETL — Arquitetura Medallion")
st.markdown(
    "Visualização da esteira de processamento e transformação de dados em três estágios lógicos."
)

if not all(
    os.path.exists(p)
    for p in [
        "data/d_customer.csv",
        "data/f_transactions.csv",
        "data/d_macro_economic.csv",
    ]
):
    st.error(
        "Falha de Dependência: Bases de dados não localizadas. Execute a rotina na página '1. Geração de Dados'."
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
st.markdown("**Diagrama de Arquitetura de Dados**")
st.code(
    """
[BRONZE] Repositório Bruto (Histórico imutável)
├── d_customer.csv         
├── f_transactions.csv     
└── d_macro_economic.csv   
            ↓
    [Sanitização, Tipagem e Correção de Anomalias]
            ↓
[SILVER] Repositório Padronizado (Single Source of Truth)
├── silver_customers
├── silver_transactions
└── silver_macro_economic
            ↓
    [Modelagem Dimensional, Cruzamentos e Regras de Negócio]
            ↓
[GOLD] Repositório Analítico (Focado em Consumo)
├── d_date                 (Tabela de Dimensão Temporal)
└── gold_f_transactions    (Tabela Fato Consolidada)
    """,
    language="text",
)

# ── Transforma e exibe ───────────────────────────
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Camada Silver: Clientes")
    silver_c = bronze_to_silver_customers(bronze_c)
    st.dataframe(silver_c.head(5), use_container_width=True)
    st.caption(
        f"Diagnóstico: Conversão de tipos de dados concluída. {len(silver_c):,} registros preservados. "
    )

    st.subheader("Camada Silver: Transações")
    silver_tx = bronze_to_silver_transactions(bronze_tx)
    st.dataframe(silver_tx.head(5), use_container_width=True)
    st.caption(
        f"Diagnóstico: Geração de chave temporal (anomes_id) finalizada. {len(silver_tx):,} eventos válidos."
    )

with col2:
    st.subheader("Camada Silver: Dados Macroeconômicos")
    silver_m = bronze_to_silver_macro(bronze_m)
    st.dataframe(silver_m.head(5), use_container_width=True)
    st.caption(
        f"Diagnóstico: Padronização numérica finalizada. {len(silver_m):,} competências mensais indexadas."
    )

    st.subheader("Camada Gold: Dimensão de Datas")
    dim_date = build_dim_date()
    st.dataframe(dim_date.head(5), use_container_width=True)
    st.caption(
        f"Diagnóstico: Criação de granularidade temporal diária finalizada ({len(dim_date):,} registros)."
    )

# ── Gold final ───────────────────────────────────
st.divider()
st.subheader("Camada Gold: Tabela Fato Transacional")

with st.spinner("Compilando modelagem analítica..."):
    gold = build_gold_transactions(silver_tx, silver_c, silver_m)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Linhas Geradas", f"{len(gold):,}")
col2.metric("Features (Colunas)", f"{gold.shape[1]}")
col3.metric("Volume Transacionado", f"R$ {gold['valor'].sum()/1e9:.2f}B")
col4.metric("Entidades Únicas (Clientes)", f"{gold['customer_id'].nunique():,}")

st.dataframe(gold.head(10), use_container_width=True)
st.session_state["gold"] = gold
st.success(
    "Tabela analítica processada com sucesso e liberada para consumo nas visualizações de negócio."
)
