import streamlit as st
import zipfile
import io
import requests
import pandas as pd
from datetime import date
from datetime import timedelta

def ultimo_dia_util_mes_anterior(data):
    # Subtrai um mês da data fornecida
    primeiro_dia_do_mes = data.replace(day=1)
    ultimo_dia_do_mes_anterior = primeiro_dia_do_mes - timedelta(days=1)
    
    # Verifica se é um dia útil (segunda a sexta-feira)
    while ultimo_dia_do_mes_anterior.weekday() >= 5:  # 5 e 6 representam sábado e domingo
        ultimo_dia_do_mes_anterior -= timedelta(days=1)
    
    return ultimo_dia_do_mes_anterior

def coleta_informes(data_mes):
    arquivo = f'inf_diario_fi_{data_mes}.csv'
    link = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{data_mes}.zip'
    r = requests.get(link)

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    arquivo_fi = zf.open(arquivo)

    linhas = arquivo_fi.readlines()
    linhas = [i.strip().decode('ISO-8859-1') for i in linhas]
    linhas = [i.split(';') for i in linhas]

    df = pd.DataFrame(linhas, columns = linhas[0])
    
    df = df[1:].reset_index()
    df[['VL_TOTAL', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST']] = df[['VL_TOTAL', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST']].apply(pd.to_numeric)

    return df


st.set_page_config(page_title='Mapa de Fundos de Investimentos',
                    page_icon='🪙',
                    layout='wide')

st.title('Mapa de Fundos de Investimentos')
st.markdown('---')

try:
    col1, col2, col3 = st.columns(3)
    with col1:
        data = st.date_input('Selecione uma data', value=date.today(), format='DD/MM/YYYY')
        ult_dia_ant = ultimo_dia_util_mes_anterior(data)
        data_mes = ult_dia_ant.strftime('%Y%m%d').replace('-','')[:-2]
        data_str = str(ult_dia_ant)
        
    with col2:
        qtd_fundos = st.slider('Quantidade de fundos para visualizar', min_value=1, max_value=100, value=15, step=1)
        
    with col3:
        nome_fundo = st.text_input('Pesquise pelo nome do fundo').upper()
        
        url = "http://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
        cadastral = pd.read_csv(url, sep = ';', encoding = 'ISO-8859-1')

        df_cadastral = cadastral.dropna(subset=['GESTOR', 'CLASSE_ANBIMA', 'CLASSE'])
        
        pl_fundos = df_cadastral[['DENOM_SOCIAL', 'VL_PATRIM_LIQ', 'CLASSE', 'PUBLICO_ALVO', 'TAXA_ADM', 'TAXA_PERFM', 'GESTOR', 'CNPJ_FUNDO', 'SIT']]
        pl_fundos = pl_fundos[pl_fundos['SIT'] == 'EM FUNCIONAMENTO NORMAL']
        pl_fundos = pl_fundos.sort_values('VL_PATRIM_LIQ', ascending=False).head(qtd_fundos)

    tab1, tab2, tab3 = st.tabs(['Fundos com maior PL', 'Fundos filtrados por nome', 'Fundos filtrados por gestora'])
    with tab1:
        st.write('Fundos com maior PL')
        pl_fundos
    with tab2:
        fundos_filtro_nome = df_cadastral[df_cadastral['DENOM_SOCIAL'].str.contains(nome_fundo)]
        fundos_filtro_nome
    with tab3:
        st.write('Fundos Filtrados por Gestora')

        gestor = st.selectbox('Selecione a gestora', df_cadastral['GESTOR'].unique())
        df_filtro_gestor = df_cadastral[df_cadastral['GESTOR'] == gestor]
        classe = st.selectbox('Selecione a classe', df_filtro_gestor['CLASSE'].unique())
        df_filtrado = df_filtro_gestor[df_filtro_gestor['CLASSE'] == classe]

        st.write("Fundos Disponíveis:")
        st.dataframe(df_filtrado)

except:
    st.error('Ocorreu algum erro, tente atualizar ou alterar as informações para coleta.')