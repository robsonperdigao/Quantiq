import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import datetime as dt
from datetime import date, datetime
from workadays import workdays as wd
from src import utils
import numpy as np


# Mostrar tabela de operações
def mostra_operacoes():
    if len(df) == 0:
        st.write('Não há estratégias disponíveis')
    else:
        with st.expander('Lista de operações possíveis', expanded=True):
            st.dataframe(df_op)
        with st.expander('Tabela com todas as operações para o ativo'):
            st.dataframe(df)
        with st.expander('Tabela com todas as PUTs do ativo'):
            st.dataframe(df_put)
        with st.expander('Tabela com todas as CALLs do ativo'):
            st.dataframe(df_call)
    return

def calcula_cdi(vencimento):
    # Coleta selic anual direto pelo BC
    url_selic = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json'
    selic = pd.read_json(url_selic)
    selic['data'] = pd.to_datetime(selic['data'], dayfirst=True)
    selic.set_index('data', inplace=True)
    selic = float(selic.iloc[-1].values[0])

    # Calcula a quantidade de dias úteis e o rendimento do CDI até o vencimento
    data_hoje = datetime.now().date()
    dias_uteis = wd.networkdays(data_hoje, vencimento, country='BR')
    cdi_operacao = round(((1 + selic / 100) ** (dias_uteis / 252) - 1) * 100, 2)
    return cdi_operacao

def coleta_opcoes(ativo, vencimento):
    # Coleta o preço do ativo com base no último fechamento
    preco_ativo = round(yf.download(ativo +'.SA', period='1d')['Adj Close'].iloc[-1], 2)
    
    # Coleta informações das opções
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={ativo}&listarVencimentos=false&cotacoes=true&vencimentos={vencimento}'
    r = requests.get(url).json()
    x = ([ativo, vencimento, i[0].split('_')[0], i[2], i[5], i[8], i[9], i[10], i[11]] for i in r['data']['cotacoesOpcoes'])
    df = pd.DataFrame(x, columns=['Ativo', 'Vencimento', 'Ticker', 'Tipo', 'Strike', 'Preço', 'Negócios', 'Volume', 'Último Negócio'])
    df['Último Negócio'] = pd.to_datetime(df['Último Negócio'], dayfirst=True).dt.date
    
    # Cria um dataframe somente com as PUTs
    df_put = df[df['Tipo'] == 'PUT']
    df_put_op = df_put.copy()
    df_put_op.rename(columns={
        'Ticker': 'Ticker Put',
        'Tipo': 'Tipo Put',
        'Strike': 'Strike Put', 
        'Preço': 'Preço Put',
        'Negócios': 'Negócios Put',
        'Volume': 'Volume Put',
        'Último Negócio': 'Último Negócio Put'
    }, inplace=True)

    # Cria um dataframe somente com as CALLs e renomeia colunas para diferenciar
    df_call = df[df['Tipo'] == 'CALL']
    df_call_op = df_call.copy()
    df_call_op.drop(columns=['Vencimento'], inplace=True)
    df_call_op.rename(columns={
        'Ticker': 'Ticker Call',
        'Tipo': 'Tipo Call',
        'Strike': 'Strike Call', 
        'Preço': 'Preço Call',
        'Negócios': 'Negócios Call',
        'Volume': 'Volume Call',
        'Último Negócio': 'Último Negócio Call'
    }, inplace=True)

    # Cria um dataframe com as operações possíveis para cada PUT
    df = pd.merge(df_put_op, df_call_op, on='Ativo', suffixes=('', '_call'))
    df['Preço Ativo'] = preco_ativo
    
    return df, df_put, df_call, preco_ativo

# Operação - Collar de Alta
def collar(ativo, vencimento, operacao='collar_alta', quantidade = 1, volume_put = 0.01, negocios_put = 1, volume_call = 0.01, 
                negocios_call = 1, filtro_data=None, risco = 0.00, corretagem_variavel = 0.00, corretagem_ordem = 0.00):
    '''
    Ativo: Ativo base da B3\n
    Vencimento: Data de vencimento da opção\n
    Operacao: collar_alta, collar_baixa\n

    '''
    # Coleta as opções disponíveis para o ativo com base no vencimento determinado
    df, df_put, df_call, preco_ativo = coleta_opcoes(ativo, vencimento)
    
    if corretagem_variavel > 0:
        tx_b3 = 0.134
    else:
        tx_b3 = 0.00
    filtro_data = datetime.strptime(filtro_data, '%Y-%m-%d').date()

    df['Custo Operação'] = round((preco_ativo + df['Preço Put'] - df['Preço Call']) * quantidade, 2)
    df['Corretagem'] = round((df['Custo Operação'] * ((corretagem_variavel + tx_b3) / 100)) + 6 * corretagem_ordem, 2)
    df['Corretagem (%)'] = round(df['Corretagem'] / df['Custo Operação'] * 100, 2)
    df['Risco (%)'] = float(risco)
    
    if operacao == 'collar_alta':
        df['Lucro Mínimo'] = round(df['Strike Put'] * quantidade - df['Custo Operação'], 2)
        df['Lucro Máximo'] = round(df['Strike Call'] * quantidade - df['Custo Operação'], 2)
    elif operacao == 'collar_baixa':
        df['Lucro Mínimo'] = round(df['Strike Call'] * quantidade - df['Custo Operação'], 2)
        df['Lucro Máximo'] = round(df['Strike Put'] * quantidade - df['Custo Operação'], 2)

    df['Lucro Mín (%)'] = round(df['Lucro Mínimo'] / df['Custo Operação'] * 100, 2)
    df['Lucro Máx (%)'] = round(df['Lucro Máximo'] / df['Custo Operação'] * 100, 2)
    
    # Filtra o dataframe somente com as operações lucrativas
    df_op = df.copy()
    df_op = df_op[df_op['Lucro Mín (%)'] >= df['Corretagem (%)'] + df['Risco (%)']]
    df_op = df_op[df_op['Lucro Máximo'] > 0]
    
    if operacao == 'collar_alta':
        df_op = df_op[df_op['Strike Put'] > preco_ativo]
        df_op = df_op[df_op['Strike Call'] > df_op['Strike Put']]
    elif operacao == 'collar_baixa':
        df_op = df_op[df_op['Strike Put'] < preco_ativo + 2]
        df_op = df_op[df_op['Strike Call'] < df_op['Strike Put']]

    df_op = df_op[df_op['Volume Put'] >= volume_put]
    df_op = df_op[df_op['Negócios Put'] >= negocios_put]
    df_op = df_op[df_op['Volume Call'] >= volume_call]
    df_op = df_op[df_op['Negócios Call'] >= negocios_call]
    df_op = df_op[df_op['Último Negócio Put'] >= filtro_data]
    df_op = df_op[df_op['Último Negócio Call'] >= filtro_data]
    df_op = df_op.sort_values(by='Lucro Mín (%)',ascending=False)
    df_op = df_op.drop(columns=['Tipo Put', 'Volume Put', 
                                'Tipo Call','Volume Call', 
                                'Corretagem', 'Corretagem (%)',
                                'Lucro Mínimo', 'Lucro Máximo'])
    
    data_columns = ['Vencimento', 'Último Negócio Put', 'Último Negócio Call']
    for col in data_columns:
        df_op[col] = pd.to_datetime(df_op[col]).dt.strftime('%d/%m/%Y')
    
    real_columns = ['Strike Put', 'Preço Put', 'Strike Call', 'Preço Call', 
                    'Preço Ativo', 'Custo Operação']
    for col in real_columns:
        df_op[col] = df_op[col].apply(lambda x: "R$ " + str(x).replace('.', ',') if pd.notnull(x) else x)
    
    pct_columns = ['Risco (%)', 'Lucro Mín (%)', 'Lucro Máx (%)']
    for col in pct_columns:
        df_op[col] = df_op[col].apply(lambda x: str(x).replace('.', ',') + "%" if pd.notnull(x) else x)

    df_op = df_op.reindex(columns=['Ativo', 'Preço Ativo', 'Custo Operação', 'Risco (%)', 'Lucro Mín (%)', 'Lucro Máx (%)',
                                   'Ticker Put', 'Strike Put', 'Preço Put', 'Negócios Put', 'Último Negócio Put',
                                   'Ticker Call', 'Strike Call', 'Preço Call', 'Negócios Call', 'Último Negócio Call'])
    
    df_op.reset_index(drop=True, inplace=True)

    return df, df_put, df_call, df_op




st.set_page_config(page_title='Estratégias com Opções',
                   page_icon='❇️',
                   layout='wide')
st.title('Estratégias de Opções')

st.write('Selecione o ativo desejado e escolha a estrutura que pretende montar com opções e veja o resultado detalhado dos ativos.')
st.markdown('---')


col1, col2, col3, col4 = st.columns(4)
with col1:
    ativos = utils.lista_ativos_b3()
    ativos.append('BOVA11')
    ativo = st.selectbox('Selecione o ativo', ativos, index=None, placeholder='Digite ou selecione')
with col2:
    vencimentos = utils.vencimentos_opcoes()
    
    vencimento = st.selectbox('Selecione a data de vencimento das opções', vencimentos)
    vencimento = datetime.strptime(vencimento, '%d/%m/%Y').date()
    #vencimento = st.date_input('Data de vencimento das opções', format='DD/MM/YYYY')
#with col3:
    #quantidade = st.number_input('Quantidade', min_value=1, step=1, value=100)
with col3:
    estruturas = ['Collar de Alta', 'Collar de Baixa']
    estrutura = st.selectbox('Selecione a estrutura', estruturas)

st.write('')
with st.expander('Filtros', expanded=False):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        #volume_put = st.slider('Volume mínimo da PUT', 0.01, 9999999.00, 500.00)
        risco = st.number_input("% de risco aceitável pela operação", min_value=-100.00, value=calcula_cdi(vencimento), 
                                help='O valor padrão é o CDI até o vencimento da opção. Ao definir o risco mínimo, será apresentado somente operações mais lucrativas (ou menos prejudiciais) que o valor escolhido.')
    with col2:
        #negocios_put = st.slider('Quantidade mínima de negócios da PUT', 1, 1000, 1, 1)
        corretagem_variavel = st.number_input('Taxa de corretagem variável', min_value=0.00, max_value=5.00, value=0.00,
                                              help='Geralmente as corretoras cobram 0,50% do volume para exercício. Altere conforme necessidade.')
    with col3:
        #volume_call = st.slider('Volume mínimo da CALL', 0.01, 9999999.00, 500.00)
        corretagem_ordem = st.number_input('Taxa de corretagem por ordem', min_value=0.00, max_value=100.00, value=0.00)
    #with col4:
        #negocios_call = st.slider('Quantidade mínima de negócios da CALL', 1, 1000, 1, 1)
    with col5:
        now = datetime.now()
        if now.hour < 19:
            # Se for antes das 19h, o valor padrão é o dia de ontem
            default_date = now.date() - dt.timedelta(days=1)
        else:
            # Se for depois das 19h, o valor padrão é o dia de hoje
            default_date = now.date()
        # Ajustar o valor padrão se não for um dia útil
        while not wd.is_workday(default_date, country="BR"):
            # Subtrair um dia até encontrar um dia útil
            default_date = default_date - dt.timedelta(days=1)
        filtro_data = default_date
        #filtro_data = st.date_input('Data último negócio', default_date, format='DD/MM/YYYY')

st.write('')
button = st.button('Ver as estratégias')

with st.container():
    if button:
        if estrutura == 'Collar de Alta':
            df, df_put, df_call, df_op = collar(ativo, vencimento, operacao='collar_alta', filtro_data=filtro_data, risco=risco, 
                                                     corretagem_variavel=corretagem_variavel, corretagem_ordem=corretagem_ordem)
            mostra_operacoes()
        elif estrutura == 'Collar de Baixa':
            df, df_put, df_call, df_op = collar(ativo, vencimento, operacao='collar_baixa', filtro_data=filtro_data, risco=risco, 
                                                     corretagem_variavel=corretagem_variavel, corretagem_ordem=corretagem_ordem)
            mostra_operacoes()
            

        st.markdown('---')

        