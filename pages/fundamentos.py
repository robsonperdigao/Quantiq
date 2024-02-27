import streamlit as st
from src import utils


st.set_page_config(page_title='Fundamentos', 
                   page_icon='📊',
                   layout='wide')
st.title('Fundamentos')
st.markdown('---')

       
lista_tickers = utils.lista_ativos_b3()

col1, col2 = st.columns(2)

with col1:
    with st.form('ativo'):
        ativo = st.selectbox('Selecione o Papel', lista_tickers)
        
        submited = st.form_submit_button('Ver dados fundamentalistas')
        if submited:
            info_papel = utils.detalhes_ativo_summary(ativo)
            utils.detalhes_ativo(info_papel)

