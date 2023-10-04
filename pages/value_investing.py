import streamlit as st
import fundamentus as fd
import requests
import pandas as pd

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


st.set_page_config(page_title='Value Investing',
                    page_icon='🔎',
                    layout='wide')

st.title('Value Investing')
st.write("""A Fórmula de Graham, também apelidada como "Modelo de Graham", é uma fórmula desenvolvida por Benjamin Graham, considerado o "pai do investimento em valor" e mentor de Warren Buffett.""")
st.write("""Essa fórmula foi apresentada em seu livro clássico de investimentos, "Security Analysis," coescrito com David Dodd, e posteriormente abordada em seu clássico livro "O investidor inteligente.""")
st.write("""O objetivo é identificar ações que são negociadas a preços significativamente abaixo de seu valor intrínseco, proporcionando uma margem de segurança para os investidores. A abordagem de investimento de Graham enfatiza a compra de ativos subvalorizados e a gestão de risco.""")
st.write("""A fórmula proposta por Graham é a seguinte:""")
st.latex("""VI = √(22,5 x LPA x VPA)""")
st.write("""O valor de "22,5" corresponde ao Índice de Graham, que equivale à multiplicação de P/L (Preço / Lucro) e P/VP (Preço / Valor Patrimonial) e, segundo Graham, os valores ideais de P/L é 15 e P/VP é 1,5.""")
st.write("""Abaixo você pode escolher os valores ideais de P/L e P/VP de acordo com cada empresa e em seguida selecionar a empresa para visualizar o Valor Intrínseco da Ação.""")
st.write("""**Não é recomendação de investimento, utilize as informações aqui para seus estudos e conta em risco**""")
st.markdown('---')


col1, col2 = st.columns(2)
with col1:
    pl = st.slider('Escolha o P/L ideal', value=15.0, max_value=50.0, step=0.5)
with col2:
    pvp = st.slider('Escolha o P/VP ideal', value=1.5, max_value=30.0, step=0.5)
indice = pl * pvp

st.metric('Índice de Graham', f'{indice:.2f}')
st.markdown('---')


ativos = lista_empresas()
ativo = st.selectbox('Selecione o ativo', ativos, index=789)

dados_ativo = fd.get_detalhes_papel(ativo)
for coluna in ['Cotacao', 'PL', 'PVP', 'LPA', 'VPA']:
        dados_ativo[coluna] = dados_ativo[coluna].str.replace('.', '')
        dados_ativo[coluna] = dados_ativo[coluna].str.replace(',', '.')
        dados_ativo[coluna] = dados_ativo[coluna].str.rstrip('%').astype('float') / 100
dados_ativo = dados_ativo[['Cotacao', 'PL', 'PVP', 'LPA', 'VPA']]

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
cotacao = float(dados_ativo['Cotacao'])
pl_ativo = float(dados_ativo['PL'])
pvp_ativo = float(dados_ativo['PVP'])
lpa = float(dados_ativo['LPA'])
vpa = float(dados_ativo['VPA'])
indice_graham_ativo = round(pl_ativo * pvp_ativo, 2)
valor_intrinseco = round((indice * lpa * vpa) ** (1 / 2), 2)

with col1:
    st.metric(f'P/L de {ativo}', pl_ativo)
with col2:
    st.metric(f'P/VP de {ativo}', pvp_ativo)
with col3:
    st.metric(f'Índice de Graham de {ativo}', indice_graham_ativo)
with col4:
    st.metric(f'LPA de {ativo}', f'R$ {lpa}')
with col5:
    st.metric(f'VPA de {ativo}', f'R$ {vpa}')
with col6:
    st.metric(f'Cotação atual de {ativo}', f'R$ {cotacao}')    
with col7:
    st.metric(f'Valor Intrínseco de {ativo}', f'R$ {valor_intrinseco}', f'{(valor_intrinseco/cotacao-1)*100:.2f}%')

