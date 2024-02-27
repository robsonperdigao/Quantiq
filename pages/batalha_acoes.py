import streamlit as st
import pandas as pd
from src import utils

st.set_page_config(page_title='Batalha de Ações', 
                   page_icon='🥊',
                   layout='wide')
st.title('Batalha de Ações')
st.markdown('---')


setores = utils.lista_setores()
setor = st.selectbox('Selecione o setor', setores.values(), placeholder='Digite ou selecione o setor')
for key, value in setores.items():
    if setor == value:
        num_setor = key

lista_tickers = utils.lista_ativos_setores_b3(num_setor)

col1, col2 = st.columns(2)

with st.form('batalha'):
    submited = st.form_submit_button("It's tiiiiime!")
    with col1:
            ativo1 = st.selectbox('Selecione o Desafiador', lista_tickers, key='ativo1')
    with col2:
            ativo2 = st.selectbox('Selecione o Desafiado', lista_tickers, key='ativo2')

    if submited:
        with col1:
            info_papel1 = utils.detalhes_ativo_summary(ativo1)
            utils.detalhes_ativo(info_papel1)

        with col2:
            info_papel2 = utils.detalhes_ativo_summary(ativo2)
            utils.detalhes_ativo(info_papel2)

        df = pd.merge(info_papel1, info_papel2, how='outer')
        st.dataframe(df)
        colunas_menor = ['PL', 'PVP', 'PEBIT', 'PSR', 'PAtivos', 'PCap_Giro', 'PAtiv_Circ_Liq',
                         'EV_EBITDA', 'EV_EBIT', 'VPA', 'Liquidez_Corr', 'Div_Br_Patrim', 'Giro_Ativos']
        colunas_maior = ['Div_Yield', 'Cres_Rec_5a', 'LPA', 'Marg_Bruta', 'Marg_EBIT', 'Marg_Liquida',
                         'EBIT_Ativo', 'ROIC', 'ROE']
        df_comparativo = df.copy()
        df_comparativo['Resultado'] = 0
        for coluna in colunas_menor:
             comparacao = df_comparativo[coluna]
