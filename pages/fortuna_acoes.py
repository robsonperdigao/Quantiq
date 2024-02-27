import streamlit as st
from src import utils


st.set_page_config(page_title='Faça Fortuna com Ações - Décio Bazin',
                    page_icon='🎯',
                    layout='wide')

st.title('Faça Fortuna com Ações - Décio Bazin')
st.write('''Baseado no livro "Faça fortuna com ações antes que seja tarde", Décio Bazin descreve sua trajetória, histórias e como escolher boas empresas para se investir. 
No livro, o autor ensina que comprar uma ação é como comprar a fração de uma empresa. Dessa forma, ele ensina quais critérios observar em uma empresa, como dividendos acima de 6%, baixo endividamento e estar fora de escândalos.''')
st.write('***Lembrando que os ativos aqui listados não são recomendação de investimentos.***')
st.markdown('---')

col1, col2, col3, col4 = st.columns(4)
with col1:
    dy = st.number_input('Qual o Dividend Yield mínimo anual?', min_value=0.0, max_value=20.0, value=6.0, step=0.1)
with col2:
    liquidez = st.slider('Qual a liquidez mínima desejada? (Ideal maior que 1.000.000)', 100000, 5000000, value=1000000, step=100000)
with col3:
    divida = st.slider('Qual o grau de endividamento máximo?', max_value=5.0, value=2.0, step=0.1)
with col4:
    qtd = st.slider('Quantidade de ativos para mostrar', min_value=3, max_value=50, value=12, step=1)

botao = st.button('Botão do Bazin')

if botao:
    with st.spinner('Gerando a lista com as melhores empresas do Método Bazin...'):
        empresas = utils.ativos_fundamentus()
        empresas = empresas[['Papel', 'Cotação', 'Div.Yield', 'Liq.2meses', 'Dív.Brut/ Patrim.']]
        empresas = empresas.set_index('Papel')
        empresas = empresas[empresas['Liq.2meses'] > liquidez]
        empresas = empresas[empresas['Dív.Brut/ Patrim.'] < divida]
        empresas = empresas[empresas['Div.Yield'] > dy]
        empresas = empresas.sort_values('Div.Yield', ascending=False)
        st.dataframe(empresas.head(qtd))
        