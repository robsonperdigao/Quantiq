import streamlit as st
import numpy_financial as npf

st.set_page_config(page_title='Calculadora Financeira',
                   page_icon='🧮',
                   layout='wide')
st.title('Calculadora Financeira')

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    juros = st.checkbox('Converte Taxa de Juros Mensal', True)
    tempo_ap_unico = st.checkbox('Descobrir Tempo com Aporte Único', True)
with col2:
    juros_ano = st.checkbox('Converte Taxa de Juros Anual', True)
    tempo_ap_recorr = st.checkbox('Descobrir Tempo com Aporte Recorrente', True)
with col3:
    taxa_patr = st.checkbox('Descobrir Taxa de Juros', True)
with col4:
    aporte_unico = st.checkbox('Descobrir Valor de Aporte Único', True)
with col5:
    aporte_recorr = st.checkbox('Descobrir Valor de Aportes Recorrentes', True)
st.markdown('---')


with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        if juros:
            st.subheader('Converte Taxa de Juros Mensal')
            j_i = st.number_input('Insira a taxa de juros anual') / 100
            j_n = st.number_input('Insira o número de meses pra calcular', 1, 12, step=1)
            j_juro_mensal = ((1 + j_i) ** (j_n/12) - 1) * 100
            st.write(f'Taxa de Juros no período {j_juro_mensal:.2f}%')

    with col2:
        if juros_ano:
            st.subheader('Converte Taxa de Juros Anual')
            ja_i = st.number_input('Insira a taxa de juros mensal') / 100
            ja_juros_anual = ((1 + ja_i) ** 12 - 1) * 100
            st.write(f'Taxa de juros anual {ja_juros_anual:.2f}%')

    with col3:        
        if taxa_patr:
            st.subheader('Descobrir Taxa de Juros')
            ptr_fv = st.number_input('Insira o valor futuro')
            ptr_pv = st.number_input('Insira o valor atual, caso haja')
            ptr_pmt = st.number_input('Insira o valor do aporte')
            ptr_n = st.number_input('Insira o período de cálculo', step=1)
            descob_taxa = npf.rate(ptr_n, -ptr_pmt, -ptr_pv, ptr_fv)
            st.write(f'Taxa de juros no período {descob_taxa:.2f}%')
st.markdown('---')

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        if aporte_unico:
            st.subheader('Descobrir Valor de Aporte Único')
            apu_fv = st.number_input('Insira o valor futuro', key='apu_fv')
            apu_i = st.number_input('Insira a taxa de juros no período', key='apu_i') / 100
            apu_n = st.number_input('Insira o período', key='apu_n')
            vlr_aporte = npf.pv(apu_i, apu_n, 0, -apu_fv,)
            st.write(f'Valor de Aporte Único R$ {vlr_aporte:.2f}')

    with col2:
        if aporte_recorr:
            st.subheader('Descobrir Valor de Aportes Recorrentes')
            apr_fv = st.number_input('Insira o valor futuro', key='apr_fv')
            apr_pv = st.number_input('Insira o patrimônio atual, caso haja')
            apr_i = st.number_input('Insira a taxa de juros no período', key='apr_i') / 100
            apr_n = st.number_input('Insira o período', key='apr_n')
            vlr_aprt_recorr = npf.pmt(apr_i, apr_n, -apr_pv, -apr_fv)
            st.write(f'Valor de Aportes Recorrentes R$ {vlr_aprt_recorr:.2f}')

    with col3:
        if tempo_ap_unico:
            st.subheader('Descobrir Tempo com Aporte Único')
            tapu_fv = st.number_input('Insira o valor futuro', key='tapu_fv')
            tapu_pv = st.number_input('Insira o patrimônio atual, caso haja', key='tapu_pv')
            tapu_i = st.number_input('Insira a taxa de juros no período', key='tapu_i') / 100
            tmp_ap_unico = npf.nper(tapu_i, 0, -tapu_pv, tapu_fv)
            st.write(f'Prazo necessário para atingir R$ {tapu_fv:.2f} é de {tmp_ap_unico:.1f} períodos')
st.markdown('---')

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        if tempo_ap_recorr:
            st.subheader('Descobrir Tempo com Aporte Recorrente')
            tapr_fv = st.number_input('Insira o valor futuro', key='tapr_fv')
            tapr_pv = st.number_input('Insira o patrimônio atual, caso haja', key='tapr_pv')
            tapr_pmt = st.number_input('Insira o valor do aporte recorrente', key='tapr_pmt')
            tapr_i = st.number_input('Insira a taxa de juros no período', key='tapr_i') / 100
            tmp_ap_recorr = npf.nper(tapr_i, -tapr_pmt, -tapr_pv, tapr_fv)
            st.write(f'Prazo necessário para atingir R$ {tapr_fv:.2f} é de {tmp_ap_recorr:.1f} períodos')

st.markdown('---')
    