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

