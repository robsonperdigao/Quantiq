import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from datetime import date

def lista_empresas():
    """
    Papel: Get list of tickers
      URL:
        http://fundamentus.com.br/detalhes.php

    Output:
      list
    """

    url = 'http://fundamentus.com.br/detalhes.php'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
           'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
           'Accept-Encoding': 'gzip, deflate',
           }
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text)[0]

    return list(df['Papel'])

st.set_page_config(page_title='Mapa de Retornos Mensais', 
                   page_icon='📈',
                   layout='wide')
st.title('Mapa de Retornos Mensais')
st.markdown('---')


opcao = st.radio('Selecione', ['Índices', 'Ações'])
col1, col2 = st.columns(2)
with col1:
    data_inicial = '1900-01-01' #st.date_input('Selecione a data inicial', min_value=date(), format='YYYY-MM-DD')
with col2:
    data_final = '2099-01-01' #st.date_input('Selecione a data final', max_value=date.today(),format='YYYY-MM-DD')

if opcao == 'Índices':
    with st.form(key = 'form_indice'):
        ticker = st.selectbox('Índices', ['IBOV', 'Dólar', 'S&P500', 'NASDAQ'])
        analisar = st.form_submit_button('Analisar')
else:
    with st.form(key = 'form_acoes'):
        ticker = st.selectbox('Ações', [i + '.SA' for i in lista_empresas()])
        analisar = st.form_submit_button('Analisar')
        
if analisar:
    if opcao == 'Índices':
        if ticker == 'IBOV':
            retornos = yf.download('^BVSP', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            cotacao = yf.download('^BVSP', start = data_inicial, end = data_final)['Close'].round(2)
        if ticker == 'Dólar':
            retornos = yf.download('USDBRL=X', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            cotacao = yf.download('USDBRL=X', start = data_inicial, end = data_final)['Close'].round(2)
        if ticker == 'S&P500':
            retornos = yf.download('^GSPC', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            cotacao = yf.download('^GSPC', start = data_inicial, end = data_final)['Close'].round(2)
        if ticker == 'NASDAQ':
            retornos = yf.download('^IXIC', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            cotacao = yf.download('^IXIC', start = data_inicial, end = data_final)['Close'].round(2)
    else:   
        retornos = yf.download(ticker, start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
        cotacao = yf.download(ticker, start = data_inicial, end = data_final)['Close'].round(2)
    
    #Gráfico
    st.line_chart(cotacao)
    
    #Matriz de retornos
    retorno_mensal = retornos.groupby([retornos.index.year.rename('Year'), retornos.index.month.rename('Month')]).mean()

    tabela_retornos = pd.DataFrame(retorno_mensal)
    tabela_retornos = pd.pivot_table(tabela_retornos, values='Close', index = 'Year', columns = 'Month')
    tabela_retornos.columns = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    #Mapa de calor
    fig, ax = plt.subplots(figsize = (12, 9))
    color = sns.color_palette('RdYlGn', 10)
    sns.heatmap(tabela_retornos, cmap = color, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02,
                cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax)
    ax.set_title(ticker, fontsize = 18)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '12')
    ax.set_xticklabels(ax.get_xticklabels(), fontsize = '12')
    ax.xaxis.tick_top()
    plt.ylabel('')
    st.pyplot(fig)
    
    #Análises estatísticas
    stats = pd.DataFrame(tabela_retornos.mean(), columns = ['Média'])
    stats['Mediana'] = tabela_retornos.median()
    stats['Maior'] = tabela_retornos.max()
    stats['Menor'] = tabela_retornos.min()
    stats['Positivos'] = tabela_retornos.gt(0).sum()/tabela_retornos.count()
    stats['Negativos'] = tabela_retornos.le(0).sum()/tabela_retornos.count()
    
    #Mapa de calor
    stats_a = stats[['Média', 'Mediana', 'Maior', 'Menor']]
    stats_a = stats_a.transpose()
    
    fig, ax = plt.subplots(figsize = (12, 6))
    sns.heatmap(stats_a, cmap = color, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02, 
                cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '12')
    st.pyplot(fig)  
    
    stats_b = stats[['Positivos', 'Negativos']]
    stats_b = stats_b.transpose()
    
    fig, ax = plt.subplots(figsize = (12, 3))
    sns.heatmap(stats_b, annot = True, fmt = '.2%', center = 0, vmax = 0.02, vmin = -0.02,
                cbar = False, linewidths = 1, xticklabels = True, yticklabels = True, ax = ax)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, verticalalignment = 'center', fontsize = '12')
    st.pyplot(fig)
    