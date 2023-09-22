import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import numpy_financial as npf
import requests
import yfinance as yf

st.set_page_config(page_title='Raio-X Financeiro', 
                   page_icon='📊',
                   layout='wide')
st.title('Raio-X Financeiro')

st.write("""Um bom planejamento financeiro oferece uma abordagem abrangente para ajudar você a atingir seus objetivos no curto, médio e longo prazo. Nesta página você poderá inserir informações sobre suas finanças pessoais, incluindo receitas, despesas, investimentos atuais e seus planos de aposentadoria desejados, e automaticamente será realizada uma projeção precisa da sua situação financeira.
Usando algoritmos avançados, é calculada sua capacidade de poupança e projetado como seu patrimônio evoluirá ao longo do tempo. Isso é apresentado de forma visual em gráficos fáceis de entender, permitindo que você visualize seu caminho financeiro. Além disso, é possível visualizar a evolução do seu patrimônio após a aposentadoria, seja mantendo um patrimônio que gera renda vitalícia ou usando-o até os 100 anos.
Futuramente será incluída a funcionalidade de Asset Alocation, que é basicamente como sua carteira fica melhor distribuída de acordo com o seu perfil e objetivos, ajudando a maximizar seu potencial de retorno e minimizar riscos.
Através desse raio-X financeiro você terá uma visão clara e estratégica de suas finanças, permitindo que tome decisões informadas e trabalhe em direção a um futuro financeiro sólido e seguro. Estou aqui para ajudá-lo a alcançar seus objetivos financeiros com confiança e clareza.

Preencha as informações abaixo:""")

def calcula_idade(nascimento): 
    today = date.today() 
    try:  
        birthday = nascimento.replace(year = today.year) 
  
    except ValueError:  
        birthday = nascimento.replace(year = today.year, 
                  month = nascimento.month + 1, day = 1) 
  
    if birthday > today: 
        return today.year - nascimento.year - 1
    else: 
        return today.year - nascimento.year 

def calcula_patrimonio(idade, idade_indep, patrim_atual, cap_poup_ano, renda_mensal_indep, tx_juro_ano): 
    anos_invest = idade_indep - idade
    meses_invest = anos_invest * 12
    meses_consumo = anos_consumo * 12
    juro_mensal = (1+tx_juro_ano)**(1/12)-1
    patrim_acumulado = npf.fv(tx_juro_ano, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    tempo_consumo_meses = round(float(npf.nper(juro_mensal, renda_mensal_indep, -patrim_acumulado)),0)
    pat_vitalicio = round(renda_mensal_indep / juro_mensal, 2)
    parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -patrim_atual, -pat_vitalicio).round(2)
    pat_consumo = npf.pv(juro_mensal, meses_consumo, -renda_mensal_indep, 0).round(2)
    parcela_consumo = npf.pmt(juro_mensal, meses_invest, 0, -pat_consumo).round(2)
    patrim_consumo = npf.fv(tx_juro_ano, anos_invest, -parcela_consumo * 12, -patrim_atual)

    evo_ano = list(range(0, anos_invest + 1))
    df = pd.DataFrame(columns=['Idade', 'Valor Investido', 'Patrimônio Acumulado', 
                                        'Vitalício', 'Consumo Patrimônio'], 
                                index=evo_ano)
    for i in evo_ano:
        valor_investido_ano = npf.fv(0, evo_ano, -cap_poup_ano, -patrim_atual).round(2)
        patrimonio = npf.fv(tx_juro_ano, evo_ano, -cap_poup_ano, -patrim_atual).round(2)
        vitalicio = npf.fv(tx_juro_ano, evo_ano, -parcela_vitalicio * 12, -patrim_atual).round(2)
        consumo = npf.fv(tx_juro_ano, evo_ano, -parcela_consumo * 12, -patrim_atual).round(2)
        df['Idade'].loc[i] = idade + i
        df['Valor Investido'] = valor_investido_ano
        df['Patrimônio Acumulado'] = patrimonio
        df['Vitalício'] = vitalicio
        df['Consumo Patrimônio'] = consumo
    df = df.set_index('Idade')
    return df

def calcula_independencia(idade, idade_indep, patrim_atual, cap_poup_ano, renda_mensal_indep, tx_juro_ano):
    anos_invest = idade_indep - idade
    anos_consumo = 100 - idade_indep
    meses_invest = anos_invest * 12
    juro_mensal = (1+tx_juro_ano)**(1/12)-1
    renda_indep_anual = renda_mensal_indep * 12
    evo_ano_indep = list(range(idade_indep, 101))
    tempo_uso = list(range(0, anos_consumo + 1))
    tempo_consumo = list(range(anos_consumo, -1, -1))
    pat_vitalicio = round(renda_mensal_indep / juro_mensal, 2)
    valor_inv = npf.fv(0, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -patrim_atual, -pat_vitalicio).round(2)
    patrim_vitalicio = npf.fv(tx_juro_ano, anos_invest, -parcela_vitalicio * 12, -patrim_atual).round(2)
    patrim_acumulado = npf.fv(tx_juro_ano, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    df = pd.DataFrame({'Idade': evo_ano_indep,
                                    'Valor Investido': valor_inv,
                                    'Patrimônio Acumulado': 0,
                                    'Vitalício': patrim_vitalicio, 
                                    'Consumo Patrimônio': 0,
                                    'Tempo de usufruto': tempo_uso},
                                    index=tempo_consumo)

    for i in tempo_consumo:
        pat_consumo = npf.pv(tx_juro_ano, i, -renda_indep_anual).round(2)
        df['Consumo Patrimônio'].loc[i] = pat_consumo

    df = df.set_index('Tempo de usufruto')

    for i in tempo_uso:
        patrim_acum = npf.fv(tx_juro_ano, i, 0, -patrim_acumulado).round(2)
        df['Patrimônio Acumulado'].loc[i] = patrim_acum

    df = df.set_index('Idade')
    return df

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

def categoria_invest(categoria, key): 
        lista_acoes =  [i + '.SA' for i in lista_empresas()]     
        match categoria:
            case 'Ações':
                carteira_acoes = st.multiselect('Selecione o(s) papel(is)', lista_acoes, placeholder='Digite o ticker', key=f'acoes{key}')
            case 'FIIs':
                carteira_fiis = st.multiselect('Selecione o(s) papel(is)', ['HGLG11', 'MXRF11'], placeholder='Digite o ticker', key=f'fii{key}')
            case 'Renda Fixa':
                carteira_renda_fixa = st.text_input('Digite o(s) ativo(s)', key=f'rf{key}')
            case 'Tesouro Direto':
                carteira_tesouro = st.text_input('Digite o(s) ativo(s)', key=f'td{key}')
            case 'Fundos de Ações':
                carteira_fundos_acoes = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_acoes{key}')
            case 'Fundos de Renda Fixa':
                carteira_fundos_rf = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_rf{key}')
            case 'Fundos Multimercados':
                carteira_fundos_mult = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_mult{key}')
            case 'Moeda':
                carteira_moeda = st.text_input('Digite a(s) moeda(s)', key=f'moeda{key}')
            case 'Cripto':
                carteira_cripto = st.text_input('Digite o(s) ativo(s)', key=f'cripto{key}')
        return


st.markdown('### Núcelo Familiar')
col1, col2, col3, col4 = st.columns(4)
with col1:
    nome_cliente = st.text_input('Nome')

with col2:
    profissao_cliente = st.text_input('Profissão')
    
with col3:
    nascimento_cliente = st.date_input('Data de Nascimento', format='DD/MM/YYYY')
    idade_cliente = calcula_idade(nascimento_cliente)  
    st.write(str(idade_cliente), 'anos')
    
with col4:
    lista_estado_civil = ['Solteiro(a)', 'Casado(a) / União Estável', 'Viúvo(a)', 'Divorciado(a)']
    estado_civil = st.selectbox('Estado Civil', lista_estado_civil)
    
st.markdown('---')
if estado_civil == 'Casado(a) / União Estável':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nome_conjuge = st.text_input('Nome Cônjuge')

    with col2:
        profissao_conjuge = st.text_input('Profissão Cônjuge')
        
    with col3:
        nascimento_conjuge = st.date_input('Data de Nascimento Cônjuge', format='DD/MM/YYYY')
        idade_conjuge = calcula_idade(nascimento_conjuge)
        st.write(str(idade_conjuge), 'anos')
        
    with col4:
        lista_regime = ['Comunhão Parcial de Bens', 'Comunhão Total de Bens', 'Separação Total de Bens']
        regime_casamento = st.selectbox('Regime de Casamento', lista_regime)
    st.markdown('---')
    
filhos = st.radio('Possui Filhos?', ['Não', 'Sim'], horizontal=True, )
if filhos == 'Sim':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nome_filho1 = st.text_input('Nome Filho(a)', key='nome_filho1')
        st.write('')
        st.write('')
        st.write('')
        nome_filho3 = st.text_input('Nome Filho(a)', key='nome_filho3')
        
    with col2:
        nascimento_filho1 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho1')
        idade_filho1 = calcula_idade(nascimento_filho1)
        st.write(str(idade_filho1), 'anos')
        nascimento_filho3 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho3')
        idade_filho3 = calcula_idade(nascimento_filho3)
        st.write(str(idade_filho3), 'anos')
        
    with col3:
        nome_filho2 = st.text_input('Nome Filho(a)', key='nome_filho2')
        st.write('')
        st.write('')
        st.write('')
        nome_filho4 = st.text_input('Nome Filho(a)', key='nome_filho4')

    with col4:
        nascimento_filho2 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascimento_filho2')
        idade_filho2 = calcula_idade(nascimento_filho2)
        st.write(str(idade_filho2), 'anos')
        nascimento_filho4 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho4')
        idade_filho4 = calcula_idade(nascimento_filho4)
        st.write(str(idade_filho4), 'anos')
st.markdown('---')


st.markdown('### Orçamento Doméstico')
st.markdown('##### Receitas')
col1, col2, col3, col4 = st.columns(4)
with col1:
    receita_mensal = st.number_input('Receita Mensal')
    receita_conjuge = 0

with col2:
    outras_receitas = st.number_input('Outras Receitas')
    
with col3:
    if estado_civil == 'Casado(a) / União Estável':
        receita_conjuge = st.number_input('Receita Cônjuge')

with col4:
    if estado_civil == 'Casado(a) / União Estável':
        receita_total = receita_mensal + outras_receitas + receita_conjuge
        st.metric('Receita total familiar', f'R$ {receita_total:.2f}') 
    else:
        receita_total = receita_mensal + outras_receitas
        st.metric('Receita total familiar', f'R$ {receita_total:.2f}') 
    
st.markdown('##### Despesas')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    despesa_mensal = st.number_input('Despesa Mensal')
    
st.markdown('##### Capacidade de Poupança')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    cap_poupanca = receita_total - despesa_mensal
    cap_poupanca_anual = cap_poupanca * 12
    st.metric('Sua capacidade de poupança mensal é', f'R$ {cap_poupanca:.2f}')
with col2:
    st.metric('Sua capacidade de poupança anual é', f'R$ {cap_poupanca_anual:.2f}')

st.markdown('---')


st.markdown('### Investimentos')
md_invest = st.toggle('Adicionar investimentos atuais')
invest_atual = 0
if md_invest:
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        categorias = ['Ações', 'FIIs', 'Renda Fixa', 'Tesouro Direto', 'Fundos de Ações',
                    'Fundos de Renda Fixa', 'Fundos Multimercados', 'Moeda', 'Cripto']
        cat1 = st.selectbox('Categoria', categorias, key='cat1')
        cat2 = st.selectbox('Categoria', categorias, key='cat2', index=1)
        cat3 = st.selectbox('Categoria', categorias, key='cat3', index=2)
        cat4 = st.selectbox('Categoria', categorias, key='cat4', index=3)
        cat5 = st.selectbox('Categoria', categorias, key='cat5', index=4)
        cat6 = st.selectbox('Categoria', categorias, key='cat6', index=7)
        cat7 = st.selectbox('Categoria', categorias, key='cat7', index=8)
        
    with col2:
        categoria_invest(cat1, 1)
        categoria_invest(cat2, 2)
        categoria_invest(cat3, 3)
        categoria_invest(cat4, 4)
        categoria_invest(cat5, 5)
        categoria_invest(cat6, 6)
        categoria_invest(cat7, 7)
            
    with col3:
        valor_ativos1 = st.number_input('Valor total dos ativos', key='val1')
        valor_ativos2 = st.number_input('Valor total dos ativos', key='val2')
        valor_ativos3 = st.number_input('Valor total dos ativos', key='val3')
        valor_ativos4 = st.number_input('Valor total dos ativos', key='val4')
        valor_ativos5 = st.number_input('Valor total dos ativos', key='val5')
        valor_ativos6 = st.number_input('Valor total dos ativos', key='val6')
        valor_ativos7 = st.number_input('Valor total dos ativos', key='val7')
        invest_atual = valor_ativos1 + valor_ativos2 + valor_ativos3 + valor_ativos4 + valor_ativos5 + valor_ativos6 + valor_ativos7
        st.metric('Patrimônio Atual', f'R$ {invest_atual:.2f}')
st.markdown('---')


st.markdown('### Bens Mobiliários e Imobiliários')
md_bens = st.toggle('Adicionar bens móveis e imóveis')
bens_atual = 0
if md_bens:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1]) 
    with col1:
        categorias_bens = ['Imóvel', 'Automóvel', 'Aeronave/Embarcação', 'Precatório', 'Outro']
        catbens1 = st.selectbox('Categoria', categorias_bens, key='catbens1')
        catbens2 = st.selectbox('Categoria', categorias_bens, key='catbens2', index=1)
        catbens3 = st.selectbox('Categoria', categorias_bens, key='catbens3', index=2)
        catbens4 = st.selectbox('Categoria', categorias_bens, key='catbens4', index=3)
        catbens5 = st.selectbox('Categoria', categorias_bens, key='catbens5', index=4)
        catbens6 = st.selectbox('Categoria', categorias_bens, key='catbens6', index=4)
        catbens7 = st.selectbox('Categoria', categorias_bens, key='catbens7', index=4)
        
    with col2:
        bem1 = st.text_input('Descrição', key='bem1')
        bem2 = st.text_input('Descrição', key='bem2')
        bem3 = st.text_input('Descrição', key='bem3')
        bem4 = st.text_input('Descrição', key='bem4')
        bem5 = st.text_input('Descrição', key='bem5')
        bem6 = st.text_input('Descrição', key='bem6')
        bem7 = st.text_input('Descrição', key='bem7')
            
    with col3:
        valor_bens1 = st.number_input('Valor do bem', key='valbens1')
        valor_bens2 = st.number_input('Valor do bem', key='valbens2')
        valor_bens3 = st.number_input('Valor do bem', key='valbens3')
        valor_bens4 = st.number_input('Valor do bem', key='valbens4')
        valor_bens5 = st.number_input('Valor do bem', key='valbens5')
        valor_bens6 = st.number_input('Valor do bem', key='valbens6')
        valor_bens7 = st.number_input('Valor do bem', key='valbens7')
        bens_atual = valor_bens1 + valor_bens2 + valor_bens3 + valor_bens4 + valor_bens5 + valor_bens6 + valor_bens7
        st.metric('Patrimônio em Bens Atual', f'R$ {bens_atual:.2f}') 
        
    with col4:
        op_venda = ['Selecione', 'Sim', 'Não', 'N/A']
        vendavel1 = st.selectbox('Vendável', op_venda, key='vendavel1')
        vendavel2 = st.selectbox('Vendável', op_venda, key='vendavel2')
        vendavel3 = st.selectbox('Vendável', op_venda, key='vendavel3')
        vendavel4 = st.selectbox('Vendável', op_venda, key='vendavel4')
        vendavel5 = st.selectbox('Vendável', op_venda, key='vendavel5')
        vendavel6 = st.selectbox('Vendável', op_venda, key='vendavel6')
        vendavel7 = st.selectbox('Vendável', op_venda, key='vendavel7')
    
    with col5:
        renda_bens1 = st.number_input('Renda do bem', key='rendabens1')
        renda_bens2 = st.number_input('Renda do bem', key='rendabens2')
        renda_bens3 = st.number_input('Renda do bem', key='rendabens3')
        renda_bens4 = st.number_input('Renda do bems', key='rendabens4')
        renda_bens5 = st.number_input('Renda do bem', key='rendabens5')
        renda_bens6 = st.number_input('Renda do bem', key='rendabens6')
        renda_bens7 = st.number_input('Renda do bem', key='rendabens7')
st.markdown('---')

patrimonio_total = invest_atual + bens_atual

st.markdown('### Independência Financeira')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    idade_indep = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=50, step=1)
   
with col2:
    renda_indep = st.number_input('Renda Mensal Desejada')
    renda_indep_anual = renda_indep * 12
    
with col3:
    juro_real = st.number_input('Taxa de Juros Real', value=4.0, step=0.5) / 100
    juro_mensal = (1+juro_real)**(1/12)-1

anos_invest = idade_indep - idade_cliente
meses_invest = anos_invest * 12
anos_consumo = 100 - idade_indep
meses_consumo = anos_consumo * 12
patrim_acumulado = npf.fv(juro_real, anos_invest, -cap_poupanca_anual, -invest_atual).round(2)
pat_consumo = npf.pv(juro_mensal, meses_consumo, -renda_indep, 0).round(2)
parcela_consumo = npf.pmt(juro_mensal, meses_invest, -invest_atual, -pat_consumo).round(2)
patrim_consumo = npf.fv(juro_real, anos_invest, -parcela_consumo * 12, -invest_atual)
pat_vitalicio = round(renda_indep / juro_mensal, 2)
parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -invest_atual, -pat_vitalicio).round(2)
patrim_vitalicio = npf.fv(juro_real, anos_invest, -parcela_vitalicio * 12, -invest_atual).round(2)
valor_inv = npf.fv(0, anos_invest, -cap_poupanca_anual, -invest_atual).round(2)

df_patrimonio = calcula_patrimonio(idade_cliente, idade_indep, invest_atual, cap_poupanca_anual, renda_indep, juro_real)
df_independencia = calcula_independencia(idade_cliente, idade_indep, invest_atual, cap_poupanca_anual, renda_indep, juro_real)
df_evolucao = pd.concat([df_patrimonio, df_independencia]).drop_duplicates('Patrimônio Acumulado')

tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução Patrimonial", "Acumulação de Patrimônio", "Independência Financeira", "🗃 Dados"])
with tab1:
    st.subheader('Evolução Patrimonial')
    st.line_chart(df_evolucao)
    
with tab2:
    st.subheader('Acumulação de Patrimônio')
    st.line_chart(df_patrimonio)
    
with tab3:
    st.subheader('Independência Financeira')
    st.line_chart(df_independencia)
    
with tab4:
    st.subheader('Dados Detalhados')
    st.dataframe(df_evolucao)

col1, col2, col3 = st.columns(3)  
with col1:
    st.metric('Projeção de Patrimônio', f'R$ {patrim_acumulado:.2f}')
    st.write('')
    st.metric('Aportes Mensais', f'R$ {cap_poupanca:.2f}')
    
with col2:
    st.metric('Patrimônio para consumo até os 100 anos', f'R$ {patrim_consumo:.2f}', f'{(patrim_acumulado/patrim_consumo-1)*100:.2f}%')
    st.metric('Aportes Mensais', f'R$ {parcela_consumo:.2f}')
    
with col3:
    st.metric('Patrimônio para renda vitalícia', f'R$ {patrim_vitalicio:.2f}', f'{(patrim_acumulado/patrim_vitalicio-1)*100:.2f}%')
    st.metric('Aportes Mensais', f'R$ {parcela_vitalicio:.2f}')

st.markdown('---')

cenario2 = st.toggle('Simular outro cenário')
if cenario2:
    st.markdown('### Cenário 2')
    
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        idade_indep_2 = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=60, step=1)

    with col2:
        renda_indep_2 = st.number_input('Renda Mensal Desejada', key='RendaIndep2')
        renda_indep_anual_2 = renda_indep_2 * 12
        
    with col3:
        juro_real_2 = st.number_input('Taxa de Juros Real', value=5.0, step=0.5) / 100
        juro_mensal_2 = (1+juro_real_2)**(1/12)-1
        
    with col4:
        cap_poupanca_anual_2 = st.number_input('Capacidade de Poupança Anual')
     
    anos_invest_2 = idade_indep_2 - idade_cliente
    meses_invest_2 = anos_invest_2 * 12
    anos_consumo_2 = 100 - idade_indep_2
    meses_consumo_2 = anos_consumo_2 * 12
    patrim_acumulado_2 = npf.fv(juro_real_2, anos_invest_2, -cap_poupanca_anual_2, -invest_atual).round(2)
    pat_consumo_2 = npf.pv(juro_mensal_2, meses_consumo_2, -renda_indep_2, 0).round(2)
    parcela_consumo_2 = npf.pmt(juro_mensal_2, meses_invest_2, -invest_atual, -pat_consumo_2).round(2)
    patrim_consumo_2 = npf.fv(juro_real_2, anos_invest_2, -parcela_consumo_2 * 12, -invest_atual)
    pat_vitalicio_2 = round(renda_indep_2 / juro_mensal_2, 2)
    parcela_vitalicio_2 = npf.pmt(juro_mensal_2, meses_invest_2, -invest_atual, -pat_vitalicio_2).round(2)
    patrim_vitalicio_2 = npf.fv(juro_real_2, anos_invest_2, -parcela_vitalicio_2 * 12, -invest_atual).round(2)
    valor_inv_2 = npf.fv(0, anos_invest_2, -cap_poupanca_anual_2, -invest_atual).round(2)

    df_patrimonio_2 = calcula_patrimonio(idade_cliente, idade_indep_2, invest_atual, cap_poupanca_anual_2, renda_indep_2, juro_real_2)
    df_independencia_2 = calcula_independencia(idade_cliente, idade_indep_2, invest_atual, cap_poupanca_anual_2, renda_indep_2, juro_real_2)
    df_evolucao_2 = pd.concat([df_patrimonio_2, df_independencia_2]).drop_duplicates('Patrimônio Acumulado')

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução Patrimonial", "Acumulação de Patrimônio", "Independência Financeira", "🗃 Dados"])
    with tab1:
        st.subheader('Evolução Patrimonial')
        st.line_chart(df_evolucao_2)
        
    with tab2:
        st.subheader('Acumulação de Patrimônio')
        st.line_chart(df_patrimonio_2)
        
    with tab3:
        st.subheader('Independência Financeira')
        st.line_chart(df_independencia_2)
        
    with tab4:
        st.subheader('Dados Detalhados')
        st.dataframe(df_evolucao_2)  
   
    with col1:
        st.metric('Projeção de Patrimônio', f'R$ {patrim_acumulado_2:.2f}')
        st.write('')
        st.metric('Aportes Mensais', f'R$ {cap_poupanca_anual_2 / 12:.2f}')
        
    with col2:
        st.metric('Patrimônio para consumo até os 100 anos', f'R$ {patrim_consumo_2:.2f}', f'{(patrim_acumulado_2/patrim_consumo_2-1)*100:.2f}%')
        st.metric('Aportes Mensais', f'R$ {parcela_consumo_2:.2f}')
        
    with col3:
        st.metric('Patrimônio para renda vitalícia', f'R$ {patrim_vitalicio_2:.2f}', f'{(patrim_acumulado_2/patrim_vitalicio_2-1)*100:.2f}%')
        st.metric('Aportes Mensais', f'R$ {parcela_vitalicio_2:.2f}')

st.markdown('---')


if receita_mensal > 0 and despesa_mensal > 0:
    st.write('### Receitas')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write('Receitas x Despesas')
        plt.style.use('_mpl-gallery-nogrid')
        x = [receita_mensal, outras_receitas, receita_conjuge]
        colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))
        fig, ax = plt.subplots()
        ax.pie(x, colors=colors, radius=3, center=(4, 4),
            wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False, labels=x)
        st.pyplot(fig)
        
    with col3:
        st.write('Distribuição das Receitas')
        plt.style.use('_mpl-gallery-nogrid') 
        x = [receita_total, despesa_mensal, cap_poupanca]
        colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(x)))
        fig, ax = plt.subplots()
        ax.pie(x, colors=colors, radius=3, center=(4, 4),
            wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=False, labels=x)
        
        st.pyplot(fig)
    st.markdown('---')





st.sidebar.header('Resumo')
if idade_cliente > 0:
    st.sidebar.write(nome_cliente)
    st.sidebar.write(str(idade_cliente), 'anos')
    if estado_civil == 'Casado(a) / União Estável':
        st.sidebar.write(f'Casado(a) com {nome_conjuge}')
    if filhos == 'Sim':    
        st.sidebar.write('Filho(a)')
        st.sidebar.write(nome_filho1)
        st.sidebar.write(nome_filho2)
        st.sidebar.write(nome_filho3)
        st.sidebar.write(nome_filho4)
    st.sidebar.write(f'Receita mensal familiar de R$ {receita_total:.2f}')
    st.sidebar.write(f'Despesa mensal familiar de R$ {despesa_mensal:.2f}')
    st.sidebar.write(f'Capacidade poupança mensal de R$ {cap_poupanca:.2f}')
    st.sidebar.write(f'Investimentos atuais R$ {invest_atual:.2f}')
    st.sidebar.write(f'Valores em bens atuais R$ {bens_atual:.2f}')
