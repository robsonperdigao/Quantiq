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


def plot_comparison(acao_returns, benchmark_returns):
    plt.figure(figsize=(12, 6))
    
    plt.plot(acao_returns.index, acao_returns.values, label='Ação')
    plt.plot(benchmark_returns.index, benchmark_returns.values, label='Benchmark')
    
    plt.title('Comparação de Retornos Acumulados')
    plt.xlabel('Data')
    plt.ylabel('Retorno Acumulado')
    plt.legend()
    plt.show()


st.set_page_config(page_title='Análise de Portfolio',
                    page_icon='📈',
                    layout='wide')

st.title('Análise de Portfolio')
st.write('Em desenvolvimento')
st.markdown('---')


benchmark_dict = {'Ibovespa': '^BVSP',
                'Dólar': 'USDBRL=X'}

col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
with col1:
    ativos = st.multiselect('Ativos da carteira', utils.lista_ativos_b3(), placeholder='Digite o nome da ação', key='carteira')
    ativos = [i + '.SA' for i in ativos]
with col2:
    benchmarks = st.multiselect('Selecione o(s) Benchmark(s)', benchmark_dict.keys(), placeholder='Digite o nome do benchmark', key='benchmark_carteira')
with col3:
    aporte = st.number_input('Aporte inicial', min_value=0.00, value=10000.00, step=0.01, placeholder='Digite o valor')
with col4:
    data_ini = st.date_input('Data de início da análise', format='DD/MM/YYYY', value=(datetime.today() - timedelta(days=1)), max_value=(datetime.today() - timedelta(days=1)))

    
if not benchmarks or not ativos:
    st.warning('Digite pelo menos 1 ação e 1 benchmark')

else:
    precos = yf.download(ativos, start=data_ini)['Adj Close'][:-1]
    if precos.empty:
        st.warning('Não há valores para a data selecionada, digite uma data diferente ou selecione outro ativo')
    else:
        if len(ativos) == 1:
            precos = pd.DataFrame(precos)
            retornos = precos/precos.iloc[0]
            retornos = retornos.dropna()
            carteira = retornos
            carteira.rename(columns={'Adj Close': 'Carteira'}, inplace=True)
        else:
            precos['Carteira'] = precos.sum(axis = 1)
            retornos = precos/precos.iloc[0]
            retornos = retornos.dropna()
            carteira = retornos['Carteira']
            retornos = retornos.drop(['Carteira'], axis = 1)

        st.markdown('### Gráfico dos retornos do(s) ativo(s) da carteira')
        st.line_chart(retornos)

        consolidado = pd.DataFrame()

        for benchmark in benchmarks:
            benchmark_ticker = benchmark_dict[benchmark]
            precos_benchmark = yf.download(benchmark_ticker, start=data_ini)['Adj Close'][:-1]
            retornos_benchmark = precos_benchmark/precos_benchmark[0]
            consolidado_benchmark = pd.merge(carteira, retornos_benchmark, how='inner', on='Date')
            consolidado_benchmark.rename(columns={'Adj Close': benchmark}, inplace=True)
            consolidado = pd.merge(consolidado, consolidado_benchmark, how='outer', left_index=True, right_index=True)
        
        consolidado = pd.merge(consolidado, carteira, how='inner', left_index=True, right_index=True)
        consolidado = consolidado.drop(columns=['Carteira_y'], axis=1)

        if len(benchmarks) > 1:
            consolidado = consolidado.drop(columns=['Carteira_x'], axis=1)  
        else:
            consolidado.rename(columns={'Carteira_x': 'Carteira'}, inplace=True)
        
        st.markdown('### Comparativo de retornos do(s) benchmark(s) com a carteira')
        st.line_chart(consolidado)
        
        st.markdown('### Resumo do portfolio')
        patrimonio = round(aporte * consolidado['Carteira'].iloc[-1], 2)
        num_colunas = len(benchmarks) + 3
        colunas = st.columns(num_colunas)
        colunas[0].metric('Valor investido', 'R$ ' + str(aporte))
        colunas[1].metric('Valor atual do portfolio', 'R$ ' + str(patrimonio))
        colunas[2].metric('Retorno Carteira', str(round((consolidado['Carteira'].iloc[-1] - 1) * 100, 2)) + '%')

        for i, benchmark in enumerate(benchmarks, start=3):
            colunas[i].metric(f'Retorno {benchmark}', str(round((consolidado[benchmark].iloc[-1] - 1) * 100, 2)) + '%')

        
        
        
        
        # Adicionar a opção de inserir a quantidade ações compradas pra cada ativo no dia 0 e calcular o valor aportado
        # Inserir gráfico de pizza com o valor aportado em cada ativo
        # Inserir dados fundamentalistas dos ativos em formato de gráfico de barras para comparar entre os ativos
        # Inserir gráfico de correlação entre ativos
        # Adicionar gráfico de barras com o retorno de cada ativo para comparar 
        # Adicionar Alpha, Beta, Z-Score da carteira com o benchmark (se possível, também o gráfico)
        # Inserir relatório quantstats como imagem da carteira com o benchmark
        # Inserir análise de Markovitz para calcular os pesos ideais em cada ativo para obter o melhor retorno e o gráfico



        