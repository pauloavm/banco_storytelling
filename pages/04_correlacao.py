import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Correlação Macro", page_icon="📈", layout="wide")
st.title("📈 KPI 4 — Correlação com Indicadores Macroeconômicos")
st.markdown(
    """
Como SELIC e desemprego influenciaram o comportamento transacional dos clientes ao longo de 25 anos?

> **Técnica aplicada:** Subplots com eixo X compartilhado (evita o eixo Y duplo — 
> recomendação de Cole Knaflic no Capítulo 2 de *Storytelling com Dados*).
"""
)


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

from src.etl import kpi_correlacao_macro
from src.viz import plot_correlacao_macro

df_macro = kpi_correlacao_macro(gold)

# ── Métricas de correlação ───────────────────────
col1, col2, col3 = st.columns(3)
corr_selic = df
