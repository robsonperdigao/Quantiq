import streamlit as st
import pandas as pd
import numpy_financial as npf
from datetime import date

def consulta_bc(codigo_bcb, data_ini = '01/01/1900', data_fim = date.today().strftime('%d/%m/%Y')):
  url = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_bcb}/dados?formato=json&dataInicial={data_ini}&dataFinal={data_fim}'
  df = pd.read_json(url)
  df['data'] = pd.to_datetime(df['data'], dayfirst=True)
  df.set_index('data', inplace=True)
  return df

def calcula_taxa_mensal(taxa_anual):
    return ((1 + taxa_anual / 100) ** (1/12) - 1)

def calcula_imposto(lucro, prazo):
    if prazo <= 6:
        ir = lucro * 0.225
    elif prazo <= 12:
        ir = lucro * 0.20
    elif prazo <= 24:
        ir = lucro * 0.175
    else:
        ir = lucro * 0.15
    return ir
    
def calcula_retorno(ativo, aporte, prazo, taxa):
    vlr_bruto = round(npf.fv(calcula_taxa_mensal(taxa), prazo, 0, -aporte), 2)
    lucro = vlr_bruto - vlr
    if (ativo == 'LCI/LCA') or (ativo == 'CRI/CRA'):
        ir = 0
    else:
        ir = calcula_imposto(lucro, prazo)
    lucro_liquido = lucro - ir
    vlr_liq_resgate = vlr + lucro_liquido
    rent_liq = round((vlr_liq_resgate / vlr - 1) * 100, 2)
    return vlr_bruto, lucro, ir, lucro_liquido, vlr_liq_resgate, rent_liq

def comparativo(key):
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            ativo = st.selectbox('Selecione a classe do ativo', ['Tesouro Direto', 'CDB', 'LCI/LCA', 'CRI/CRA', 'Debênture'], index=1, key=f'ativo{key}')
        with col2:
            opt = st.selectbox('Tipo de rentabilidade', ['Pré-Fixado', 'Pós-Fixado', 'Híbrido'], index=1, key=f'opt{key}')
        with col3:
            match opt:
                case 'Pré-Fixado':
                    tx = st.number_input('Insira a taxa contratada', value=10.0, key=f'pre{key}')
                    vlr_bruto, lucro, ir, lucro_liquido, vlr_liq_resgate, rent_liq = calcula_retorno(ativo, vlr, prazo, tx)
                case 'Pós-Fixado':
                    pct_cdi = st.number_input('% do CDI', value=110.0, key=f'cdi{key}') / 100
                    tx = pct_cdi * cdi_ano
                    vlr_bruto, lucro, ir, lucro_liquido, vlr_liq_resgate, rent_liq = calcula_retorno(ativo, vlr, prazo, tx)
                case 'Híbrido':
                    tx_pre = st.number_input('Insira a taxa IPCA + X', value=7.0, key=f'hib{key}')
                    tx = tx_pre + ipca_ano
                    vlr_bruto, lucro, ir, lucro_liquido, vlr_liq_resgate, rent_liq = calcula_retorno(ativo, vlr, prazo, tx)
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Valor bruto', f'R$ {vlr_bruto:.2f}')
            st.metric('Lucro líquido', f'R$ {lucro_liquido:.2f}')
        with col2:
            st.metric('Lucro bruto', f'R$ {lucro:.2f}')
            st.metric('Valor líquido de resgate', f'R$ {vlr_liq_resgate:.2f}')
        with col3:
            st.metric('Imposto de Renda', f'R$ {ir:.2f}')
            st.metric('Rentabilidade líquida', f'{rent_liq:.2f}%')   
    return ativo, vlr_liq_resgate, rent_liq

    
st.set_page_config(page_title='Comparador de Rentabilidade',
                    page_icon='🏅',
                    layout='wide')

st.title('Comparador de Rentabilidade')
st.markdown('---')

with st.spinner('Buscando dados atualizados...'):
    with st.container():
        col1, col2, col3 = st.columns(3)
        selic_ano = float(consulta_bc(432).iloc[-1].values)
        cdi_ano = float(consulta_bc(1178).iloc[-1:].values)
        ipca_ano = round(float(consulta_bc(433).iloc[-12:].sum().values), 2)
        with col1:
            st.metric('Selic Anual', f'{selic_ano:.2f}%')
        with col2:
            st.metric('CDI Anual', f'{cdi_ano:.2f}%')
        with col3:
            st.metric('IPCA Anual', f'{ipca_ano:.2f}%')
        
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        vlr = st.number_input('Valor da aplicação')
        prazo = st.number_input('Insira o prazo de vencimento (em meses)', step=1)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        with st.expander('Ativo 1', expanded=True):
            ativo1, ativo1_vlr_liq_resg, ativo1_rent_liq = comparativo('ativo1')
    with col2:
        with st.expander('Ativo 2', expanded=True):
            ativo2, ativo2_vlr_liq_resg, ativo2_rent_liq = comparativo('ativo2')

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    if ativo1_vlr_liq_resg > ativo2_vlr_liq_resg:
        with col2:
            st.metric(f'O {ativo1} é mais rentável, a diferença no resgate é de:', f'R$ {ativo1_vlr_liq_resg - ativo2_vlr_liq_resg:.2f}', f'{(ativo1_vlr_liq_resg / ativo2_vlr_liq_resg - 1):.2f}%')
        with col3: 
            st.metric('Diferença na rentabilidade:', f'{ativo1_rent_liq - ativo2_rent_liq:.2f}%', f'{(ativo1_rent_liq / ativo2_rent_liq - 1):.2f}%')
    else:
        with col2:
            st.metric(f'O {ativo2} é mais rentável, a diferença no resgate é de:', f'R$ {ativo2_vlr_liq_resg - ativo1_vlr_liq_resg:.2f}', f'{(ativo2_vlr_liq_resg / ativo1_vlr_liq_resg - 1):.2f}%')
        with col3: 
            st.metric('Diferença na rentabilidade:', f'{ativo2_rent_liq - ativo1_rent_liq:.2f}%', f'{(ativo2_rent_liq / ativo1_rent_liq - 1):.2f}%')


