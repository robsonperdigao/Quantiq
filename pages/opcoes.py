import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import datetime as dt
from datetime import date, datetime
import datetime as dt
from workadays import workdays as wd

# Lista as empresas da B3
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

# Coleta as opções com data de vencimento específica
def opt_venc(ativo, vencimento):
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={ativo}&listarVencimentos=false&cotacoes=true&vencimentos={vencimento}'
    r = requests.get(url).json()
    x = ([ativo, vencimento, i[0].split('_')[0], i[2], i[3], i[5], i[8], i[9], i[10], i[11]] for i in r['data']['cotacoesOpcoes'])
    df = pd.DataFrame(x, columns=['ativo', 'vencimento', 'ticker', 'tipo', 'modelo', 'strike', 'preco', 'negocios', 'volume', 'data ult'])
    return df

# Coleta as opções com todos os vencimentos
def opt_all(ativo):
    url = f'https://opcoes.net.br/listaopcoes/completa?idLista=ML&idAcao={ativo}&listarVencimentos=true&cotacoes=true'
    r = requests.get(url).json()
    vencimentos = [i['value'] for i in r['data']['vencimentos']]
    df = pd.concat([opt_venc(ativo, vencimento) for vencimento in vencimentos])
    return df

# Operação - Collar de Alta
def collar_alta(ativo, vencimento, quantidade = 1, volume_put = 0.01, negocios_put = 1, volume_call = 0.01, negocios_call = 1):
    # Coleta selic anual direto pelo BC
    url_selic = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json'
    selic = pd.read_json(url_selic)
    selic['data'] = pd.to_datetime(selic['data'], dayfirst=True)
    selic.set_index('data', inplace=True)
    selic = float(selic.iloc[-1].values)

    # Calcula a quantidade de dias úteis e o rendimento do CDI até o vencimento
    data_hoje = dt.date.today()
    dias_uteis = wd.networkdays(data_hoje, vencimento, country='BR')
    cdi_operacao = round(((1 + selic / 100) ** (dias_uteis / 252) - 1) * 100, 2)
    
    # Coleta o preço do ativo com base no último fechamento
    preco_ativo = round(yf.download(ativo +'.SA', period='1d')['Adj Close'].iloc[-1], 2)
    
    # Coleta as opções disponíveis para o ativo com base no vencimento determinado
    df = opt_venc(ativo, vencimento)
    
    # Cria um dataframe somente com as PUTs
    df_put = df[df['tipo'] == 'PUT']

    # Cria um dataframe somente com as CALLs e renomeia colunas para diferenciar
    df_call = df[df['tipo'] == 'CALL']
    df_call_op = df_call.copy()
    df_call_op.drop(columns=['vencimento'], inplace=True)
    df_call_op.rename(columns={
        'ticker': 'ticker_call',
        'tipo': 'tipo_call',
        'modelo': 'modelo_call',
        'strike': 'strike_call', 
        'preco': 'preco_call',
        'negocios': 'negocios_call',
        'volume': 'volume_call',
        'data ult': 'data ult_call'
    }, inplace=True)

    # Cria um dataframe com as operações possíveis para cada PUT
    df = pd.merge(df_put, df_call_op, on='ativo', suffixes=('', '_call'))
    df = df[df['strike'] > preco_ativo]
    df['preco ativo'] = preco_ativo
    df['custo'] = (df['preco'] - df['preco_call'] + preco_ativo) * quantidade
    df['cdi oper'] = cdi_operacao
    df['lucro minimo'] = df['strike'] * quantidade - df['custo']
    df['lucro min pct'] = round(df['lucro minimo'] / df['custo'] * 100, 2)
    df['lucro maximo'] = df['strike_call'] * quantidade - df['custo']
    df['lucro max pct'] = round(df['lucro maximo'] / df['custo'] * 100, 2)
    
    # Filtra o dataframe somente com as operações lucrativas
    df_op = df.copy()
    df_op = df_op[df_op['lucro min pct'] >= cdi_operacao]
    df_op = df_op[df_op['lucro maximo'] > 0]
    df_op = df_op[df_op['strike_call'] > df_op['strike']]
    df_op = df_op[df_op['volume'] >= volume_put]
    df_op = df_op[df_op['negocios'] >= negocios_put]
    df_op = df_op[df_op['volume_call'] >= volume_call]
    df_op = df_op[df_op['negocios_call'] >= negocios_call]
    df_op = df_op.sort_values(by='lucro min pct',ascending=True)
    
    return df, df_put, df_call, df_op


st.set_page_config(page_title='Estratégias com Opções',
                   page_icon='❇️',
                   layout='wide')
st.title('Estratégias de Opções')

st.write('Selecione o ativo desejado e escolha a estrutura que pretende montar com opções e veja o resultado detalhado dos ativos.')
st.markdown('---')

col1, col2, col3, col4 = st.columns(4)
with col1:
    ativos = lista_empresas()
    ativos.append('BOVA11')
    ativo = st.selectbox('Selecione o ativo', ativos)
    volume_put = st.slider('Volume mínimo da PUT', 0.01, 9999999.00, 500.00)

with col2:
    vencimento = st.date_input('Data de vencimento das opções', format='DD/MM/YYYY')
    negocios_put = st.slider('Quantidade mínima de negócios da PUT', 1, 1000, 1, 1)

with col3:
    quantidade = st.number_input('Quantidade', min_value=1, step=1, value=100)
    volume_call = st.slider('Volume mínimo da CALL', 0.01, 9999999.00, 500.00)

with col4:
    estruturas = ['Collar de Alta', 'Collar de Baixa']
    estrutura = st.selectbox('Selecione a estrutura', estruturas)
    negocios_call = st.slider('Quantidade mínima de negócios da CALL', 1, 1000, 1, 1)

#button = st.button('Ver as estratégias')
st.write('')

#if button:
col1, col2, col3 = st.columns(3)
with col1:
    tabela = st.checkbox('Ver todas as operações')
with col2:
    put = st.checkbox('Ver tabela das PUTs')
with col3:
    call = st.checkbox('Ver tabela das CALLs')


with st.container():
    st.write('Lista de operações possíveis')
    if estrutura == 'Collar de Alta':
        df, df_put, df_call, df_op = collar_alta(ativo, vencimento, quantidade, volume_put, negocios_put, volume_call, negocios_call)
        if len(df) == 0:
            st.write('Não há estratégias disponíveis')
        else:
            st.dataframe(df_op)

            with st.container():
                if tabela:
                    st.write('Tabela com todas as operações para o ativo')
                    st.dataframe(df)
                if put:
                    st.write('Tabela com todas as PUTs do ativo')
                    st.dataframe(df_put)
                if call:
                    st.write('Tabela com todas as CALLs do ativo')
                    st.dataframe(df_call)

st.markdown('---')