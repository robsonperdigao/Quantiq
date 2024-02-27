import streamlit as st
import pandas as pd
from src import utils

st.set_page_config(page_title='Análise Setorial de Ações',
                    page_icon='🗄️',
                    layout='wide')
st.title('Análise Setorial de Ações')
st.markdown('---')


setores = utils.lista_setores()
setor = st.selectbox('Selecione o setor', setores.values(), index=None, placeholder='Digite ou selecione o setor')
for key, value in setores.items():
     if setor == value:
        num_setor = key

lista_tickers = utils.lista_ativos_setores_b3(num_setor)


botao = st.button('Coletar Dados')
if botao:
    dados_acoes = []
    for acao in lista_tickers:
        info_papel = utils.detalhes_ativo_summary(acao)
        dados_acoes.append(info_papel)
    
    df = pd.concat(dados_acoes, axis=0, ignore_index=True)
    for coluna in ['Data_ult_cot', 'Ult_balanco_processado']:
        df[coluna] = pd.to_datetime(df[coluna], format='%Y-%m-%d', errors='coerce').dt.date

    df
    st.write(df.dtypes)
