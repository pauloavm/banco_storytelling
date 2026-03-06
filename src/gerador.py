import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import requests  # Lembre-se de adicionar 'requests' ao seu requirements.txt

fake = Faker("pt_BR")
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────
# GERADOR DE CLIENTES
# ─────────────────────────────────────────


def obter_cidades_ibge() -> dict:
    """
    Consome a API do IBGE e retorna um dicionário mapeando siglas de UF
    para listas de nomes de municípios. Trata dados ausentes.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()

        cidades_uf = {}
        for municipio in dados:
            try:
                # Extração com tratamento para registros sem microrregião (ex: DF)
                uf = municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
                nome = municipio["nome"]

                if uf not in cidades_uf:
                    cidades_uf[uf] = []
                cidades_uf[uf].append(nome)
            except (KeyError, TypeError):
                # Ignora o município específico e continua a iteração
                continue

        if not cidades_uf:
            raise ValueError("O mapeamento retornou um dicionário vazio.")

        return cidades_uf

    except Exception as e:
        print(f"Erro ao acessar API do IBGE: {e}. Utilizando dados de fallback.")
        # Fallback de segurança em caso de falha de rede
        return {
            "SP": [
                "São Paulo",
                "Campinas",
                "Guarulhos",
                "São Bernardo do Campo",
                "Ribeirão Preto",
            ],
            "RJ": [
                "Rio de Janeiro",
                "Niterói",
                "Duque de Caxias",
                "São Gonçalo",
                "Nova Iguaçu",
            ],
            "MG": ["Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim"],
            "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria"],
            "PR": ["Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel"],
            "SC": ["Joinville", "Florianópolis", "Blumenau", "São José", "Chapecó"],
            "BA": [
                "Salvador",
                "Feira de Santana",
                "Vitória da Conquista",
                "Camaçari",
                "Itabuna",
            ],
            "CE": ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú", "Sobral"],
            "PE": [
                "Recife",
                "Jaboatão dos Guararapes",
                "Olinda",
                "Caruaru",
                "Petrolina",
            ],
            "GO": [
                "Goiânia",
                "Aparecida de Goiânia",
                "Anápolis",
                "Rio Verde",
                "Luziânia",
            ],
            "AM": ["Manaus", "Parintins", "Itacoatiara", "Manacapuru", "Coari"],
            "PA": ["Belém", "Ananindeua", "Santarém", "Marabá", "Castanhal"],
        }


def gerar_clientes(n: int = 15_000, path: str = "data/d_customer.csv") -> pd.DataFrame:
    """
    Gera base sintética de clientes bancários utilizando distribuição real de cidades
    e ordem cronológica de abertura de conta.
    """
    # Obtém o mapeamento real de todos os municípios brasileiros
    cidades_por_estado = obter_cidades_ibge()
    estados_disponiveis = list(cidades_por_estado.keys())

    faixas_renda = ["Até R$2k", "R$2k-5k", "R$5k-10k", "R$10k-20k", "Acima R$20k"]
    data_min = datetime(2000, 1, 1)
    data_max = datetime(2025, 12, 31)
    delta_dias = (data_max - data_min).days

    # Geração e ordenação cronológica das datas de abertura
    datas_abertura = sorted(
        [data_min + timedelta(days=random.randint(0, delta_dias)) for _ in range(n)]
    )

    registros = []
    for i in range(1, n + 1):
        # Atribui a data em ordem cronológica conforme o incremento do ID
        data_conta = datas_abertura[i - 1]

        # Seleção hierárquica e coerente
        estado_escolhido = random.choice(estados_disponiveis)
        cidade_escolhida = random.choice(cidades_por_estado[estado_escolhido])

        registros.append(
            {
                "customer_id": i,
                "nome": fake.name(),
                "idade": random.randint(18, 75),
                "cidade": cidade_escolhida,
                "estado": estado_escolhido,
                "data_abertura_conta": data_conta.strftime("%Y-%m-%d"),
                "faixa_renda": random.choice(faixas_renda),
                "score_de_credito": random.randint(300, 1000),
            }
        )

    df = pd.DataFrame(registros)
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False)
    return df


# ─────────────────────────────────────────
# COLETOR DE DADOS MACRO (com fallback sintético)
# ─────────────────────────────────────────
def coletar_macro(path: str = "data/d_macro_economic.csv") -> pd.DataFrame:
    """
    Tenta buscar dados reais do BACEN via biblioteca bcb.
    Em caso de falha, gera dados sintéticos plausíveis para o Brasil (2000-2025).
    """
    try:
        from bcb import sgs

        dados_macro = sgs.get(
            {"selic": 4189, "ipca": 433, "desemprego": 24369},
            start="2000-01-01",
            end="2026-02-28",
        )

        df = pd.DataFrame(dados_macro).reset_index()
        df.columns = ["data", "selic", "ipca", "desemprego"]
        df["anomes_id"] = (
            pd.to_datetime(df["data"])
            .dt.to_period("M")
            .astype(str)
            .str.replace("-", "")
        )

    except Exception:
        # FALLBACK: série sintética histórica plausível para o Brasil
        datas = pd.date_range("2000-01-01", "2025-03-01", freq="MS")
        n = len(datas)
        np.random.seed(99)
        # Selic: começou alta (~19%), foi caindo, subiu na pandemia, caiu e subiu novamente
        selic_base = np.interp(
            np.arange(n),
            [0, 60, 120, 150, 180, 210, 240, 270, 300],
            [19, 11, 13, 8, 6, 2, 13, 10, 10.5],
        ) + np.random.normal(0, 0.3, n)

        ipca_base = np.interp(
            np.arange(n),
            [0, 50, 100, 150, 200, 240, 270, 300],
            [7, 5, 6, 4, 3, 10, 5, 4.5],
        ) + np.random.normal(0, 0.2, n)

        desem_base = np.interp(
            np.arange(n), [0, 100, 170, 200, 230, 270, 300], [10, 5, 14, 11, 9, 8, 6.5]
        ) + np.random.normal(0, 0.3, n)

        df = pd.DataFrame(
            {
                "data": datas,
                "selic": np.clip(selic_base, 1.5, 27),
                "ipca": np.clip(ipca_base, 0.2, 12),
                "desemprego": np.clip(desem_base, 4, 15),
            }
        )
        df["anomes_id"] = df["data"].dt.to_period("M").astype(str).str.replace("-", "")

    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False)
    return df


# ─────────────────────────────────────────
# GERADOR DE TRANSAÇÕES
# ─────────────────────────────────────────
def gerar_transacoes(
    df_clientes: pd.DataFrame, path: str = "data/f_transactions.csv"
) -> pd.DataFrame:
    """
    Gera histórico de transações bancárias por cliente.
    Simula a evolução digital: maior probabilidade de canais digitais
    ao longo do tempo, e introdução do PIX em novembro/2020.
    """
    tipos_base = [
        "Depósito",
        "Saque",
        "Transferência",
        "Pagamento de Conta",
        "Investimento",
        "Empréstimo",
    ]
    tipos_com_pix = tipos_base + ["PIX"]

    canais_por_ano = {
        # ano: [Agência, Caixa Eletrônico, Internet Banking, Mobile App]
        # pesos somam 1.0 — evolução digital ao longo do tempo
        2000: [0.70, 0.25, 0.05, 0.00],
        2005: [0.50, 0.30, 0.18, 0.02],
        2010: [0.30, 0.28, 0.30, 0.12],
        2015: [0.18, 0.18, 0.35, 0.29],
        2020: [0.08, 0.10, 0.32, 0.50],
        2025: [0.04, 0.06, 0.28, 0.62],
    }
    canais = ["Agência", "Caixa Eletrônico", "Internet Banking", "Mobile App"]

    def get_pesos_canal(ano: int) -> list:
        anos_ref = sorted(canais_por_ano.keys())
        if ano <= anos_ref[0]:
            return canais_por_ano[anos_ref[0]]
        if ano >= anos_ref[-1]:
            return canais_por_ano[anos_ref[-1]]
        for i in range(len(anos_ref) - 1):
            if anos_ref[i] <= ano < anos_ref[i + 1]:
                a0, a1 = anos_ref[i], anos_ref[i + 1]
                t = (ano - a0) / (a1 - a0)
                p0 = np.array(canais_por_ano[a0])
                p1 = np.array(canais_por_ano[a1])
                pesos = p0 * (1 - t) + p1 * t
                return (pesos / pesos.sum()).tolist()
        return canais_por_ano[anos_ref[-1]]

    registros = []
    tx_id = 1
    data_fim = datetime(2025, 3, 31)
    pix_inicio = datetime(2020, 11, 1)

    for _, cliente in df_clientes.iterrows():
        data_abertura = datetime.strptime(cliente["data_abertura_conta"], "%Y-%m-%d")
        # Número de transações baseado na faixa de renda
        n_tx_map = {
            "Até R$2k": (30, 80),
            "R$2k-5k": (60, 150),
            "R$5k-10k": (100, 250),
            "R$10k-20k": (150, 400),
            "Acima R$20k": (200, 600),
        }
        n_min, n_max = n_tx_map.get(cliente["faixa_renda"], (50, 150))
        n_tx = random.randint(n_min, n_max)

        delta = (data_fim - data_abertura).days
        if delta <= 0:
            continue

        for _ in range(n_tx):
            data_tx = data_abertura + timedelta(days=random.randint(0, delta))
            ano_tx = data_tx.year

            # Tipos com PIX só após novembro/2020
            tipos_disponiveis = tipos_com_pix if data_tx >= pix_inicio else tipos_base
            tipo = random.choice(tipos_disponiveis)

            # Canal baseado no ano (evolução digital)
            pesos = get_pesos_canal(ano_tx)
            canal = random.choices(canais, weights=pesos, k=1)[0]

            # Valor baseado na faixa de renda
            valor_map = {
                "Até R$2k": (10, 1_500),
                "R$2k-5k": (20, 5_000),
                "R$5k-10k": (50, 15_000),
                "R$10k-20k": (100, 40_000),
                "Acima R$20k": (200, 150_000),
            }
            v_min, v_max = valor_map.get(cliente["faixa_renda"], (50, 5_000))
            valor = round(random.uniform(v_min, v_max), 2)

            registros.append(
                {
                    "transaction_id": tx_id,
                    "customer_id": int(cliente["customer_id"]),
                    "data_transacao": data_tx.strftime("%Y-%m-%d"),
                    "tipo_transacao": tipo,
                    "canal": canal,
                    "valor": valor,
                    "anomes_id": data_tx.strftime("%Y%m"),
                }
            )
            tx_id += 1

    df = pd.DataFrame(registros)
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False)
    return df
