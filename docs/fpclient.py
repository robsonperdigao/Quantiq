import streamlit as st

st.set_page_config(page_title='Exemplo FPClient Preenchido',
                    page_icon='📝',
                    layout='wide')

st.title('Exemplo FPClient Preenchido')
st.write('Exemplo do FPClient preenchido e abaixo o PDF do Diagnóstico do Cliente para download')

st.markdown('---')

st.image('docs/fp1.png')
st.image('docs/fp2.png')
st.image('docs/fp3.png')
st.image('docs/fp4.png')
st.image('docs/fp5.png')
st.image('docs/fp6.png')
st.image('docs/fp7.png')
st.image('docs/fp8.png')
st.image('docs/fp9.png')
st.image('docs/fp10.png')

with open('docs/diagnostico.pdf', 'rb') as file:
    btn = st.download_button(
            label='Baixe o PDF do Diagnóstico do Cliente',
            data=file,
            file_name='diagnostico.pdf',
            mime='pdf'
          )


