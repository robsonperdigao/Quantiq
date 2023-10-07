import streamlit as st
import fundamentus as fd
import quantstats as qs

st.set_page_config(page_title='Análise de Carteira',
                    page_icon='📈',
                    layout='wide')

st.title('Análise de Carteira')

acoes = st.multiselect('Ações', [i + '.SA' for i in fd.list_papel_all()])

benchmark = ['CDI', 'IBOV']

carteira = qs.utils.make_index(acoes)

col1, col2, col3, col4 = st.columns(4)
with col1:
    carteira
