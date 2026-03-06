import streamlit as st
import os

st.set_page_config(
    page_title="Banco Fictício — Análise Estratégica",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Pipeline Bancário e Storytelling com Dados")
st.markdown(
    """
### Bem-vindo ao painel de análise estratégica

Este projeto consiste em um ambiente analítico completo de uma instituição financeira fictícia. Os dados aqui gerados e analisados são sintéticos, porém construídos com base em **informações reais do Brasil**, refletindo a malha de municípios oficiais do IBGE e o histórico de indicadores macroeconômicos (taxa SELIC, IPCA e taxa de Desemprego).

A aplicação demonstra o ciclo de vida da informação combinando duas disciplinas essenciais:
- **Engenharia de Dados (Pipeline Medallion):** Estruturação do fluxo em camadas (Bronze → Silver → Gold) para saneamento e modelagem dimensional.
- **Visualização Executiva (Storytelling com Dados):** Aplicação de técnicas narrativas visuais para construção de painéis limpos, interativos e focados na tomada de decisão, baseadas nas diretrizes de Cole Nussbaumer Knaflic.

---

### Guia de Navegação
Utilize o menu lateral para explorar as etapas do projeto:

| Página | Descrição |
|---|---|
| **1. Geração de Dados** | Criação parametrizada da base de clientes, histórico de transações e coleta de dados macroeconômicos. |
| **2. Pipeline ETL** | Demonstração técnica da transformação e enriquecimento dos dados brutos até a tabela fato. |
| **3. KPIs com Storytelling** | Análises visuais orientadas à ação abordando Adoção Digital, Volume por Canal e Perfil de Risco. |
| **4. Correlação Macro** | Estudo comparativo do impacto da economia nacional no comportamento transacional bancário. |

> **Nota Operacional:** É estritamente necessário garantir a existência dos arquivos na página de "Geração de Dados" antes de prosseguir para as visualizações de ETL e KPIs.
"""
)

# Status dos dados na camada Bronze
col1, col2, col3 = st.columns(3)
with col1:
    existe = os.path.exists("data/d_customer.csv")
    st.metric("Base de Clientes", "Disponível" if existe else "Pendente")
with col2:
    existe = os.path.exists("data/f_transactions.csv")
    st.metric("Base de Transações", "Disponível" if existe else "Pendente")
with col3:
    existe = os.path.exists("data/d_macro_economic.csv")
    st.metric("Dados Macroeconômicos", "Disponível" if existe else "Pendente")
