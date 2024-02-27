import streamlit as st
from datetime import date
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from src import utils


st.set_page_config(page_title='Panorama de Mercado', 
                   page_icon='📰',
                   layout='wide')
st.title('Panorama do Mercado')
st.markdown('---')


st.markdown(date.today().strftime('%d/%m/%Y'))

#Mercados pelo mundo
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

lista_acoes =  [i + '.SA' for i in utils.lista_ativos_b3()]
acao = st.selectbox('Selecione', lista_acoes, index = 33)
hist_acao = yf.download(acao, period = '1mo', interval = '1d', auto_adjust=True)

fig = go.Figure(data=[go.Candlestick(x = hist_acao.index,
                                    open = hist_acao['Open'],
                                    high = hist_acao['High'],
                                    low = hist_acao['Low'],
                                    close = hist_acao['Close'])]) 
fig.update_layout(title = acao, xaxis_rangeslider_visible = False)
st.plotly_chart(fig) 
