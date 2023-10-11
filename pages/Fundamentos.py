import streamlit as st
import fundamentus as fd

st.set_page_config(page_title='Análise Fundamentalista', 
                   page_icon='📊',
                   layout='wide')
st.title('Análise Fundamentalista')
st.markdown('---')

def dados_ativo(papel):
    info_papel = fd.get_detalhes_papel(papel)
    st.write('**Empresa:**', info_papel['Empresa'][0])
    st.write('**Setor:**', info_papel['Setor'][0])
    st.write('**Segmento:**', info_papel['Subsetor'][0])
    st.markdown('---')
    st.write('**Cotação:**', f"R$ {float(info_papel['Cotacao'][0]):,.2f}")
    st.write('**Data Última Cotação:**', info_papel['Data_ult_cot'][0])
    st.write('**Valor de Mercado:**', f"R$ {float(info_papel['Valor_de_mercado'][0]):,.2f}")
    st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel['Patrim_Liq'][0]):,.2f}")
    st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel['Receita_Liquida_12m'][0]):,.2f}")
    st.write('**Lucro Líquido 12m:**', f"R$ {float(info_papel['Lucro_Liquido_12m'][0]):,.2f}")
    st.write('**Dívida Bruta:**', f"R$ {float(info_papel['Div_Bruta'][0]):,.2f}")
    st.write('**Dívida Líquida:**', f"R$ {float(info_papel['Div_Liquida'][0]):,.2f}")
    st.write('**P/L:**', f"{float(info_papel['PL'][0])/100:,.2f}")
    st.write('**P/VP:**', f"{float(info_papel['PVP'][0])/100:,.2f}")
    st.write('**Dividend Yield:**', info_papel['Div_Yield'][0])   
    st.write('**Margem Bruta:**', info_papel['Marg_Bruta'][0])  
    st.write('**Margem Líquida:**', info_papel['Marg_Liquida'][0]) 
    st.markdown('---') 
    st.write('**Último Balanço Processado:**', info_papel['Ult_balanco_processado'][0]) 
        
lista_tickers = fd.list_papel_all()
comparar = st.checkbox('Comparar 2 ativos')

col1, col2 = st.columns(2)

with col1:
    with st.expander('', expanded=True):
        papel1 = st.selectbox('Selecione o Papel', lista_tickers)
        dados_ativo(papel1)

if comparar:
    with col2:
        with st.expander('', expanded=True):
            papel2 = st.selectbox('Selecione o 2º Papel', lista_tickers)
            dados_ativo(papel2)