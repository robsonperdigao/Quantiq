import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import numpy_financial as npf

st.set_page_config(page_title='Contexto de Vida e Diagnóstico', 
                   page_icon='📊',
                   layout='wide')
st.title('Contexto de Vida')
st.sidebar.header('Diagnóstico')
st.write(
    """Texto explicativo sobre o que é o contexto de vida e diagnóstico"""
)

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

with col2:
    outras_receitas = st.number_input('Outras Receitas')
    
with col3:
    if estado_civil == 'Casado(a) / União Estável':
        receita_conjuge = st.number_input('Receita Cônjuge')

with col4:
    if estado_civil == 'Casado(a) / União Estável':
        receita_total = receita_mensal + outras_receitas + receita_conjuge
        st.write('A receita total familiar é de R$', str(receita_total))
    else:
        receita_total = receita_mensal + outras_receitas 
        st.write('A receita total familiar é de R$', str(receita_total))

st.markdown('##### Despesas')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    despesa_mensal = st.number_input('Despesa Mensal')
    
st.markdown('##### Capacidade de Poupança')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    cap_poupanca = receita_total - despesa_mensal
    cap_poupanca_anual = cap_poupanca * 12
st.write('Sua capacidade de poupança é de R$', str(cap_poupanca), 'mensais')
st.write('Sua capacidade de poupança é de R$', str(cap_poupanca_anual), 'anuais')

st.markdown('---')

st.markdown('### Investimentos')
#Criar
st.markdown('---')

st.markdown('### Ativos Mobiliários e Imobiliários')
#Criar
st.markdown('---')

st.markdown('### Independência Financeira')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    idade_indep = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=50, step=1)
    anos_indep = idade_indep - idade_cliente
    st.write(anos_indep)
    
with col2:
    renda_indep = st.number_input('Renda Mensal Desejada')
    
with col3:
    juro_real = st.number_input('Taxa de Juros Real', value=4.0, step=0.5) / 100
    juro_mensal = (1+juro_real)**(1/12)-1
    
patrim_indep = npf.fv(juro_real, anos_indep, -cap_poupanca_anual, 0).round(2)
tempo_consumo = round(float(npf.nper(juro_mensal, renda_indep, -patrim_indep)),0)
renda_perpetua = round(renda_indep / juro_mensal, 2)
meses_consumo = (100 - idade_indep) * 12
renda_consumo = npf.pv(juro_mensal, meses_consumo, -renda_indep).round(2)
st.write(patrim_indep)
st.write(tempo_consumo)
st.write(renda_perpetua)

evo_anual = list(range(1, anos_indep+1))
df = pd.DataFrame(columns=['Valor Investido', 'Patrimônio'], index=evo_anual)
for i in evo_anual:
    valor_investido = npf.fv(0, evo_anual, -cap_poupanca_anual, 0).round(2)
    patrimonio = npf.fv(juro_real, evo_anual, -cap_poupanca_anual, 0).round(2)
    df['Valor Investido'] = valor_investido
    df['Patrimônio'] = patrimonio

tab1, tab2 = st.tabs(["📈 Gráfico", "🗃 Dados"])
tab1.subheader("Evolução Patrimonial")
tab1.line_chart(df)

tab2.subheader("Dados Detalhados")
tab2.write(df)
col1, col2, col3 = st.columns(3)  
with col1:
    st.success(f'Projeção de patrimônio: R$ {patrim_indep:.2f}')
    
with col2:
    st.success(f'Capital necessário para consumo até os 100 anos: R$ {renda_consumo:.2f}')
    
with col3:
    st.success(f'Capital necessário para renda vitalícia: R$ {renda_perpetua:.2f}')

st.markdown('---')

cenario2 = st.toggle('Simular outro cenário')
if cenario2:
    st.markdown('### Cenário 2')
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        idade_indep_2 = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=60, step=1)
        anos_indep_2 = idade_indep_2 - idade_cliente
        st.write(anos_indep_2)  

    with col2:
        renda_indep_2 = st.number_input('Renda Mensal Desejada', key='RendaIndep2')

    with col3:
        juro_real_2 = st.number_input('Taxa de Juros Real', value=5.0, step=0.5) / 100
        
    with col4:
        cap_poupanca_anual_2 = st.number_input('Capacidade de Poupança Anual')
    
    evo_anual_2 = list(range(1, anos_indep_2+1))
    df = pd.DataFrame(columns=['Valor Investido', 'Patrimônio'], index=evo_anual_2)
    for i in evo_anual_2:
        valor_investido = npf.fv(0, evo_anual_2, -cap_poupanca_anual_2, 0).round(2)
        patrimonio = npf.fv(juro_real_2, evo_anual_2, -cap_poupanca_anual_2, 0).round(2)
        df['Valor Investido'] = valor_investido
        df['Patrimônio'] = patrimonio
         
    patrim_indep_2 = npf.fv(juro_real_2, anos_indep_2, -cap_poupanca_anual_2, 0).round(2)  
    
    tab1, tab2 = st.tabs(["📈 Gráfico", "🗃 Dados"])
    
    with tab1:
        st.subheader("Evolução Patrimonial")
        st.line_chart(df)
    
    with tab2:
        st.subheader("Dados Detalhados")
        st.write(df)

    col1, col2, col3 = st.columns(3)  
    with col1:
        st.success(f'Projeção de patrimônio: R$ {patrim_indep}')
        
    with col2:
        st.success(f'Capital necessário para consumo até os 100 anos: R$ {patrim_indep}')
        
    with col3:
        st.success(f'Capital necessário para renda vitalícia: R$ {patrim_indep}')

st.markdown('---')

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
