import streamlit as st
import fundamentus as fd

st.set_page_config(page_title='Análise Fundamentalista', page_icon='📊')
st.title('Análise Fundamentalista')
    
lista_tickers = fd.list_papel_all()
comparar = st.checkbox('Comparar 2 ativos')

col1, col2 = st.columns(2)

with col1:
    with st.expander('', expanded=True):
        papel1 = st.selectbox('Selecione o Papel', lista_tickers)
        info_papel1 = fd.get_detalhes_papel(papel1)
        st.write('**Empresa:**', info_papel1['Empresa'][0])
        st.write('**Setor:**', info_papel1['Setor'][0])
        st.write('**Segmento:**', info_papel1['Subsetor'][0])
        st.write('**Valor de Mercado:**', f"R$ {info_papel1['Valor_de_mercado'][0]:,.2f}")
        st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel1['Patrim_Liq'][0]):,.2f}")
        st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel1['Receita_Liquida_12m'][0]):,.2f}")
        st.write('**Dívida Bruta:**', f"R$ {float(info_papel1['Div_Bruta'][0]):,.2f}")
        st.write('**Dívida Líquida:**', f"R$ {float(info_papel1['Div_Liquida'][0]):,.2f}")
        st.write('**P/L:**', f"{float(info_papel1['PL'][0]):,.2f}")
        st.write('**Dividend Yield:**', f"{info_papel1['Div_Yield'][0]}")

if comparar:
    with col2:
        with st.expander('', expanded=True):
            papel2 = st.selectbox('Selecione o 2º Papel', lista_tickers)
            info_papel2 = fd.get_detalhes_papel(papel2)
            st.write('**Empresa:**', info_papel2['Empresa'][0])
            st.write('**Setor:**', info_papel2['Setor'][0])
            st.write('**Segmento:**', info_papel2['Subsetor'][0])
            st.write('**Valor de Mercado:**', f"R$ {info_papel2['Valor_de_mercado'][0]:,.2f}")
            st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel2['Patrim_Liq'][0]):,.2f}")
            st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel2['Receita_Liquida_12m'][0]):,.2f}")
            st.write('**Dívida Bruta:**', f"R$ {float(info_papel2['Div_Bruta'][0]):,.2f}")
            st.write('**Dívida Líquida:**', f"R$ {float(info_papel2['Div_Liquida'][0]):,.2f}")
            st.write('**P/L:**', f"{float(info_papel2['PL'][0]):,.2f}")
            st.write('**Dividend Yield:**', f"{info_papel2['Div_Yield'][0]}")

