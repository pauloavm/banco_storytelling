Olá, Paulo.

A inclusão da licença MIT é uma excelente decisão. Ela permite que outros profissionais e empresas utilizem, copiem e modifiquem o seu código livremente, desde que mantenham os créditos originais, o que ajuda muito na visibilidade do seu portfólio.

Para aplicar a licença corretamente no GitHub, você precisará atualizar o seu arquivo `README.md` e criar um novo arquivo chamado `LICENSE` na raiz do seu repositório.

### 1. Atualização do `README.md`

Adicionei a seção **"Licença"** ao final do documento. Segue o código completo e atualizado do seu `README.md`:

```markdown
# Banco Fictício: Pipeline Analítico e Storytelling com Dados

## Visão Geral
Este projeto consiste em um ambiente analítico completo de uma instituição financeira fictícia, desenvolvido em Python e Streamlit. O objetivo principal é demonstrar o ciclo de vida dos dados fim a fim: desde a geração de bases sintéticas fundamentadas em demografia real, passando pelo tratamento e modelagem estruturada (ETL), até a entrega de valor visual para a tomada de decisão executiva.

O repositório consolida duas disciplinas fundamentais do cenário corporativo de dados:
1. **Engenharia de Dados:** Aplicação da Arquitetura Medallion (camadas Bronze, Silver e Gold) para o saneamento, estruturação e enriquecimento das informações.
2. **Visualização de Dados:** Aplicação rigorosa das técnicas de "Storytelling com Dados", propostas por Cole Nussbaumer Knaflic, para a construção de painéis limpos, interativos e focados na ação.

## Principais Funcionalidades

* **Geração de Dados Sintéticos e Realistas:** Criação parametrizada de clientes e transações financeiras com base em dados geográficos reais (integração com a API de Municípios do IBGE).
* **Contexto Macroeconômico:** Coleta automatizada de indicadores oficiais (Taxa SELIC, IPCA e Taxa de Desemprego) via integração com o Banco Central do Brasil (BACEN).
* **Pipeline Medallion (ETL):** * **Bronze:** Armazenamento bruto das simulações operacionais e econômicas.
  * **Silver:** Limpeza de tipos de dados, remoção de inconsistências, padronização e criação de chaves de cruzamento temporal.
  * **Gold:** Modelagem dimensional (Tabela Fato e Dimensões) preparada exclusivamente para o consumo analítico e processamento dos indicadores de negócio.
* **Dashboards Executivos e Interativos:** Gráficos interativos renderizados via Plotly, projetados sem ruído visual (remoção de bordas e eixos desnecessários), contendo títulos narrativos, anotações de eventos disruptivos (como o lançamento do PIX) e destaques de atenção por saturação de cor.

## Estrutura do Repositório

```text
├── app.py                   # Ponto de entrada da aplicação Streamlit (Página Inicial)
├── requirements.txt         # Relação de dependências e versões fixadas do projeto
├── data/                    # Diretório local para armazenamento dos arquivos CSV estáticos (Camada Bronze)
├── pages/                   # Módulos das páginas da interface web
│   ├── 01_geracao.py        # Interface para parametrização e geração do volume de dados
│   ├── 02_pipeline.py       # Demonstração visual do fluxo ETL e validação de registros
│   ├── 03_kpis.py           # Painel de indicadores de negócios (Adoção Digital, Volume por Canal, Risco de Crédito)
│   └── 04_correlacao.py     # Análise estatística (Correlação de Pearson) entre dados bancários e macroeconomia
└── src/                     # Código-fonte e regras de negócio encapsuladas
    ├── etl.py               # Funções de transformação de dados e cálculos agregados de KPIs
    ├── gerador.py           # Lógica de criação de dados sintéticos e consumo de APIs públicas
    └── viz.py               # Padronização visual corporativa e funções de plotagem gráfica

```

## Tecnologias e Bibliotecas Utilizadas

* **Linguagem:** Python 3.12+
* **Interface Web:** Streamlit
* **Manipulação e Processamento de Dados:** Pandas, NumPy
* **Visualização de Dados:** Plotly
* **Geração e Extração de Dados:** Faker, Python-BCB (Banco Central), Requests (API IBGE)

## Instruções para Execução Local

1. Clone este repositório para o seu ambiente local:

```bash
git clone [https://github.com/pauloavm/banco_storytelling.git](https://github.com/pauloavm/banco_storytelling.git)
cd banco_storytelling

```

2. Crie e ative um ambiente virtual isolado:

```bash
python -m venv venv

# Ativação no Windows:
venv\Scripts\activate

# Ativação no Linux/macOS:
source venv/bin/activate

```

3. Instale as dependências exigidas pelo projeto:

```bash
pip install -r requirements.txt

```

4. Inicie o servidor da aplicação:

```bash
streamlit run app.py

```

**Nota Operacional:** Ao executar a aplicação localmente pela primeira vez, navegue até a página "1. Geração de Dados" através do menu lateral para provisionar a carga inicial da camada Bronze. No ambiente de nuvem, a aplicação consome os dados pré-processados alocados no diretório `data/` para preservar a estabilidade da memória.

## Referências Metodológicas

* **Knaflic, Cole Nussbaumer.** *Storytelling com Dados: um guia para profissionais de negócios*. As diretrizes desta obra refletem diretamente nas escolhas visuais do projeto, priorizando a minimização da carga cognitiva e o uso estratégico do contraste.
* **Arquitetura Medallion:** Padrão arquitetural de dados amplamente adotado no ecossistema de Engenharia de Dados para assegurar governança, qualidade e escalabilidade na estruturação lógica de Data Lakes e Data Warehouses.

## Autor e Contato

**Paulo Munhoz**

* LinkedIn: [https://www.linkedin.com/in/paulomunhoz/](https://www.linkedin.com/in/paulomunhoz/)

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.
