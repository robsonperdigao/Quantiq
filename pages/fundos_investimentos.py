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

st.set_page_config(page_title='Mapa de Fundos de Investimentos',
                    page_icon='🪙',
                    layout='wide')

st.title('Mapa de Fundos de Investimentos')

data = st.date_input('Selecione uma data', value=date.today(), format='DD/MM/YYYY')
ult_dia_ant = ultimo_dia_util_mes_anterior(data)
data_mes = ult_dia_ant.strftime('%Y%m%d').replace('-','')[:-2]
data_str = str(ult_dia_ant)

arquivo = f'inf_diario_fi_{data_mes}.csv'
link = f'https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{data_mes}.zip'
r = requests.get(link)

zf = zipfile.ZipFile(io.BytesIO(r.content))
arquivo_fi = zf.open(arquivo)

linhas = arquivo_fi.readlines()
linhas = [i.strip().decode('ISO-8859-1') for i in linhas]
linhas = [i.split(';') for i in linhas]

df = pd.DataFrame(linhas, columns = linhas[0])

informes_diarios = df[1:].reset_index()
informes_diarios[['VL_TOTAL', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST']] = informes_diarios[['VL_TOTAL', 'VL_QUOTA', 'VL_PATRIM_LIQ', 'CAPTC_DIA', 'RESG_DIA', 'NR_COTST']].apply(pd.to_numeric)

comparativo = informes_diarios[informes_diarios['DT_COMPTC'] == data_str]
comparativo = comparativo.sort_values('VL_PATRIM_LIQ', ascending=False)


url = "http://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
cadastral = pd.read_csv(url, sep = ';', encoding = 'ISO-8859-1')

df = cadastral.dropna(subset=['GESTOR', 'CLASSE_ANBIMA', 'CLASSE'])
#lista_gestoras = list(df['GESTOR'].unique())
gestor = st.selectbox('Selecione a gestora', df['GESTOR'].unique())
df_filtrado_por_gestor = df[df['GESTOR'] == gestor]
#lista_classe = list(df['CLASSE_ANBIMA'].unique())
classe = st.selectbox('Selecione a classe', df_filtrado_por_gestor['CLASSE'].unique())
df_filtrado_por_classe = df_filtrado_por_gestor[df_filtrado_por_gestor['CLASSE'] == classe]

# Mostrar os fundos disponíveis com base nas seleções
st.write("Fundos Disponíveis:")
st.dataframe(df_filtrado_por_classe)

