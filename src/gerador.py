import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os
import requests  # Adicione 'requests' ao seu requirements.txt

fake = Faker("pt_BR")
np.random.seed(42)
random.seed(42)


def obter_cidades_ibge() -> dict:
    """
    Consome a API do IBGE e retorna um dicionário mapeando siglas de UF
    para listas de nomes de municípios.
    """
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()

        cidades_uf = {}
        for municipio in dados:
            uf = municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"]
            nome = municipio["nome"]
            if uf not in cidades_uf:
                cidades_uf[uf] = []
            cidades_uf[uf].append(nome)
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
    Gera base sintética de clientes bancários utilizando distribuição real de cidades.
    """
    # Obtém o mapeamento real de todos os municípios brasileiros
    cidades_por_estado = obter_cidades_ibge()
    estados_disponiveis = list(cidades_por_estado.keys())

    faixas_renda = ["Até R$2k", "R$2k-5k", "R$5k-10k", "R$10k-20k", "Acima R$20k"]
    data_min = datetime(2000, 1, 1)
    data_max = datetime(2025, 3, 1)
    delta_dias = (data_max - data_min).days

    registros = []
    for i in range(1, n + 1):
        data_conta = data_min + timedelta(days=random.randint(0, delta_dias))

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
