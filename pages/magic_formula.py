import streamlit as st
from src import utils


st.set_page_config(page_title='Magic Formula', 
                   page_icon='🪄',
                   layout='wide')
st.title('Magic Formula')
st.write("""Em 'The Little Book That Beats the Market' (A Fórmula Mágica de Joel Greenblatt para bater o mercado de ações, tradução para o Brasil), Joel Greenblatt compartilha uma estratégia de investimento que desafia a sabedoria convencional de Wall Street. Sua abordagem gira em torno da chamada "fórmula mágica", uma fórmula simples que utiliza dois critérios-chave para selecionar ações. 
         O primeiro é o Rendimento de Lucros (Earning Yield), que mede o quão baratas as ações são em relação aos lucros que geram. 
         O segundo é o Retorno sobre o Capital (Return on Capital), que avalia a eficácia das empresas na alocação de capital.
         Greenblatt argumenta que, ao classificar as ações com base nesses critérios e investir nas melhores classificadas, os investidores podem superar consistentemente o desempenho do mercado. Uma das grandes vantagens dessa estratégia é sua simplicidade. Mesmo investidores iniciantes podem entender e aplicar a fórmula mágica com facilidade.""")
st.write("""O autor também enfatiza a importância de manter uma perspectiva de longo prazo. Ele destaca que, embora a estratégia possa não funcionar bem a cada trimestre ou ano, ao longo de vários anos, ela tende a superar o mercado de forma impressionante. Greenblatt sustenta essa afirmação ao fornecer uma série de exemplos históricos de sucesso da fórmula mágica.
         No entanto, ele também faz questão de alertar que nenhum método de investimento é infalível e que os investidores ainda enfrentam riscos. A estratégia de Greenblatt não se concentra na diversificação, o que significa que os investidores podem estar expostos a riscos específicos de empresas individuais.
         Em resumo, 'The Little Book That Beats the Market' oferece uma abordagem clara e acessível para investir com sabedoria, baseada na seleção de ações de empresas de qualidade a preços atrativos. É uma estratégia que se baseia em princípios sólidos, mas que requer disciplina e paciência para ser eficaz a longo prazo. O livro é uma leitura valiosa para investidores interessados em uma abordagem diferente e potencialmente lucrativa para o mercado de ações.""")
st.write('Eu fiz questão de adaptar a Fórmula Mágica para o mercado brasileiro e deixar de forma ainda mais simples a obtenção das ações de acordo com os critérios do livro.')
st.write('***Lembrando que os ativos aqui listados não são recomendação de investimentos.***')
st.write("""Altere os critérios abaixo conforme sua vontade, os valores padrões já consideram o recomendado no livro.""")
st.markdown('---')


col1, col2 = st.columns(2)
with col1:
    liquidez = st.slider('Qual a liquidez mínima desejada? (Ideal maior que 1.000.000)', 100000, 5000000, value=1000000, step=100000)
with col2:
    qtd_ativos = st.slider('Quantos ativos você deseja no Ranking Final?', 3, 30, value=15)

botao = st.button('Botão Mágico')
    
if botao:
    with st.spinner('Gerando o ranking da Magic Formula...'):
        ranking = utils.magic_formula(liquidez, qtd_ativos)
        
        st.markdown('**Ranking final da Magic Formula:**')
        st.write('_Selecione o ativo para ver mais informações_')
        
        col1, col2 = st.columns(2)
        with col1:
            for ativo in ranking.index:
                with st.expander(ativo, expanded=False):
                    info_papel = utils.detalhes_ativo_summary(ativo)
                    utils.detalhes_ativo_magic_formula(info_papel)