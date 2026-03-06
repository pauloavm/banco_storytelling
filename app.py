"""
app.py
------
Entry point da aplicação Streamlit.
Define a navegação entre páginas e carrega o estado global da sessão.
"""

import streamlit as st

# ── Configuração da página ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Banco Storytelling | Dashboard Analítico",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Esconde o menu padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer     {visibility: hidden;}

        /* Card de métrica customizado */
        div[data-testid="metric-container"] {
            background-color : #F0F4FF;
            border           : 1px solid #D0DEFF;
            border-radius    : 8px;
            padding          : 16px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1A1A2E;
        }
        [data-testid="stSidebar"] * {
            color: #E0E0E0 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# ── Sidebar de navegação ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Banco Storytelling")
    st.markdown("---")
    st.markdown(
        """
    **Pipeline de Dados Bancários**
    aplicando princípios de
    *Storytelling com Dados*

    ---
    📂 **Páginas**
    - 📊 Geração de Dados
    - 🔄 Pipeline ETL
    - 📈 KPIs Analíticos
    - 🔗 Correlação Macro
    ---
    """
    )

    st.caption("Dados sintéticos — uso educacional")
    st.caption("Referência: *Storytelling com Dados*\nCole Nussbaumer Knaflic")


# ── Página inicial (home) ──────────────────────────────────────────────────
st.title("🏦 Banco Storytelling — Pipeline Analítico")
st.markdown(
    """
Este projeto demonstra um pipeline completo de engenharia e análise de dados
para um banco brasileiro fictício, aplicando os **princípios de Storytelling com Dados**.

---
"""
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
    ### 📊 O Que Este Projeto Faz
    - Gera dados sintéticos de **15.000 clientes** e suas transações
    - Simula **25 anos** de comportamento bancário (2000–2025)
    - Implementa arquitetura **Bronze → Silver → Gold** em Pandas
    """
    )

with col2:
    st.markdown(
        """
    ### 🎯 KPIs Analisados
    - **Adoção Digital** ao longo do tempo
    - **Volume por Canal** (Agência, ATM, Internet, PIX)
    - **Perfil de Risco** da carteira
    - **Correlação** com SELIC e Desemprego
    """
    )

with col3:
    st.markdown(
        """
    ### 📖 Filosofia Visual
    Cada gráfico segue as lições de **Cole Nussbaumer Knaflic**:
    - Título narrativo (história, não rótulo)
    - Cor como ferramenta de foco
    - Remoção de elementos desnecessários
    - Anotações em pontos críticos
    """
    )

st.info("👈 **Use o menu lateral** para navegar entre as seções do pipeline.", icon="ℹ️")
