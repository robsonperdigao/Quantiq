import streamlit as st
import pandas as pd
import yfinance as yf
import investpy as inv
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date
import plotly.graph_objects as go
import requests
import fundamentus as fd

#Obtém a lista com as empresas listadas na B3
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

#Home
def home():
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown('---')
        st.image('QUANTIQ.png')
        st.markdown('---')
    st.write('Escolha a opção no menu ao lado')
        
#Panorama do Mercado
def panorama():
    st.title('Panorama do Mercado')
    st.markdown(date.today().strftime('%d/%m/%Y'))
    
    #Mercaod pelo mundo
    st.subheader('Mercados pelo Mundo')
    
    dict_tickers = {'Bovespa': '^BVSP',
                    'Dólar': 'USDBRL=X',
                    'S&P500': '^GSPC',
                    'NASDAQ': '^IXIC',
                    'Bitcoin': 'BTC-USD',
                    'Ethereum': 'ETH-USD'}
    df_info = pd.DataFrame({'Ativo': dict_tickers.keys(), 'Ticker': dict_tickers.values()})
    df_info['Últ. Valor'] = ''
    df_info['%'] = ''
    count = 0
    with st.spinner('Baixando cotações...'):
        for ticker in dict_tickers.values():
            cotacoes = yf.download(ticker, period = '5d')['Adj Close']
            variacao = ((cotacoes.iloc[-1]/cotacoes.iloc[-2])-1)*100
            df_info['Últ. Valor'][count] = round(cotacoes.iloc[-1],2)
            df_info['%'][count] = round(variacao, 2)
            count += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(df_info['Ativo'][0], value=str(df_info['Últ. Valor'][0]) + 'pts', delta=str(df_info['%'][0]) + '%')
        st.metric(df_info['Ativo'][1], value= 'R$ '+ str(df_info['Últ. Valor'][1]), delta=str(df_info['%'][1]) + '%')
    with col2:
        st.metric(df_info['Ativo'][2], value=str(df_info['Últ. Valor'][2]) + 'pts', delta=str(df_info['%'][2]) + '%')
        st.metric(df_info['Ativo'][3], value=str(df_info['Últ. Valor'][3]) + 'pts', delta=str(df_info['%'][3]) + '%')
    with col3:
        st.metric(df_info['Ativo'][4], value= 'US$ '+ str(df_info['Últ. Valor'][4]), delta=str(df_info['%'][4]) + '%')
        st.metric(df_info['Ativo'][5], value= 'US$ '+ str(df_info['Últ. Valor'][5]), delta=str(df_info['%'][5]) + '%')

    #Destaques do dia
    st.markdown('---')
    st.subheader('Destaques do dia')
    lista_indices = ['IBOV', 'Dólar', 'S&P500', 'NASDAQ']
    indice = st.selectbox('Selecione', lista_indices)

    if indice == 'IBOV':
        indice_diario = yf.download('^BVSP', period = '1mo', interval = '1d')
    if indice == 'Dólar':
        indice_diario = yf.download('USDBRL=X', period = '1mo', interval = '1d')
    if indice == 'S&P500':
        indice_diario = yf.download('^GSPC', period = '1mo', interval = '1d')
    if indice == 'NASDAQ':
        indice_diario = yf.download('^IXIC', period = '1mo', interval = '1d')
    
    fig = go.Figure(data=[go.Candlestick(x = indice_diario.index,
                                        open = indice_diario['Open'],
                                        high = indice_diario['High'],
                                        low = indice_diario['Low'],
                                        close = indice_diario['Close'])]) 
    fig.update_layout(title = indice, xaxis_rangeslider_visible = False)
    st.plotly_chart(fig) 
    
    lista_acoes =  [i + '.SA' for i in lista_empresas()]
    acao = st.selectbox('Selecione', lista_acoes, index = 333)
    hist_acao = yf.download(acao, period = '1mo', interval = '1d', auto_adjust=True)
    
    fig = go.Figure(data=[go.Candlestick(x = hist_acao.index,
                                        open = hist_acao['Open'],
                                        high = hist_acao['High'],
                                        low = hist_acao['Low'],
                                        close = hist_acao['Close'])]) 
    fig.update_layout(title = acao, xaxis_rangeslider_visible = False)
    st.plotly_chart(fig) 
 
#Mapa Mensal    
def mapa_mensal():
    st.title('Mapa Mensal')
    
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
            if ticker == 'Dólar':
                retornos = yf.download('USDBRL=X', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            if ticker == 'S&P500':
                retornos = yf.download('^GSPC', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
            if ticker == 'NASDAQ':
                retornos = yf.download('^IXIC', start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
        else:
            retornos = yf.download(ticker, start = data_inicial, end = data_final, interval = '1mo')['Close'].pct_change()
        
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
        
#Análise Fundamentalista    
def fundamentos():
    st.title('Análise Fundamentalista')
    
    lista_tickers = fd.list_papel_all()
    comparar = st.checkbox('Comparar 2 ativos')
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander('', expanded=True):
            papel1 = st.selectbox('Selecione o Papel', lista_tickers)
            info_papel1 = fd.get_detalhes_papel(papel1)
            st.write('**Empresa:**', info_papel1['Empresa'][0])
            st.write('**Setor:**', info_papel1['Setor'][0])
            st.write('**Segmento:**', info_papel1['Subsetor'][0])
            st.write('**Valor de Mercado:**', f"R$ {info_papel1['Valor_de_mercado'][0]:,.2f}")
            st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel1['Patrim_Liq'][0]):,.2f}")
            st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel1['Receita_Liquida_12m'][0]):,.2f}")
            st.write('**Dívida Bruta:**', f"R$ {float(info_papel1['Div_Bruta'][0]):,.2f}")
            st.write('**Dívida Líquida:**', f"R$ {float(info_papel1['Div_Liquida'][0]):,.2f}")
            st.write('**P/L:**', f"{float(info_papel1['PL'][0]):,.2f}")
            st.write('**Dividend Yield:**', f"{info_papel1['Div_Yield'][0]}")
    
    if comparar:
        with col2:
            with st.expander('', expanded=True):
                papel2 = st.selectbox('Selecione o 2º Papel', lista_tickers)
                info_papel2 = fd.get_detalhes_papel(papel2)
                st.write('**Empresa:**', info_papel2['Empresa'][0])
                st.write('**Setor:**', info_papel2['Setor'][0])
                st.write('**Segmento:**', info_papel2['Subsetor'][0])
                st.write('**Valor de Mercado:**', f"R$ {info_papel2['Valor_de_mercado'][0]:,.2f}")
                st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel2['Patrim_Liq'][0]):,.2f}")
                st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel2['Receita_Liquida_12m'][0]):,.2f}")
                st.write('**Dívida Bruta:**', f"R$ {float(info_papel2['Div_Bruta'][0]):,.2f}")
                st.write('**Dívida Líquida:**', f"R$ {float(info_papel2['Div_Liquida'][0]):,.2f}")
                st.write('**P/L:**', f"{float(info_papel2['PL'][0]):,.2f}")
                st.write('**Dividend Yield:**', f"{info_papel2['Div_Yield'][0]}")   
    
#Magic Formula
def magic_formula():
    st.title('Magic Formula')
    liquidez = st.slider('Qual a liquidez mínima desejada? (Ideal maior que 1.000.000)', 100000, 5000000, value=1000000, step=100000)
    qtd_ativos = st.slider('Quantos ativos você deseja no Ranking Final?', 3, 30, value=15)
    botao = st.button('Botão Mágico')
    
    if botao:
        with st.spinner('Gerando o ranking da Magic Formula...'):    
            url = 'http://www.fundamentus.com.br/resultado.php'
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
            r = requests.get(url, headers=header)
            tabela = pd.read_html(r.text,  decimal=',', thousands='.')[0]
            
            for coluna in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
                tabela[coluna] = tabela[coluna].str.replace('.', '')
                tabela[coluna] = tabela[coluna].str.replace(',', '.')
                tabela[coluna] = tabela[coluna].str.rstrip('%').astype('float') / 100
            
            
            tabela = tabela[['Papel', 'Cotação', 'EV/EBIT', 'ROIC', 'Liq.2meses', 'P/L']]
            tabela['Empresa'] = tabela['Papel'].str[:4]
            tabela = tabela.drop_duplicates(subset='Empresa')
            tabela = tabela.set_index('Papel')
            tabela = tabela[tabela['Liq.2meses'] > liquidez]
            tabela = tabela[tabela['P/L'] > 0]
            tabela = tabela[tabela['EV/EBIT'] > 0]
            tabela = tabela[tabela['ROIC'] > 0]
            tabela = tabela.drop(columns = ['Empresa', 'P/L', 'Liq.2meses'])
            tabela['RANKING_EV/EBIT'] = tabela['EV/EBIT'].rank(ascending = True)
            tabela['RANKING_ROIC'] = tabela['ROIC'].rank(ascending = False)
            tabela['RANKING_TOTAL'] = tabela['RANKING_EV/EBIT'] + tabela['RANKING_ROIC']
            tabela = tabela.sort_values('RANKING_TOTAL')
            tabela = tabela.head(qtd_ativos)
                
            ranking = tabela.index
            ranking = '\n'.join(f'{i+1}. {acao}' for i, acao in enumerate(ranking))
            st.markdown('**Ranking final da Magic Formula:**')
            st.write(ranking)
    
def main():
    st.set_page_config(page_title='Robson Perdigão - Quantiq Finanças Quantitativas',
                       page_icon='📈',
                       initial_sidebar_state='expanded')
    st.sidebar.image('QUANTIQ.png')
    st.sidebar.markdown('---')
    
    col1, col2, col3, col4 = st.columns(4)
    st.markdown('---')
    with col1:
        st.image('QUANTIQ.png')

    with col2:
        st.markdown('# Robson Perdigão')
        st.markdown('## Assessor de Investimentos')
        st.write('InvestSmart')
    st.write("""Me chamo Robson Perdigão, sou Assessor de Investimentos na InvestSmart.
                 Investidor desde 2012, trader desde 2018 e Assessor desde 2020.
                 2023 foi o ano para entrar no mundo das Finanças Quantitativas com o objetivo de melhorar a performance dos meus investimentos e auxiliar os investidores a tomar melhores decisões.""")
    st.write('Escolha a opção no menu ao lado')
   

main()
