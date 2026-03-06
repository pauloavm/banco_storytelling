import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="KPIs Estratégicos", layout="wide")
st.title("KPIs e Indicadores de Negócio")
st.markdown(
    "Painéis de acompanhamento estratégico com aplicação de técnicas de Storytelling para direcionamento de decisões operacionais."
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
    st.error(
        "Falha de Dependência: Execute a geração de dados antes de acessar os painéis."
    )
    st.stop()

from src.etl import kpi_adocao_digital, kpi_volume_por_canal, kpi_perfil_risco
from src.viz import plot_adocao_digital, plot_volume_canal, plot_perfil_risco

# ──────────────────────────────────────────────────
# KPI 1 — Adoção Digital
# ──────────────────────────────────────────────────
st.subheader("Indicador 1: Evolução da Adoção Digital")

with st.expander("Aprofundamento Estratégico e Possíveis Cenários"):
    st.markdown(
        """
    **Objetivo da Métrica:** Monitorar a proporção do volume de transações em canais digitais (App e Internet Banking) versus canais físicos.
    
    **Cenários e Interpretações Analíticas:**
    - **Estagnação na adoção digital:** Se a curva apresentar platô mesmo após lançamentos tecnológicos (como o PIX), isso pode apontar para barreiras de UX/UI no aplicativo ou resistência de faixas etárias específicas da base.
    - **Queda abrupta:** Indica possíveis instabilidades críticas de sistema ou fraudes em massa que levaram os clientes a retornar aos canais de contingência física.
    - **Direcionamento:** O aumento sustentado desta curva justifica a realocação de OPEX (despesas operacionais) com agências físicas para CAPEX (investimentos em infraestrutura de nuvem e segurança cibernética).
    """
    )

df_digital = kpi_adocao_digital(gold)
col1, col2, col3 = st.columns(3)
col1.metric("Penetração Digital Atual", f"{df_digital['pct_digital'].iloc[-1]:.1f}%")
col2.metric(
    "Penetração Histórica (Ano 2000)", f"{df_digital['pct_digital'].iloc[0]:.1f}%"
)
delta = df_digital["pct_digital"].iloc[-1] - df_digital["pct_digital"].iloc[0]
col3.metric("Crescimento Acumulado", f"+{delta:.1f} p.p.", delta_color="normal")

fig1 = plot_adocao_digital(df_digital)
st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

# ──────────────────────────────────────────────────
# KPI 2 — Volume por Canal
# ──────────────────────────────────────────────────
st.divider()
st.subheader("Indicador 2: Distribuição do Volume Financeiro por Canal")

with st.expander("Aprofundamento Estratégico e Possíveis Cenários"):
    st.markdown(
        """
    **Objetivo da Métrica:** Quantificar a movimentação de capital segregada por ponto de contato institucional.
    
    **Cenários e Interpretações Analíticas:**
    - **Alto volume em canais físicos (Agências):** Caso o volume em reais se mantenha alto nas agências, mesmo com queda no número de transações, isso sinaliza operações corporativas (B2B) ou de alta renda (Wealth Management) que exigem validação gerencial humana.
    - **Crescimento acelerado do Mobile:** Confirma a consolidação do smartphone como principal ferramenta de pagamentos. Exige políticas rigorosas de escalabilidade de servidores para mitigar downtime em horários de pico comercial.
    """
    )

df_canal = kpi_volume_por_canal(gold)
col1, col2 = st.columns([2, 1])
with col1:
    fig2 = plot_volume_canal(df_canal)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
with col2:
    st.markdown("**Síntese Consolidada por Canal**")
    resumo = (
        df_canal.groupby("canal")
        .agg(Volume=("volume_total", "sum"), Transações=("n_transacoes", "sum"))
        .reset_index()
    )
    resumo["Volume"] = resumo["Volume"].apply(lambda v: f"R$ {v/1e9:.2f}B")
    resumo["Transações"] = resumo["Transações"].apply(lambda v: f"{v:,}")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────
# KPI 3 — Perfil de Risco
# ──────────────────────────────────────────────────
st.divider()
st.subheader("Indicador 3: Segmentação de Risco de Crédito")

with st.expander("Aprofundamento Estratégico e Possíveis Cenários"):
    st.markdown(
        """
    **Objetivo da Métrica:** Expor a composição da carteira de clientes baseada em bureaus de avaliação (Score).
    
    **Cenários e Interpretações Analíticas:**
    - **Expansão da faixa 'Alto Risco':** Um aumento percentual nesta faixa indica iminente elevação das taxas de inadimplência (NPL - Non-Performing Loans). A recomendação imediata é o endurecimento dos critérios de esteira de concessão de crédito.
    - **Concentração na faixa 'Excelente':** Apresenta uma carteira conservadora e saudável, contudo, se for expressivamente majoritária, pode indicar um modelo de aprovação de crédito muito restritivo, custando *market share* ao banco em produtos de menor ticket.
    """
    )

df_risco = kpi_perfil_risco(gold)
col1, col2 = st.columns([3, 2])
with col1:
    fig3 = plot_perfil_risco(df_risco)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
with col2:
    st.markdown("**Composição da Carteira**")
    st.dataframe(
        df_risco[["faixa_risco", "n_clientes", "pct"]].rename(
            columns={
                "faixa_risco": "Classificação",
                "n_clientes": "Contas Ativas",
                "pct": "Representatividade (%)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    alto = df_risco[df_risco["faixa_risco"] == "Alto"]
    if not alto.empty:
        st.warning(
            f"Alerta de Exposição: {alto['pct'].values[0]}% da base encontra-se classificada como 'Alto Risco' "
            f"({alto['n_clientes'].values[0]:,} contratos). Avaliar necessidade de provisionamento extra."
        )
