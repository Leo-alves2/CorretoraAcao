# importar as bibliotecas

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

# funcões de carregamento de dados
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-07-01")
    cotacoes_acao = cotacoes_acao["Close"] # dois cochete para dizer que quero um datafreme mantendo o index data
    return cotacoes_acao

@st.cache_data
def carregar_teckers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = list(base_tickers["Codigo"])
    # tickers = [str(item) + ".SA" for item in tickers]
    tickers = [item +".SA" for item in tickers]
    return tickers

# preparar para carregar

acoes = carregar_teckers_acoes()
dados = carregar_dados(acoes)

# criar a interface de streamlit

st.write("""
# Aplicativo de Preços de Ações
O gráfico abaixo representa a evolução do preço das ações ao logo dos anos
""")    

# preparar as visualizações ou filtros

st.sidebar.header("Filtros")


# filtro de acoes

lista_acoes = st.sidebar.multiselect('Escolha as ações para visualização', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})


# filtro de datas

data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()

intervalo_data = st.sidebar.slider("Selecione o periodo", 
                                   min_value=data_inicial, 
                                   max_value=data_final,
                                   value=(data_inicial, data_final),
                                   step= timedelta(days=1)) # determina o salta de tempo pode ser mes, ano, dia

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# criar o grafico

st.line_chart(dados)

# Performace dos ativos

texto_performance_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})


for acao in lista_acoes:
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] -1
    performance_ativo = float(performance_ativo)

    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: {performance_ativo:.1%}"

st.write(f"""
### Perfomance dos Ativos
Esta foi a performace de cada ativo no periodo selecionado:

{texto_performance_ativos}
""")  