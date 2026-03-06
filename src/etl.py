import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# BRONZE → SILVER
# ─────────────────────────────────────────


def bronze_to_silver_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige tipos e limpa silver_customers."""
    df = df.copy()
    df["data_abertura_conta"] = pd.to_datetime(df["data_abertura_conta"])
    df["customer_id"] = df["customer_id"].astype(int)
    df["score_de_credito"] = df["score_de_credito"].astype(int)
    df["idade"] = df["idade"].astype(int)
    df = df.dropna(subset=["customer_id", "data_abertura_conta"])
    return df


def bronze_to_silver_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige tipos e cria chave anomes_id para silver_transactions."""
    df = df.copy()
    df["data_transacao"] = pd.to_datetime(df["data_transacao"])
    df["valor"] = df["valor"].astype(float)
    df["transaction_id"] = df["transaction_id"].astype(int)
    df["customer_id"] = df["customer_id"].astype(int)
    df["anomes_id"] = df["data_transacao"].dt.strftime("%Y%m")
    df["ano"] = df["data_transacao"].dt.year
    df["mes"] = df["data_transacao"].dt.month
    df = df.dropna(subset=["transaction_id", "customer_id", "valor"])
    df = df[df["valor"] > 0]
    return df


def bronze_to_silver_macro(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige tipos e cria chave anomes_id para silver_macro."""
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"])
    df["anomes_id"] = df["data"].dt.strftime("%Y%m")
    for col in ["selic", "ipca", "desemprego"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ─────────────────────────────────────────
# SILVER → GOLD
# ─────────────────────────────────────────


def build_dim_date(start: str = "2000-01-01", end: str = "2025-03-31") -> pd.DataFrame:
    """Dimensão de datas completa."""
    datas = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"data": datas})
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["trimestre"] = df["data"].dt.quarter
    df["dia_semana"] = df["data"].dt.day_name()
    df["anomes_id"] = df["data"].dt.strftime("%Y%m")
    df["ano_mes_label"] = df["data"].dt.to_period("M").astype(str)
    return df


def build_gold_transactions(
    silver_tx: pd.DataFrame, silver_customers: pd.DataFrame, silver_macro: pd.DataFrame
) -> pd.DataFrame:
    """
    Tabela fato Gold — une transações, clientes e macro.
    Equivalente ao gold_f_transactions do projeto Bancario.
    """
    # Join com clientes
    gold = silver_tx.merge(
        silver_customers[
            [
                "customer_id",
                "estado",
                "faixa_renda",
                "score_de_credito",
                "data_abertura_conta",
            ]
        ],
        on="customer_id",
        how="left",
    )

    # Join com macro (pela chave anomes_id)
    macro_slim = silver_macro[
        ["anomes_id", "selic", "ipca", "desemprego"]
    ].drop_duplicates("anomes_id")
    gold = gold.merge(macro_slim, on="anomes_id", how="left")

    # Segmentação de risco (replicando KPI 3 do projeto original)
    def faixa_risco(score):
        if score >= 800:
            return "Excelente"
        elif score >= 650:
            return "Bom"
        elif score >= 500:
            return "Médio"
        else:
            return "Alto"

    gold["faixa_risco"] = gold["score_de_credito"].apply(faixa_risco)

    # Canal digital ou físico
    gold["canal_digital"] = gold["canal"].isin(["Internet Banking", "Mobile App"])

    return gold


# ─────────────────────────────────────────
# KPIs — cálculos prontos para visualização
# ─────────────────────────────────────────


def kpi_adocao_digital(gold: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 1: % de transações digitais por mês.
    Retorna: ano_mes | total_tx | tx_digital | pct_digital
    """
    gold["ano_mes"] = gold["data_transacao"].dt.to_period("M").astype(str)
    agg = (
        gold.groupby("ano_mes")
        .agg(total_tx=("transaction_id", "count"), tx_digital=("canal_digital", "sum"))
        .reset_index()
    )
    agg["pct_digital"] = (agg["tx_digital"] / agg["total_tx"] * 100).round(2)
    return agg


def kpi_volume_por_canal(gold: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 2: Volume financeiro e número de transações por canal e ano.
    Retorna: ano | canal | volume_total | n_transacoes
    """
    agg = (
        gold.groupby(["ano", "canal"])
        .agg(volume_total=("valor", "sum"), n_transacoes=("transaction_id", "count"))
        .reset_index()
    )
    return agg


def kpi_perfil_risco(gold: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 3: Distribuição de clientes por faixa de risco.
    Retorna: faixa_risco | n_clientes | pct
    """
    clientes_unicos = gold.drop_duplicates("customer_id")
    agg = (
        clientes_unicos.groupby("faixa_risco")
        .agg(n_clientes=("customer_id", "count"))
        .reset_index()
    )
    agg["pct"] = (agg["n_clientes"] / agg["n_clientes"].sum() * 100).round(1)
    ordem = ["Excelente", "Bom", "Médio", "Alto"]
    agg["faixa_risco"] = pd.Categorical(
        agg["faixa_risco"], categories=ordem, ordered=True
    )
    agg = agg.sort_values("faixa_risco")
    return agg


def kpi_correlacao_macro(gold: pd.DataFrame) -> pd.DataFrame:
    """
    KPI 4: Volume transacionado vs. SELIC e desemprego ao longo do tempo.
    Retorna: ano_mes | volume_total | selic | desemprego
    """
    gold["ano_mes"] = gold["data_transacao"].dt.to_period("M").astype(str)
    agg = (
        gold.groupby("ano_mes")
        .agg(
            volume_total=("valor", "sum"),
            selic=("selic", "mean"),
            desemprego=("desemprego", "mean"),
        )
        .reset_index()
    )
    return agg
