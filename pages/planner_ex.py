import streamlit as st

st.set_page_config(page_title='Exemplo Planejamento Financeiro',
                    page_icon='📝',
                    layout='wide')

st.title('Exemplo Planejamento Financeiro')
st.write('Exemplo Planejamento Financeiro preenchido e abaixo o PDF do Diagnóstico do Cliente para download')

st.markdown('---')

st.image('pages/docs/plnr1.png')
st.image('pages/docs/plnr2.png')
st.image('pages/docs/plnr3.png')
st.image('pages/docs/plnr4.png')
st.image('pages/docs/plnr5.png')
st.image('pages/docs/plnr6.png')
st.image('pages/docs/plnr7.png')
st.image('pages/docs/plnr8.png')
st.image('pages/docs/plnr9.png')
st.image('pages/docs/plnr10.png')

with open('pages/docs/diagnostico.pdf', 'rb') as file:
    btn = st.download_button(
            label='Baixe o PDF do Diagnóstico do Cliente',
            data=file,
            file_name='Diagnóstico do Cliente.pdf',
            mime='pdf'
          )


