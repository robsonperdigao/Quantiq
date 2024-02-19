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

# Coleta as opções com todos os vencimentos
def opt_all(ativo):
    url = f'https://opcoes.net.br/listaopcoes/completa?idLista=ML&idAcao={ativo}&listarVencimentos=true&cotacoes=true'
    r = requests.get(url).json()
    vencimentos = [i['value'] for i in r['data']['vencimentos']]
    df = pd.concat([coleta_opcoes(ativo, vencimento) for vencimento in vencimentos])
    return df

# Mostrar tabela de operações
def mostra_operacoes():
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
    return

def calcula_cdi(vencimento):
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
    return cdi_operacao

def coleta_opcoes(ativo, vencimento):
    # Coleta o preço do ativo com base no último fechamento
    preco_ativo = round(yf.download(ativo +'.SA', period='1d')['Adj Close'].iloc[-1], 2)
    
    # Coleta informações das opções
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={ativo}&listarVencimentos=false&cotacoes=true&vencimentos={vencimento}'
    r = requests.get(url).json()
    x = ([ativo, vencimento, i[0].split('_')[0], i[2], i[3], i[5], i[8], i[9], i[10], i[11]] for i in r['data']['cotacoesOpcoes'])
    df = pd.DataFrame(x, columns=['ativo', 'vencimento', 'ticker', 'tipo', 'modelo', 'strike', 'preco', 'negocios', 'volume', 'data ult'])
    df['data ult'] = df['data ult'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').date() if isinstance(x, str) else None)
    
    # Cria um dataframe somente com as PUTs
    df_put = df[df['tipo'] == 'PUT']
    df_put_op = df_put.copy()
    df_put_op.rename(columns={
        'ticker': 'ticker_put',
        'tipo': 'tipo_put',
        'modelo': 'modelo_put',
        'strike': 'strike_put', 
        'preco': 'preco_put',
        'negocios': 'negocios_put',
        'volume': 'volume_put',
        'data ult': 'data ult_put'
    }, inplace=True)

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
    df = pd.merge(df_put_op, df_call_op, on='ativo', suffixes=('', '_call'))
    df['preco ativo'] = preco_ativo
    
    return df, df_put, df_call, preco_ativo

# Operação - Collar de Alta
def collar_alta(ativo, vencimento, quantidade = 1, volume_put = 0.01, negocios_put = 1, volume_call = 0.01, 
                negocios_call = 1, filtro_data=None, risco = 0.00, corretagem_variavel = 0.00, corretagem_ordem = 0.00):
    # Calcula CDI da operação
    cdi_operacao = calcula_cdi(vencimento)
    
    # Coleta as opções disponíveis para o ativo com base no vencimento determinado
    df, df_put, df_call, preco_ativo = coleta_opcoes(ativo, vencimento)
    
    tx_b3 = 0.1340
    df['corretagem'] = ((preco_ativo + df['preco_put'] + df['preco_call']) * (corretagem_variavel + tx_b3)) + 6 * corretagem_ordem
    df['custo'] = ((df['preco_put'] - df['preco_call'] + preco_ativo) * quantidade) - df['corretagem']
    df['cdi oper'] = cdi_operacao
    df['lucro minimo'] = df['strike_put'] * quantidade - df['custo']
    df['lucro min pct'] = round(df['lucro minimo'] / df['custo'] * 100, 2)
    df['lucro maximo'] = df['strike_call'] * quantidade - df['custo']
    df['lucro max pct'] = round(df['lucro maximo'] / df['custo'] * 100, 2)
    
    # Filtra o dataframe somente com as operações lucrativas
    df_op = df.copy()
    df_op = df_op[df_op['lucro min pct'] >= risco]
    df_op = df_op[df_op['lucro maximo'] > 0]
    df_op = df_op[df_op['strike_put'] > preco_ativo]
    df_op = df_op[df_op['strike_call'] > df_op['strike_put']]
    df_op = df_op[df_op['volume_put'] >= volume_put]
    df_op = df_op[df_op['negocios_put'] >= negocios_put]
    df_op = df_op[df_op['volume_call'] >= volume_call]
    df_op = df_op[df_op['negocios_call'] >= negocios_call]
    df_op = df_op[df_op['data ult_put'] >= filtro_data]
    df_op = df_op[df_op['data ult_call'] >= filtro_data]
    df_op = df_op.sort_values(by='lucro min pct',ascending=True)
    
    return df, df_put, df_call, df_op

# Operação - Collar de Baixa
def collar_baixa(ativo, vencimento, quantidade = 1, volume_put = 0.01, negocios_put = 1, volume_call = 0.01, 
                 negocios_call = 1, filtro_data=None, risco = 0.00, corretagem_variavel = 0.00, corretagem_ordem = 0.00):
    # Calcula CDI da operação
    cdi_operacao = calcula_cdi(vencimento)
    
    # Coleta as opções disponíveis para o ativo com base no vencimento determinado
    df, df_put, df_call, preco_ativo = coleta_opcoes(ativo, vencimento)

    tx_b3 = 0.1340
    df['corretagem'] = ((preco_ativo + df['preco_put'] + df['preco_call']) * (corretagem_variavel + tx_b3)) + 6 * corretagem_ordem
    df['custo'] = (df['preco_put'] - df['preco_call'] + preco_ativo) * quantidade
    df['cdi oper'] = cdi_operacao
    df['lucro minimo'] = df['strike_call'] * quantidade - df['custo']
    df['lucro min pct'] = round(df['lucro minimo'] / df['custo'] * 100, 2)
    df['lucro maximo'] = df['strike_put'] * quantidade - df['custo']
    df['lucro max pct'] = round(df['lucro maximo'] / df['custo'] * 100, 2)
    
    # Filtra o dataframe somente com as operações lucrativas
    df_op = df.copy()
    df_op = df_op[df_op['lucro min pct'] >= risco]
    df_op = df_op[df_op['lucro maximo'] > 0]
    df_op = df_op[df_op['strike_put'] < preco_ativo + 2]
    df_op = df_op[df_op['strike_call'] < df_op['strike_put']]
    df_op = df_op[df_op['volume_put'] >= volume_put]
    df_op = df_op[df_op['negocios_put'] >= negocios_put]
    df_op = df_op[df_op['volume_call'] >= volume_call]
    df_op = df_op[df_op['negocios_call'] >= negocios_call]
    df_op = df_op[df_op['data ult_put'] >= filtro_data]
    df_op = df_op[df_op['data ult_call'] >= filtro_data]
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
    ativo = st.selectbox('Selecione o ativo', ativos, index=None, placeholder='Digite ou selecione')
with col2:
    vencimento = st.date_input('Data de vencimento das opções', format='DD/MM/YYYY')
with col3:
    quantidade = st.number_input('Quantidade', min_value=1, step=1, value=100)
with col4:
    estruturas = ['Collar de Alta', 'Collar de Baixa']
    estrutura = st.selectbox('Selecione a estrutura', estruturas)

with st.container():
    st.write('')
    st.write('Filtros')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        volume_put = st.slider('Volume mínimo da PUT', 0.01, 9999999.00, 500.00)
        risco = st.number_input("% de risco aceitável pela operação", min_value=-100.00, value=calcula_cdi(vencimento), 
                                help='O valor padrão é o CDI até o vencimento da opção.\nAo definir o risco mínimo, será apresentado somente operações mais lucrativas (ou menos prejudiciais) que o valor escolhido.')
    with col2:
        negocios_put = st.slider('Quantidade mínima de negócios da PUT', 1, 1000, 1, 1)
        corretagem_variavel = st.number_input('Taxa de corretagem variável da sua corretora', min_value=0.00, max_value=5.00, value=0.50)
    with col3:
        volume_call = st.slider('Volume mínimo da CALL', 0.01, 9999999.00, 500.00)
        corretagem_ordem = st.number_input('Taxa de corretagem por ordem', min_value=0.00, max_value=100.00, value=2.90)
    with col4:
        negocios_call = st.slider('Quantidade mínima de negócios da CALL', 1, 1000, 1, 1)
    with col5:
        filtro_data = st.date_input('Data último negócio', format='DD/MM/YYYY')

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
        df, df_put, df_call, df_op = collar_alta(ativo, vencimento, quantidade, volume_put, negocios_put, volume_call, 
                                                 negocios_call, filtro_data, risco, corretagem_variavel, corretagem_ordem)
        mostra_operacoes()
    elif estrutura == 'Collar de Baixa':
        df, df_put, df_call, df_op = collar_baixa(ativo, vencimento, quantidade, volume_put, negocios_put, volume_call, 
                                                  negocios_call, filtro_data, risco, corretagem_variavel, corretagem_ordem)
        mostra_operacoes()

st.markdown('---')