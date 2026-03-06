"""
etl.py
------
Implementa o pipeline ETL em Pandas simulando a arquitetura Medallion.

Bronze  → dados brutos (CSV lidos sem transformação)
Silver  → tipos corrigidos, chaves criadas, nulos tratados
Gold    → tabela fato unificada, pronta para análise

Nota: Aqui NÃO usamos Databricks/Spark — a lógica é idêntica,
      mas executada em Pandas para rodar no Streamlit Cloud.
      O design respeita a mesma nomenclatura e lógica do projeto original.
"""

import pandas as pd
import numpy as np
import streamlit as st


# ── Caminhos padrão dos arquivos ───────────────────────────────────────────
PATH_CUSTOMERS = "data/d_customer.csv"
PATH_TRANSACTIONS = "data/f_transactions.csv"
PATH_MACRO = "data/d_macro_economic.csv"


# ══════════════════════════════════════════════════════════════════════════
# CAMADA BRONZE — Leitura bruta dos CSVs
# ══════════════════════════════════════════════════════════════════════════


@st.cache_data(show_spinner=False)
def bronze_customers() -> pd.DataFrame:
    """Lê clientes sem qualquer transformação (camada Bronze)."""
    return pd.read_csv(PATH_CUSTOMERS, dtype=str)


@st.cache_data(show_spinner=False)
def bronze_transactions() -> pd.DataFrame:
    """Lê transações sem qualquer transformação (camada Bronze)."""
    return pd.read_csv(PATH_TRANSACTIONS, dtype=str)


@st.cache_data(show_spinner=False)
def bronze_macro() -> pd.DataFrame:
    """Lê dados macroeconômicos sem transformação (camada Bronze)."""
    return pd.read_csv(PATH_MACRO, dtype=str)


# ══════════════════════════════════════════════════════════════════════════
# CAMADA SILVER — Tipagem, limpeza e chaves
# ══════════════════════════════════════════════════════════════════════════


@st.cache_data(show_spinner=False)
def silver_customers() -> pd.DataFrame:
    """
    Aplica transformações Silver em clientes:
    - Converte datas para datetime
    - Garante tipos numéricos corretos
    - Remove duplicatas e nulos críticos
    """
    df = bronze_customers()

    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], errors="coerce")
    df["data_abertura"] = pd.to_datetime(df["data_abertura"], errors="coerce")
    df["score_credito"] = pd.to_numeric(df["score_credito"], errors="coerce")

    # Faixa de risco baseada no score (replica lógica do KPI 3 original)
    df["faixa_risco"] = pd.cut(
        df["score_credito"],
        bins=[0, 500, 650, 800, 1001],
        labels=["Alto Risco", "Risco Médio", "Bom", "Excelente"],
        right=False,
    )

    # Remove nulos em campos obrigatórios
    df = df.dropna(subset=["customer_id", "data_abertura", "score_credito"])

    return df.drop_duplicates(subset=["customer_id"])


@st.cache_data(show_spinner=False)
def silver_transactions() -> pd.DataFrame:
    """
    Aplica transformações Silver em transações:
    - Converte data para datetime
    - Converte valor para float
    - Cria chave anomes_id para join com macro
    - Adiciona flag de canal digital
    """
    df = bronze_transactions()

    df["data_transacao"] = pd.to_datetime(df["data_transacao"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Chave de join com dados macroeconômicos (AAAAMM)
    df["anomes_id"] = df["data_transacao"].dt.to_period("M").astype(str)

    # Flag de canal digital (KPI 1)
    CANAIS_DIGITAIS = {"Internet Banking", "Mobile App", "PIX"}
    df["is_digital"] = df["canal"].isin(CANAIS_DIGITAIS).astype(int)

    # Extrai componentes temporais para análises
    df["ano"] = df["data_transacao"].dt.year
    df["mes"] = df["data_transacao"].dt.month

    return df.dropna(
        subset=["transaction_id", "customer_id", "data_transacao", "valor"]
    )


@st.cache_data(show_spinner=False)
def silver_macro() -> pd.DataFrame:
    """
    Aplica transformações Silver nos dados macroeconômicos:
    - Converte data para datetime
    - Cria chave anomes_id para join
    - Garante tipos numéricos nas taxas
    """
    df = bronze_macro()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # Chave de join (mesma do silver_transactions)
    df["anomes_id"] = df["data"].dt.to_period("M").astype(str)

    # Converte indicadores para numérico
    indicadores = ["selic", "ipca", "desemprego", "pib"]
    for col in indicadores:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["anomes_id"])


# ══════════════════════════════════════════════════════════════════════════
# CAMADA GOLD — Tabela fato unificada
# ══════════════════════════════════════════════════════════════════════════


@st.cache_data(show_spinner=False)
def gold_fact_transactions() -> pd.DataFrame:
    """
    Constrói a gold_f_transactions: tabela fato principal.

    Joins realizados:
    - silver_transactions + silver_customers  (LEFT JOIN por customer_id)
    - resultado + silver_macro               (LEFT JOIN por anomes_id)

    Esta tabela é o coração de todas as análises de KPI.
    """
    tx = silver_transactions()
    cust = silver_customers()[
        [
            "customer_id",
            "estado",
            "faixa_renda",
            "score_credito",
            "faixa_risco",
            "data_abertura",
        ]
    ]
    macro = silver_macro()

    # Join 1: transações + clientes
    gold = tx.merge(cust, on="customer_id", how="left", suffixes=("", "_cust"))

    # Join 2: resultado + macro
    gold = gold.merge(macro, on="anomes_id", how="left")

    return gold


# ══════════════════════════════════════════════════════════════════════════
# AGREGAÇÕES PRÉ-CALCULADAS (performance no Streamlit)
# ══════════════════════════════════════════════════════════════════════════


@st.cache_data(show_spinner=False)
def kpi_adocao_digital() -> pd.DataFrame:
    """
    KPI 1: % de transações digitais por mês (2000-2025).
    Retorna série temporal pronta para plotagem.
    """
    df = gold_fact_transactions()
    mensal = (
        df.groupby("anomes_id")
        .agg(
            total_tx=("transaction_id", "count"),
            tx_digitais=("is_digital", "sum"),
        )
        .reset_index()
    )

    mensal["pct_digital"] = mensal["tx_digitais"] / mensal["total_tx"] * 100
    mensal["periodo"] = pd.to_datetime(mensal["anomes_id"])

    return mensal.sort_values("periodo")


@st.cache_data(show_spinner=False)
def kpi_volume_canal() -> pd.DataFrame:
    """
    KPI 2: Volume financeiro (R$) e nº de transações por canal e ano.
    """
    df = gold_fact_transactions()
    return (
        df.groupby(["ano", "canal"])
        .agg(
            volume_total=("valor", "sum"),
            qtd_tx=("transaction_id", "count"),
        )
        .reset_index()
    )


@st.cache_data(show_spinner=False)
def kpi_perfil_risco() -> pd.DataFrame:
    """
    KPI 3: Distribuição de clientes por faixa de risco.
    """
    df = silver_customers()
    return (
        df.groupby("faixa_risco")
        .agg(qtd_clientes=("customer_id", "count"))
        .reset_index()
        .sort_values("qtd_clientes", ascending=False)
    )


@st.cache_data(show_spinner=False)
def kpi_correlacao_macro() -> pd.DataFrame:
    """
    KPI 4: Volume mensal transacionado vs indicadores macroeconômicos.
    """
    df = gold_fact_transactions()
    mensal = (
        df.groupby(["anomes_id", "selic", "desemprego"])
        .agg(volume_total=("valor", "sum"))
        .reset_index()
    )

    mensal["periodo"] = pd.to_datetime(mensal["anomes_id"])
    return mensal.sort_values("periodo")
