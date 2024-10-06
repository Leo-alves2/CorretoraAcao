# IMPORTAR BIBLIOTECAS
import streamlit as st  # Para criar a interface web
import pandas as pd     # Para manipulação de dados
import yfinance as yf   # Para obter os dados das ações
from datetime import timedelta  # Para trabalhar com intervalos de datas

# FUNÇÃO PARA CARREGAR DADOS DAS AÇÕES
# Esta função usa a biblioteca `yfinance` para buscar dados de ações de uma lista de empresas
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)  # Cria uma string contendo todos os tickers separados por espaço
    dados_acao = yf.Tickers(texto_tickers)  # Obtém os dados das ações
    # Pega o histórico de preços de fechamento das ações desde 2010-01-01 até 2024-07-01
    cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-07-01")
    cotacoes_acao = cotacoes_acao["Close"]  # Mantém apenas o preço de fechamento das ações
    return cotacoes_acao

# FUNÇÃO PARA CARREGAR OS TICKERS DAS AÇÕES
# Esta função carrega os códigos de ações (tickers) a partir de um arquivo CSV
@st.cache_data
def carregar_teckers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")  # Lê o arquivo CSV contendo os tickers
    tickers = list(base_tickers["Codigo"])  # Extrai os tickers da coluna 'Codigo'
    tickers = [item + ".SA" for item in tickers]  # Adiciona ".SA" para indicar ações brasileiras (B3)
    return tickers

# CARREGAR OS DADOS
acoes = carregar_teckers_acoes()  # Carrega os tickers das ações
dados = carregar_dados(acoes)     # Carrega os dados históricos dessas ações

# CRIAR A INTERFACE DO STREAMLIT
st.write("""
# Aplicativo de Preços de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos.
""")  # Exibe o título e a descrição da aplicação

# PREPARAR OS FILTROS (SIDEBAR)
st.sidebar.header("Filtros")  # Título da barra lateral

# FILTRO DE AÇÕES (MULTISELÇÃO)
# Permite ao usuário selecionar uma ou mais ações para visualização
lista_acoes = st.sidebar.multiselect('Escolha as ações para visualização', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]  # Filtra os dados para exibir apenas as ações selecionadas
    if len(lista_acoes) == 1:   # Se apenas uma ação for selecionada, renomeia a coluna para 'Close'
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: "Close"})

# FILTRO DE DATA
# O controle deslizante permite ao usuário selecionar um período de tempo para a visualização dos dados
data_inicial = dados.index.min().to_pydatetime()  # Data mínima nos dados
data_final = dados.index.max().to_pydatetime()    # Data máxima nos dados

intervalo_data = st.sidebar.slider(
    "Selecione o período", 
    min_value=data_inicial, 
    max_value=data_final,
    value=(data_inicial, data_final),  # Período padrão do filtro
    step=timedelta(days=1)  # Incremento do controle deslizante (1 dia)
)

dados = dados.loc[intervalo_data[0]:intervalo_data[1]]  # Filtra os dados conforme o período selecionado

# CRIAR O GRÁFICO DE LINHA
# Exibe o gráfico da evolução dos preços de fechamento das ações no período selecionado
st.line_chart(dados)

# PERFORMANCE DOS ATIVOS
# Calcula a performance percentual dos ativos no período selecionado
texto_performance_ativos = ""

if len(lista_acoes) == 0:
    lista_acoes = list(dados.columns)  # Se nenhuma ação for selecionada, usa todas as ações do dataframe
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={"Close": acao_unica})  # Renomeia 'Close' de volta para o nome original da ação

# Itera sobre as ações e calcula a performance no período selecionado
for acao in lista_acoes:
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1  # Calcula a variação percentual
    performance_ativo = float(performance_ativo)

    # Formatação colorida para mostrar a performance positiva ou negativa
    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: {performance_ativo:.1%}"

# EXIBE A PERFORMANCE DOS ATIVOS
st.write(f"""
### Performance dos Ativos
Esta foi a performance de cada ativo no período selecionado:

{texto_performance_ativos}
""")  # Exibe a performance dos ativos na aplicação