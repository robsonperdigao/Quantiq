import streamlit as st

st.set_page_config(page_title='Exemplo FPClient Preenchido',
                    page_icon='📝',
                    layout='wide')

st.title('Exemplo FPClient Preenchido')
st.write('Exemplo do FPClient preenchido e abaixo o PDF do Diagnóstico do Cliente para download')

st.markdown('---')

st.image('pages/is/docs/fp1.png')
st.image('pages/is/docs/fp2.png')
st.image('pages/is/docs/fp3.png')
st.image('pages/is/docs/fp4.png')
st.image('pages/is/docs/fp5.png')
st.image('pages/is/docs/fp6.png')
st.image('pages/is/docs/fp7.png')
st.image('pages/is/docs/fp8.png')
st.image('pages/is/docs/fp9.png')
st.image('pages/is/docs/fp10.png')

with open('pages/is/docs/diagnostico.pdf', 'rb') as file:
    btn = st.download_button(
            label='Baixe o PDF do Diagnóstico do Cliente',
            data=file,
            file_name='Diagnóstico do Cliente.pdf',
            mime='pdf'
          )


