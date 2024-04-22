import streamlit as st
from st_pages import Page, Section, show_pages, add_indentation
import pandas as pd
import yfinance as yf

def mercados_mundo():
    #st.subheader('Mercados pelo Mundo')

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


st.set_page_config(page_title='Quantiq Trade - Finanças Quantitativas',
                    page_icon='📈',
                    initial_sidebar_state='expanded',
                    layout='wide')
#add_indentation()

# Organização das páginas para aparecer na barra lateral
show_pages(
    [
        Page('home.py', 'Home', '🏠'),
        #Section("Planejamento", '📊'),
        Page('pages/planner.py', 'Planejamento Financeiro', '📊'),
        Page('pages/planner_ex.py', 'Exemplo Plan. Financeiro', '📝'),
        Page('pages/quant/analise_portfolio.py', 'Análise de Portfolio', '📈'),
        #Section("Quantiq", '💲'),
        Page('pages/opcoes.py', 'Estratégias com Opções', '❇️'),
        Page('pages/comparador_rentabilidade.py', 'Comparador de Rentabilidade', '🏅'),
        #Page('pages/quant/analise_setorial.py', 'Análise Setorial', '🗄️'),
        #Page('pages/quant/algotrading.py', 'Algotrading/Robô Trader', '🗄️'),
        #Page('pages/quant/factor_investing.py', 'Factor Investing', '🗄️'),
        #Page('pages/quant/quant_finance.py', 'Finanças Quantitativas', '🗄️'),
        Page('pages/calculadora.py', 'Calculadora Financeira', '🧮'),
        Page('pages/magic_formula.py', 'Magic Formula', '🪄'),
        Page('pages/value_investing.py', 'Ben Graham - Value Investing', '🔎'),
        Page('pages/fortuna_acoes.py', 'Método Bazin', '🎯'),
        Page('pages/fundos_investimentos.py', 'Mapa de Fundos de Investimentos', '🪙'),
        #Page('pages/quant/remuneracao.py', 'Remuneração', '🗄️'),
        Page('pages/fundamentos.py', 'Fundamentos', '📊'),
        Page('pages/batalha_acoes.py', 'Batalha de Ações', '🥊'),
        Page('pages/about.py', 'About', '🪪')
    ]
)

col1, col2, col3 = st.columns(3)
st.markdown('---')
        
with col2:
    st.image('img/QUANTIQ.png', use_column_width=True)
        
st.write("""A Quantiq Trade é uma empresa especializada em soluções financeiras. Nossos serviços abrangem análise quantitativa, estratégias automatizadas, pesquisa e modelagem de estratégias, consultoria financeira para investidores. 
            Oferecemos modelos de investimento avançados e consultoria financeira para auxiliar nossos clientes a tomar decisões embasadas e otimizar suas estratégias de investimento. Combinamos tecnologia com expertise financeira para fornecer soluções inovadoras e eficazes para as necessidades financeiras de nossos clientes.""")
st.write("Do desenvolvimento de modelos de investimento com machine learning à orientação estratégica, nosso nome reflete nossa busca incansável por resolver os desafios financeiros mais complexos de maneira inteligente e eficaz.")
#st.write("⬅️ Escolha uma opção no menu ao lado")
st.markdown('---')

mercados_mundo()

