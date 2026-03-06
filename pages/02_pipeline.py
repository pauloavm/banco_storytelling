"""
02_pipeline.py
--------------
Página 2: Visualização do pipeline ETL (Bronze → Silver → Gold).
Demonstra as transformações aplicadas em cada camada.
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.etl import (
    bronze_customers,
    bronze_transactions,
    silver_customers,
    silver_transactions,
    gold_fact_transactions,
)

st.set_page_config(page_title="Pipeline ETL", page_icon="🔄", layout="wide")

st.title("🔄 Pipeline ETL — Arquitetura Medallion")
st.markdown(
    """
Visualize a progressão dos dados desde a camada **Bronze** (dados brutos)
até a **Gold** (dados prontos para análise), simulando o mesmo pipeline
implementado originalmente em **Databricks/Spark**.
"""
)
st.markdown("---")

# ── Diagrama do pipeline ───────────────────────────────────────────────────
st.markdown(
    """
┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ BRONZE │────▶│ SILVER │────▶│ GOLD │ │ │ │ │ │ │ │ CSV brutos │ │ Tipos OK │ │ Tabela Fato │ │ dtype=str │ │ Chaves OK │ │ (Joins completos) │ │ sem limpeza │ │ Nulos trat. │ │ Pronta para KPIs │ └─────────────┘ └─────────────┘ └─────────────────────┘
            
            """
)

# ── Tabs por camada ────────────────────────────────────────────────────────
tab_b, tab_s, tab_g = st.tabs(["🟤 Bronze", "⚪ Silver", "🟡 Gold"])

with tab_b:
    st.subheader("🟤 Camada Bronze — Dados Brutos")
    st.info(
        "Dados lidos diretamente dos CSVs, sem qualquer transformação. "
        "Todos os campos são strings."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**bronze_customers**")
        df = bronze_customers()
        st.dataframe(df.head(5), use_container_width=True)
        st.caption(f"Shape: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    with col2:
        st.markdown("**bronze_transactions**")
        df = bronze_transactions()
        st.dataframe(df.head(5), use_container_width=True)
        st.caption(f"Shape: {df.shape[0]:,} linhas × {df.shape[1]} colunas")

with tab_s:
    st.subheader("⚪ Camada Silver — Dados Limpos")
    st.success(
        "Tipos corrigidos, chaves criadas (`anomes_id`), "
        "flag digital adicionada, faixa de risco calculada."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**silver_customers** — novos campos")
        df = silver_customers()
        st.dataframe(df.head(5), use_container_width=True)

        st.markdown("**Transformações aplicadas:**")
        st.markdown(
            """
        - `data_abertura` → `datetime64`
        - `score_credito` → `int64`
        - ➕ `faixa_risco` → derivada do score
        """
        )

    with col2:
        st.markdown("**silver_transactions** — novos campos")
        df = silver_transactions()
        st.dataframe(df.head(5), use_container_width=True)

        st.markdown("**Transformações aplicadas:**")
        st.markdown(
            """
        - `data_transacao` → `datetime64`
        - `valor` → `float64`
        - ➕ `anomes_id` → chave de join com macro
        - ➕ `is_digital` → flag canal digital (0/1)
        - ➕ `ano`, `mes` → granularidade temporal
        """
        )

with tab_g:
    st.subheader("🟡 Camada Gold — Tabela Fato Principal")
    st.success(
        "Tabela `gold_f_transactions`: todos os joins realizados. "
        "Cada linha é uma transação enriquecida com dados de cliente e macroeconômicos."
    )

    with st.spinner("Construindo camada Gold (join completo)..."):
        df_gold = gold_fact_transactions()

    st.dataframe(df_gold.head(10), use_container_width=True)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("📏 Total de Linhas", f"{len(df_gold):,}")
    col_m2.metric("📐 Total de Colunas", f"{df_gold.shape[1]}")
    col_m3.metric(
        "💾 Tamanho (memória)", f"{df_gold.memory_usage(deep=True).sum() / 1e6:.1f} MB"
    )

    st.markdown("**Campos disponíveis na Gold:**")
    col_info = pd.DataFrame(
        {
            "Campo": df_gold.columns,
            "Tipo": df_gold.dtypes.astype(str).values,
            "Nulos": df_gold.isnull().sum().values,
            "Únicos": df_gold.nunique().values,
        }
    )
    st.dataframe(col_info, use_container_width=True, hide_index=True)
