import streamlit as st
import fundamentus as fd
import quantstats as qs
from datetime import datetime, timedelta
import pandas as pd
from src import utils


def periodo_analise(data):
    data_atual = datetime.now().strftime("%Y-%m-%d")

    data = datetime.strptime(str(data), "%Y-%m-%d")
    data_atual = datetime.strptime(data_atual, "%Y-%m-%d")

    intervalo_datas = pd.date_range(data, data_atual)

    dias = len(intervalo_datas[(intervalo_datas.dayofweek < 5)])
    return f'{dias}d'


st.set_page_config(page_title='Análise de Carteira',
                    page_icon='📈',
                    layout='wide')

st.title('Análise de Carteira')
st.write('Em desenvolvimento')
st.markdown('---')

qs.extend_pandas()
benchmark_dict = {'Ibovespa': '^BVSP', 
                'CDI': 'CDI',
                'Dólar': 'Dólar'}

periodo_dict = {'3 meses': '3mo',
                '6 meses': '6mo',
                '1 ano': '1y',
                '2 anos': '2y',
                '3 anos': '3y',
                '5 anos': '5y',
                'Desde início': 'max'}

tab1, tab2 = st.tabs(['Ativo único', 'Carteira'])
with tab1:
    acao = st.selectbox('Ativo da carteira', [i + '.SA' for i in utils.lista_ativos_b3()], placeholder='Digite o nome da ação')
    benchmark = benchmark_dict[st.selectbox('Selecione o Benchmark', benchmark_dict.keys())]
    periodo = periodo_dict[st.selectbox('Selecione o período de análise', periodo_dict.keys())]
    carteira = qs.utils.download_returns(acao)
    carteira
    col1, col2, col3, col4 = st.columns(4)
    
        
        
with tab2:
    acoes= st.multiselect('Ativo da carteira', [i + '.SA' for i in utils.lista_ativos_b3()], placeholder='Digite o nome da ação')
    portfolio = {}
    for acao in acoes:
        portfolio[acao] = 1/len(acoes)
    portfolio

    

    benchmark = benchmark_dict[st.selectbox('Selecione o Benchmark', benchmark_dict.keys())]

    periodo = periodo_dict[st.selectbox('Selecione o período de análise', periodo_dict.keys())]