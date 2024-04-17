import streamlit as st
import quantstats as qs
from datetime import datetime, timedelta
import pandas as pd
from src import utils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import datetime as dt
import yfinance as yf



def periodo_analise(data):
    data_atual = datetime.now().strftime("%Y-%m-%d")

    data = datetime.strptime(str(data), "%Y-%m-%d")
    data_atual = datetime.strptime(data_atual, "%Y-%m-%d")

    intervalo_datas = pd.date_range(data, data_atual)

    dias = len(intervalo_datas[(intervalo_datas.dayofweek < 5)])
    return f'{dias}d'

def plot_comparison(acao_returns, benchmark_returns):
    plt.figure(figsize=(12, 6))
    
    plt.plot(acao_returns.index, acao_returns.values, label='Ação')
    plt.plot(benchmark_returns.index, benchmark_returns.values, label='Benchmark')
    
    plt.title('Comparação de Retornos Acumulados')
    plt.xlabel('Data')
    plt.ylabel('Retorno Acumulado')
    plt.legend()
    plt.show()


st.set_page_config(page_title='Análise de Carteira',
                    page_icon='📈',
                    layout='wide')

st.title('Análise de Carteira')
st.write('Em desenvolvimento')
st.markdown('---')

qs.extend_pandas()
benchmark_dict = {'Ibovespa': '^BVSP', 
                'CDI': 'CDI',
                'Dólar': 'USDBRL=X'}

benchmark_dict = {'Ibovespa': '^BVSP',
                'Dólar': 'USDBRL=X'}

periodo_dict = {'3 meses': '3mo',
                '6 meses': '6mo',
                '1 ano': '1y',
                '2 anos': '2y',
                '3 anos': '3y',
                '5 anos': '5y',
                'Desde início': 'max'}


ativos = st.multiselect('Ativos da carteira', utils.lista_ativos_b3(), placeholder='Digite o nome da ação', key='carteira')
ativos = [i + '.SA' for i in ativos]

benchmarks = st.multiselect('Selecione o(s) Benchmark(s)', benchmark_dict.keys(), key='benchmark_carteira')
data_ini = st.date_input('Digite a data de início da análise', format='DD/MM/YYYY')
#periodo = periodo_dict[st.selectbox('Selecione o período de análise', periodo_dict.keys(), key='periodo_carteira')]
#retorno_benchmark = qs.utils.download_returns(benchmark, period=periodo)
    

precos = yf.download(ativos, start=data_ini)['Adj Close']
precos['Carteira'] = precos.sum(axis = 1)
retornos = precos/precos.iloc[0]
retornos = retornos.dropna()
carteira = retornos['Carteira']
retornos = retornos.drop(['Carteira'], axis = 1)
st.line_chart(retornos)

consolidado = pd.DataFrame()

for benchmark in benchmarks:
    benchmark_ticker = benchmark_dict[benchmark]
    precos_benchmark = yf.download(benchmark_ticker, start=data_ini)['Adj Close']
    retornos_benchmark = precos_benchmark/precos_benchmark[0]
    consolidado_benchmark = pd.merge(carteira, retornos_benchmark, how='inner', on='Date')
    consolidado_benchmark.rename(columns={'Adj Close': benchmark}, inplace=True)
    consolidado = pd.merge(consolidado, consolidado_benchmark, how='outer', left_index=True, right_index=True)

consolidado = consolidado.drop(columns=['Carteira_x', 'Carteira_y'], axis=1)
consolidado = pd.merge(consolidado, carteira, how='outer', left_index=True, right_index=True)
st.line_chart(consolidado)




precos_primeiro_dia = precos.iloc[0]


  
