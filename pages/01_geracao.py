import streamlit as st
import os

st.set_page_config(page_title="Geração de Dados", page_icon="⚙️", layout="wide")
st.title("⚙️ Geração de Dados Sintéticos")
st.markdown("Cria a camada **Bronze** — dados brutos simulados.")

# ── Parâmetros ──────────────────────────────────
with st.expander("⚙️ Parâmetros de Geração", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        n_clientes = st.slider("Número de clientes", 1_000, 15_000, 5_000, 1_000)
        st.caption(
            "⚡ Mais clientes = mais tempo de geração. 5.000 é um bom equilíbrio."
        )
    with col2:
        forcar_regenerar = st.checkbox(
            "Forçar regeneração (ignorar cache)", value=False
        )

# ── Botão de geração ─────────────────────────────
if st.button("🚀 Gerar Dados", type="primary", use_container_width=True):
    from src.gerador import gerar_clientes, coletar_macro, gerar_transacoes

    # Clientes
    if not os.path.exists("data/d_customer.csv") or forcar_regenerar:
        with st.spinner("Gerando clientes..."):
            df_clientes = gerar_clientes(n=n_clientes)
        st.success(f"✅ {len(df_clientes):,} clientes gerados.")
    else:
        import pandas as pd

        df_clientes = pd.read_csv("data/d_customer.csv")
        st.info(
            f"ℹ️ Clientes já existentes carregados ({len(df_clientes):,} registros)."
        )

    # Macro
    if not os.path.exists("data/d_macro_economic.csv") or forcar_regenerar:
        with st.spinner("Coletando dados macroeconômicos..."):
            df_macro = coletar_macro()
        st.success(f"✅ {len(df_macro):,} meses de dados macro.")
    else:
        import pandas as pd

        df_macro = pd.read_csv("data/d_macro_economic.csv")
        st.info(f"ℹ️ Dados macro já existentes ({len(df_macro):,} meses).")

    # Transações
    if not os.path.exists("data/f_transactions.csv") or forcar_regenerar:
        with st.spinner(
            f"Gerando transações para {len(df_clientes):,} clientes... (pode levar alguns minutos)"
        ):
            df_tx = gerar_transacoes(df_clientes)
        st.success(f"✅ {len(df_tx):,} transações geradas.")
    else:
        import pandas as pd

        df_tx = pd.read_csv("data/f_transactions.csv")
        st.info(f"ℹ️ Transações já existentes ({len(df_tx):,} registros).")

    st.balloons()

# ── Preview dos dados ────────────────────────────
st.divider()
st.subheader("👁️ Preview dos Dados Brutos (Bronze)")

import pandas as pd

tab1, tab2, tab3 = st.tabs(["👤 Clientes", "💳 Transações", "📈 Macro"])

with tab1:
    if os.path.exists("data/d_customer.csv"):
        df = pd.read_csv("data/d_customer.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de clientes", f"{len(df):,}")
        col2.metric("Score médio", f"{df['score_de_credito'].mean():.0f}")
        col3.metric("Idade média", f"{df['idade'].mean():.1f} anos")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dados ainda não gerados. Clique em 'Gerar Dados'.")

with tab2:
    if os.path.exists("data/f_transactions.csv"):
        df = pd.read_csv("data/f_transactions.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de transações", f"{len(df):,}")
        col2.metric("Valor médio", f"R$ {df['valor'].mean():,.2f}")
        col3.metric("Volume total", f"R$ {df['valor'].sum()/1e9:.2f}B")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dados ainda não gerados.")

with tab3:
    if os.path.exists("data/d_macro_economic.csv"):
        df = pd.read_csv("data/d_macro_economic.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("SELIC média", f"{df['selic'].mean():.1f}%")
        col2.metric("IPCA médio", f"{df['ipca'].mean():.1f}%")
        col3.metric("Desemprego médio", f"{df['desemprego'].mean():.1f}%")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dados ainda não gerados.")
