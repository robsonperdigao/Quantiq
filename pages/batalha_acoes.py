import streamlit as st
import pandas as pd
from src import utils

st.set_page_config(page_title='Batalha de Ações', 
                   page_icon='🥊',
                   layout='wide')
st.title('Batalha de Ações')
st.markdown('---')


st.write("""A "Batalha de Ações" é uma ferramenta que permite comparar dois ativos financeiros de forma detalhada, utilizando uma ampla gama de indicadores financeiros. Esta funcionalidade é particularmente útil para investidores e analistas que desejam avaliar a saúde financeira e o desempenho de diferentes empresas.

**Aqui está como a batalha funciona:**

**Seleção dos Ativos:** Primeiro, o usuário seleciona o setor que gostaria de comparar os ativos e depois escolhe entre 2 empresas do setor escolhido. Cada ativo é representado por uma série de indicadores financeiros, que incluem, entre outros, o preço de lucro (PL), o preço/valor (PVP), o preço/EBIT (PEBIT), a rentabilidade dos ativos (PSR), entre outros.

**Comparação dos Indicadores:** A ferramenta compara os valores desses indicadores entre os dois ativos. Para cada indicador, a ferramenta determina o vencedor com base em critérios específicos:

**Para indicadores onde um valor maior é preferível:** Dividend Yield, Crescimento de Receita dos Últimos 5 anos, Lucro Por Ação (LPA), Margem Bruta, Margem EBIT, Margem Líquida, EBIT/Ativo, ROIC e ROE.
O ativo com o maior valor ganha um ponto.

**Para indicadores onde um valor menor é preferível:**  Preço/Lucro (PL), Preço/Valor Patrimonial (PVP), Preço/EBIT (PEBIT), Price Sales Ratio (PSR), Preço/Ativos, Preço/Capital de Giro, Preço/Ativo Circulante Líquido, EV/EBITDA, EV/EBIT, Valor por Ação (VPA), Liquidez Corrente, Dívida Bruta/Patrimônio Líquido, Giro Ativos.
O ativo com o menor valor ganha um ponto.

**Determinação do Vencedor:** O ativo que ganha mais pontos é declarado o vencedor da batalha. Isso significa que, com base nos critérios especificados, o ativo vencedor é considerado o melhor em termos de saúde financeira e desempenho entre os dois ativos comparados.

*Isso não é recomendação de investimentos*.""")

setores = utils.lista_setores()
setor = st.selectbox('Selecione o setor', setores.values(), placeholder='Digite ou selecione o setor')
for key, value in setores.items():
    if setor == value:
        num_setor = key

lista_tickers = utils.lista_ativos_setores_b3(num_setor)

col1, col2 = st.columns(2)

with st.form('batalha'):
    submited = st.form_submit_button("It's tiiiiime!")
    with col1:
            ativo1 = st.selectbox('Selecione o Desafiador', lista_tickers, key='ativo1')
    with col2:
            ativo2 = st.selectbox('Selecione o Desafiado', lista_tickers, key='ativo2')

    if submited:
        if ativo1 == ativo2:
             st.warning('Selecione 2 ativos diferentes', icon="⚠️")
             pass
        else:
            with col1:
                info_papel1 = utils.detalhes_ativo_summary(ativo1)
                utils.detalhes_ativo(info_papel1)

            with col2:
                info_papel2 = utils.detalhes_ativo_summary(ativo2)
                utils.detalhes_ativo(info_papel2)

            df = pd.merge(info_papel1, info_papel2, how='outer')
            st.dataframe(df)
            vencedor, perdedor, pontos_vencedor, pontos_perdedor = utils.vencedor_batalha(df=df)
            col1, col2, col3, col4 = st.columns(4)
            with col2:
                st.metric('Vencedor', vencedor)
                st.metric('Pontos', pontos_vencedor)
            with col3:
                st.metric('Perdedor', perdedor)
                st.metric('Pontos', pontos_perdedor)
        
