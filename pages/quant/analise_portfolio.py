import streamlit as st
import quantstats as qs
from datetime import datetime, timedelta
import pandas as pd
from src import utils
import matplotlib.pyplot as plt
import seaborn as sns
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
    data_ini = st.date_input('Data de início da análise', format='DD/MM/YYYY', value=(datetime.today() - timedelta(days=365)), max_value=(datetime.today() - timedelta(days=365)))

    
if not benchmarks or not ativos:
    st.warning('Selecione pelo menos 1 ação e 1 benchmark')

else:
    precos = yf.download(ativos, start=data_ini)['Adj Close'][:-1]
    if precos.empty:
        st.warning('Não há valores para a data selecionada, digite uma data diferente ou selecione outro ativo')
    else:
        if len(ativos) == 1:
            precos = pd.DataFrame(precos)
            #retornos = yf.download(ativos, start=data_ini, interval='1mo')['Adj Close'][:-1].pct_change()
            retornos = precos/precos.iloc[0]
            retornos = retornos.dropna()
            retorno_diário = retornos['Carteira'].pct_change()
            carteira = retornos
            carteira.rename(columns={'Adj Close': 'Carteira'}, inplace=True)
        else:
            precos['Carteira'] = precos.sum(axis = 1)
            retornos = precos/precos.iloc[0]
            retornos = retornos.dropna()
            retorno_diário = retornos['Carteira'].pct_change()
            carteira = retornos['Carteira']
            retornos = retornos.drop(['Carteira'], axis = 1)      
        
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
        
        retorno_mensal = retorno_diário.groupby([retorno_diário.index.year.rename('Year'), retorno_diário.index.month.rename('Month')]).mean()
        tabela_retornos = pd.DataFrame(retorno_mensal)
        tabela_retornos = pd.pivot_table(tabela_retornos, values='Carteira', index = 'Year', columns = 'Month')
        tabela_retornos.columns = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        stats = pd.DataFrame(tabela_retornos.mean(), columns = ['Média'])
        stats['Mediana'] = tabela_retornos.median()
        stats['Maior'] = tabela_retornos.max()
        stats['Menor'] = tabela_retornos.min()
        stats['Positivos'] = tabela_retornos.gt(0).sum()/tabela_retornos.count()
        stats['Negativos'] = tabela_retornos.le(0).sum()/tabela_retornos.count()
        stats_a = stats[['Média', 'Mediana', 'Maior', 'Menor']]
        stats_a = stats_a.transpose()
        stats_b = stats[['Positivos', 'Negativos']]
        stats_b = stats_b.transpose()

        fig_retornos, ax_retornos = plt.subplots(figsize = (12, 6))
        color = sns.color_palette('RdYlGn', 9)
        sns.heatmap(tabela_retornos, cmap = color, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02,
                    cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax_retornos)
        
        #ax.set_title('Matriz de Retornos da Carteira', fontsize = 15)
        ax_retornos.set_yticklabels(ax_retornos.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '9')
        ax_retornos.set_xticklabels(ax_retornos.get_xticklabels(), fontsize = '9')
        ax_retornos.xaxis.tick_top()
        plt.ylabel('')

        fig_stats_a, ax_stats_a = plt.subplots(figsize = (12, 4))
        sns.heatmap(stats_a, cmap = color, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02, 
                    cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax_stats_a)
        ax_stats_a.set_yticklabels(ax_stats_a.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '9')
        ax_stats_a.set_xticklabels(ax_stats_a.get_xticklabels(), fontsize = '9')
        ax_stats_a.xaxis.tick_top()

        fig_stats_b, ax_stats_b = plt.subplots(figsize = (12, 2))
        sns.heatmap(stats_b, cmap = color, annot = True, fmt = '.2%', center = 0, 
                    cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax_stats_b)
        ax_stats_b.set_yticklabels(ax_stats_b.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '9')
        ax_stats_b.set_xticklabels(ax_stats_b.get_xticklabels(), fontsize = '9')
        ax_stats_b.xaxis.tick_top()
        
        st.markdown('### Gráfico dos retornos do(s) ativo(s) da carteira')
        st.line_chart(retornos)
        st.markdown('### Gráfico da volatilidade diária da carteira')
        st.line_chart(retorno_diário)
        st.markdown('### Matriz de Retornos da Carteira')
        st.pyplot(fig_retornos)
        st.markdown('### Análises Estatísticas da Carteira')
        st.pyplot(fig_stats_a)
        st.markdown('### Estatísticas de Retornos da Carteira')
        st.pyplot(fig_stats_b)
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



        