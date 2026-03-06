import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Geração de Dados", layout="wide")
st.title("Geração de Dados Sintéticos")
st.markdown(
    "Criação da camada **Bronze** — dados brutos simulados com base em demografia e economia real."
)

# Detecta se está rodando localmente (Windows = 'nt') ou na Nuvem (Linux = 'posix')
IS_LOCAL = os.name == "nt"

if IS_LOCAL:
    # ── Parâmetros Locais ──────────────────────────────────
    with st.expander("Parâmetros de Geração (Ambiente Local)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            n_clientes = st.slider(
                "Número de clientes na amostra", 1_000, 15_000, 5_000, 1_000
            )
            st.caption(
                "Nota: Amostras maiores aumentam a precisão estatística, mas exigem maior capacidade de processamento."
            )
        with col2:
            forcar_regenerar = st.checkbox(
                "Forçar regeneração (ignorar cache)", value=False
            )

    # ── Botão de geração ─────────────────────────────
    if st.button("Executar Geração de Dados", type="primary", use_container_width=True):
        from src.gerador import gerar_clientes, coletar_macro, gerar_transacoes

        # Clientes
        if not os.path.exists("data/d_customer.csv") or forcar_regenerar:
            with st.spinner("Processando base de clientes..."):
                df_clientes = gerar_clientes(n=n_clientes)
            st.success(f"Operação concluída: {len(df_clientes):,} clientes gerados.")
        else:
            df_clientes = pd.read_csv("data/d_customer.csv")
            st.info(
                f"Base de clientes carregada do cache ({len(df_clientes):,} registros)."
            )

        # Macro
        if not os.path.exists("data/d_macro_economic.csv") or forcar_regenerar:
            with st.spinner("Sincronizando dados macroeconômicos..."):
                df_macro = coletar_macro()
            st.success(
                f"Operação concluída: {len(df_macro):,} meses de dados macroeconômicos armazenados."
            )
        else:
            df_macro = pd.read_csv("data/d_macro_economic.csv")
            st.info(
                f"Dados macroeconômicos carregados do cache ({len(df_macro):,} meses)."
            )

        # Transações
        if not os.path.exists("data/f_transactions.csv") or forcar_regenerar:
            with st.spinner(
                f"Processando histórico transacional para {len(df_clientes):,} clientes..."
            ):
                df_tx = gerar_transacoes(df_clientes)
            st.success(
                f"Operação concluída: {len(df_tx):,} transações financeiras geradas."
            )
        else:
            df_tx = pd.read_csv("data/f_transactions.csv")
            st.info(
                f"Base de transações carregada do cache ({len(df_tx):,} registros)."
            )

else:
    # ── Ambiente em Nuvem ─────────────────────────────
    st.info(
        "Ambiente em Nuvem Detectado: A rotina de geração de dados dinâmicos está "
        "desabilitada para preservar os limites de memória do servidor. O painel utilizará "
        "exclusivamente os dados estáticos pré-gerados."
    )

# ── Preview dos dados ────────────────────────────
st.divider()
st.subheader("Visualização Prévia: Dados Brutos (Camada Bronze)")

tab1, tab2, tab3 = st.tabs(
    ["Base de Clientes", "Base de Transações", "Indicadores Macro"]
)

with tab1:
    if os.path.exists("data/d_customer.csv"):
        df = pd.read_csv("data/d_customer.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volume Total de Clientes", f"{len(df):,}")
        col2.metric("Score de Crédito (Média)", f"{df['score_de_credito'].mean():.0f}")
        col3.metric("Idade Demográfica (Média)", f"{df['idade'].mean():.1f} anos")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning(
            "Dados não localizados. Execute a rotina de geração ou verifique o repositório."
        )

with tab2:
    if os.path.exists("data/f_transactions.csv"):
        df = pd.read_csv("data/f_transactions.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Volume de Transações", f"{len(df):,}")
        col2.metric("Ticket Médio", f"R$ {df['valor'].mean():,.2f}")
        col3.metric("Volume Financeiro Total", f"R$ {df['valor'].sum()/1e9:.2f}B")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dados não localizados.")

with tab3:
    if os.path.exists("data/d_macro_economic.csv"):
        df = pd.read_csv("data/d_macro_economic.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Taxa SELIC (Média Histórica)", f"{df['selic'].mean():.1f}%")
        col2.metric("IPCA (Média Histórica)", f"{df['ipca'].mean():.1f}%")
        col3.metric("Desemprego (Média Histórica)", f"{df['desemprego'].mean():.1f}%")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("Dados não localizados.")
