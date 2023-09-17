import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title='Magic Formula', page_icon='🎯')
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