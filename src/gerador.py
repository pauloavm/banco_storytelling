"""
gerador.py
----------
Responsável por gerar os três datasets sintéticos do pipeline bancário.
Encapsula toda a lógica de geração em funções independentes para
permitir reuso nas páginas Streamlit.

Filosofia: dados gerados UMA VEZ e salvos em /data.
           A app lê os CSVs — nunca regenera em runtime.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# ── Semente global para reprodutibilidade ──────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("pt_BR")
Faker.seed(SEED)

# ── Constantes de negócio ──────────────────────────────────────────────────
N_CLIENTES       = 15_000
DATA_INICIO      = datetime(2000, 1, 1)
DATA_FIM         = datetime(2025, 12, 31)
DATA_PIX         = datetime(2020, 11, 1)   # Lançamento oficial do PIX

FAIXAS_RENDA = [
    "Até R$2.000",
    "R$2.001 a R$5.000",
    "R$5.001 a R$10.000",
    "Acima de R$10.000",
]

CANAIS_PRE_PIX  = ["Agência", "Caixa Eletrônico", "Internet Banking", "Mobile App"]
CANAIS_POS_PIX  = ["Agência", "Caixa Eletrônico", "Internet Banking", "Mobile App", "PIX"]

TIPOS_TRANSACAO = [
    "Transferência", "Pagamento de Conta", "Saque",
    "Depósito", "Investimento", "Empréstimo",
]

ESTADOS_BR = [
    "SP", "RJ", "MG", "RS", "PR", "SC",
    "BA", "GO", "PE", "CE", "DF", "AM",
]


# ── 1. Gerador de Clientes ─────────────────────────────────────────────────
def gerar_clientes(n: int = N_CLIENTES) -> pd.DataFrame:
    """
    Gera DataFrame de clientes fictícios com perfil demográfico e financeiro.

    Campos gerados:
    - customer_id     : identificador único (UUID simplificado)
    - nome            : nome completo (Faker pt_BR)
    - data_nascimento : entre 1950 e 2000
    - cidade / estado : aleatório entre principais cidades BR
    - data_abertura   : data de abertura da conta (2000-2023)
    - faixa_renda     : faixa de renda mensal
    - score_credito   : score entre 300 e 1000
    """
    registros = []

    for i in range(n):
        data_nasc   = fake.date_of_birth(minimum_age=18, maximum_age=75)
        data_aber   = fake.date_between(
            start_date=DATA_INICIO.date(),
            end_date=datetime(2023, 12, 31).date()
        )
        score       = int(np.clip(np.random.normal(650, 150), 300, 1000))
        faixa       = np.random.choice(
            FAIXAS_RENDA,
            p=[0.35, 0.30, 0.20, 0.15]   # distribuição realista BR
        )

        registros.append({
            "customer_id"    : f"CLI{i+1:06d}",
            "nome"           : fake.name(),
            "data_nascimento": data_nasc,
            "cidade"         : fake.city(),
            "estado"         : np.random.choice(ESTADOS_BR),
            "data_abertura"  : data_aber,
            "faixa_renda"    : faixa,
            "score_credito"  : score,
        })

    return pd.DataFrame(registros)


# ── 2. Gerador de Transações ───────────────────────────────────────────────
def gerar_transacoes(df_clientes: pd.DataFrame) -> pd.DataFrame:
    """
    Gera histórico de transações para cada cliente.

    Regras de negócio simuladas:
    - Cada cliente gera entre 5 e 200 transações ao longo da vida da conta
    - PIX só aparece a partir de novembro/2020
    - Probabilidade de canal digital aumenta com o tempo (tendência real)
    - Valor das transações varia por tipo e faixa de renda
    """
    registros = []

    for _, cliente in df_clientes.iterrows():
        data_aber    = pd.to_datetime(cliente["data_abertura"])
        n_transacoes = random.randint(5, 200)

        for _ in range(n_transacoes):
            # Data aleatória entre abertura da conta e 2025
            dias_ativos = (DATA_FIM - data_aber).days
            if dias_ativos <= 0:
                continue

            data_tx = data_aber + timedelta(days=random.randint(0, dias_ativos))

            # Canal: lógica temporal (digital cresce com o tempo)
            ano = data_tx.year
            prob_digital = min(0.15 + (ano - 2000) * 0.035, 0.85)

            if data_tx >= DATA_PIX:
                canais  = CANAIS_POS_PIX
                # PIX tem peso crescente após 2020
                peso_pix = min((ano - 2020) * 0.08, 0.40)
                pesos   = [
                    (1 - prob_digital) * 0.5,          # Agência
                    (1 - prob_digital) * 0.5,          # Caixa
                    prob_digital * (1 - peso_pix) * 0.5,  # Internet
                    prob_digital * (1 - peso_pix) * 0.5,  # Mobile
                    peso_pix,                          # PIX
                ]
            else:
                canais = CANAIS_PRE_PIX
                pesos  = [
                    (1 - prob_digital) * 0.5,
                    (1 - prob_digital) * 0.5,
                    prob_digital * 0.5,
                    prob_digital * 0.5,
                ]

            # Normaliza pesos
            pesos = np.array(pesos)
            pesos = pesos / pesos.sum()

            canal = np.random.choice(canais, p=pesos)
            tipo  = np.random.choice(TIPOS_TRANSACAO)

            # Valor baseado na faixa de renda
            multiplicador = {
                "Até R$2.000"         : 1.0,
                "R$2.001 a R$5.000"   : 2.5,
                "R$5.001 a R$10.000"  : 5.0,
                "Acima de R$10.000"   : 12.0,
            }.get(cliente["faixa_renda"], 1.0)

            valor = round(
                abs(np.random.lognormal(mean=5.5, sigma=1.2)) * multiplicador, 2
            )

            registros.append({
                "transaction_id" : f"TXN{len(registros)+1:010d}",
                "customer_id"    : cliente["customer_id"],
                "data_transacao" : data_tx.date(),
                "tipo_transacao" : tipo,
                "canal"          : canal,
                "valor"          : valor,
                "estado"         : cliente["estado"],
            })

    return pd.DataFrame(registros)


# ── 3. Executor principal (gera e salva CSVs) ──────────────────────────────
def gerar_e_salvar(output_dir: str = "data") -> dict:
    """
    Orquestra a geração de todos os datasets e salva em /data.

    Retorna dict com os DataFrames gerados para uso imediato,
    evitando releitura de disco quando chamado uma vez.
    """
    os.makedirs(output_dir, exist_ok=True)

    print("⏳ Gerando clientes...")
    df_clientes = gerar_clientes()
    df_clientes.to_csv(f"{output_dir}/d_customer.csv", index=False)
    print(f"   ✅ {len(df_clientes):,} clientes gerados.")

    print("⏳ Gerando transações (pode levar alguns minutos)...")
    df_transacoes = gerar_transacoes(df_clientes)
    df_transacoes.to_csv(f"{output_dir}/f_transactions.csv", index=False)
    print(f"   ✅ {len(df_transacoes):,} transações geradas.")

    return {
        "clientes"   : df_clientes,
        "transacoes" : df_transacoes,
    }


if __name__ == "__main__":
    gerar_e_salvar()