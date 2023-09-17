import streamlit as st
 
def main():
    st.set_page_config(page_title='Robson Perdigão - Quantiq Finanças Quantitativas',
                       page_icon='📈',
                       initial_sidebar_state='expanded')
    st.sidebar.image('QUANTIQ.png')
    st.sidebar.markdown('---')
    
    col1, col2, col3, col4 = st.columns(4)
    st.markdown('---')
    with col1:
        st.image('QUANTIQ.png')

    with col2:
        st.markdown('# Robson Perdigão')
        st.markdown('## Assessor de Investimentos')
        st.write('InvestSmart')
    st.write("""Me chamo Robson Perdigão, sou Assessor de Investimentos na InvestSmart.
                 Investidor desde 2012, trader desde 2018 e Assessor desde 2020.
                 2023 foi o ano para entrar no mundo das Finanças Quantitativas com o objetivo de melhorar a performance dos meus investimentos e auxiliar os investidores a tomar melhores decisões.""")
    st.write('Escolha a opção no menu ao lado')
   
main()
