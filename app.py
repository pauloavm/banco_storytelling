import streamlit as st

st.set_page_config(
    page_title="Banco Fictício — Análise Estratégica",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Pipeline Bancário com Storytelling")
st.markdown(
    """
### Bem-vindo ao painel de análise estratégica

Este projeto combina duas abordagens:
- **Pipeline ETL Medallion** (Bronze → Silver → Gold) — inspirado no projeto [pauloavm/Bancario](https://github.com/pauloavm/Bancario)
- **Storytelling com Dados** — técnicas de visualização executiva inspiradas em [BrunoMeloSlv/storytelling_with_data](https://github.com/BrunoMeloSlv/storytelling_with_data) e no livro de Cole Nussbaumer Knaflic

---

### 📌 Como usar
Use o menu lateral para navegar pelas etapas:

| Página | O que faz |
|---|---|
| **1. Geração de Dados** | Cria a base sintética de clientes, transações e dados macro |
| **2. Pipeline ETL** | Mostra a transformação Bronze → Silver → Gold |
| **3. KPIs com Storytelling** | Análises visuais orientadas à decisão |
| **4. Correlação Macro** | Impacto de SELIC e desemprego no comportamento bancário |

> ⚠️ **Comece pela página 1** para gerar os dados antes de navegar para as análises.
"""
)

# Status dos dados
import os

col1, col2, col3 = st.columns(3)
with col1:
    existe = os.path.exists("data/d_customer.csv")
    st.metric("Clientes", "✅ Gerado" if existe else "❌ Pendente")
with col2:
    existe = os.path.exists("data/f_transactions.csv")
    st.metric("Transações", "✅ Gerado" if existe else "❌ Pendente")
with col3:
    existe = os.path.exists("data/d_macro_economic.csv")
    st.metric("Dados Macro", "✅ Gerado" if existe else "❌ Pendente")
