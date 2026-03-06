import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Correlação Macroeconômica", layout="wide")
st.title("Estudo de Correlação: Contexto Macroeconômico vs. Movimentação Bancária")
st.markdown(
    """
Análise comparativa da influência de indicadores externos (SELIC e Desemprego) no comportamento transacional da base de clientes ao longo do tempo.

> **Fundamentação Visual:** A utilização de subplots com eixo X compartilhado elimina a ambiguidade visual característica de gráficos com múltiplos eixos Y, alinhando-se às boas práticas de visualização executiva.
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
    st.error("Falha de Dependência: Execute a geração de dados na página principal.")
    st.stop()

from src.etl import kpi_correlacao_macro
from src.viz import plot_correlacao_macro

df_macro = kpi_correlacao_macro(gold)

# ── Métricas de correlação ───────────────────────
st.subheader("Análise do Coeficiente de Pearson (r)")

with st.expander("Interpretação Estatística dos Coeficientes"):
    st.markdown(
        """
        O Coeficiente de Correlação de Pearson mensura o grau da correlação linear entre duas variáveis, variando de -1 (correlação negativa perfeita) a 1 (correlação positiva perfeita).
        
        **Insights Econômicos Observáveis:**
        - **Correlação Volume vs. SELIC:** Um índice fortemente negativo sugeriria que o aumento dos juros reduz a tomada de crédito e esfria a movimentação financeira no varejo. Já um índice positivo ou próximo de zero indica que a base transacional é resiliente ou guiada por fatores independentes da taxa básica de juros.
        - **Correlação Volume vs. Desemprego:** Em cenários macroeconômicos normais, espera-se uma correlação negativa acentuada; o desemprego contrai a renda disponível, o que reduz substancialmente o consumo e, consequentemente, o volume financeiro transacionado pelas contas correntes.
        """
    )

col1, col2 = st.columns(2)

corr_selic = df_macro["volume_total"].corr(df_macro["selic"])
corr_desemprego = df_macro["volume_total"].corr(df_macro["desemprego"])

col1.metric("Coeficiente de Correlação: Volume x SELIC", f"{corr_selic:.2f}")
col2.metric("Coeficiente de Correlação: Volume x Desemprego", f"{corr_desemprego:.2f}")

st.divider()

# ── Renderização do Gráfico ──────────────────────
fig4 = plot_correlacao_macro(df_macro)
st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
