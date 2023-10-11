import streamlit as st
from st_pages import Page, Section, show_pages
 
def main():
    st.set_page_config(page_title='Robson Perdigão - Finanças Quantitativas',
                        page_icon='📈',
                        initial_sidebar_state='expanded',
                        layout='wide')

    show_pages(
        [
            Page('home.py', 'Home', '🏠'),
            Page('pages/Raio-X Financeiro.py', 'Raio-X Financeiro', '📊'),
            Page('is/docs/fpclient.py', 'Exemplo FPClient', '📝'),
            Page('pages/comparador_rentabilidade.py', 'Comparador de Rentabilidade', '🏅'),
            #Page('quant/analise_portfolio.py', 'Análise de Carteira', '📈'),
            Page('pages/calculadora.py', 'Calculadora Financeira', '🧮'),
            Page('pages/magic-formula.py', 'Magic Formula', '🪄'),
            Page('pages/value_investing.py', 'Ben Graham - Value Investing', '🔎'),
            Page('pages/fortuna_acoes.py', 'Método Bazin', '🎯'),
            Page('pages/fundos_investimentos.py', 'Mapa de Fundos de Investimentos', '🪙'),
            Section('PMF', '👨🏻‍💻'),
            Page('pmf/fundamentos.py', 'Fundamentos', '📊'),
            Page('pmf/panorama-mercado.py', 'Panorama de Mercado', '📰'),
            Page('pmf/mapa-retornos.py', 'Mapa de Retornos Mensais', '📈')
        ]
    )


    col1, col2, col3, col4 = st.columns(4)
    st.markdown('---')
    with col1:
        st.image('img/foto_perfil.png')
    with col2:
        st.markdown('# Robson Perdigão')
        st.markdown('## Assessor de Investimentos')
        st.write("[InvestSmart](https://investsmart.com.br/robson-perdigao/)")
        st.write(" LinkedIn: [@robsonperdigao](https://www.linkedin.com/in/robsonperdigao/)")
    st.write("""Me chamo Robson Perdigão, sou Assessor de Investimentos na InvestSmart.
                    Investidor desde 2012, trader desde 2018 e Assessor desde 2020.
                    2023 foi o ano para entrar no mundo das Finanças Quantitativas com o objetivo de melhorar a performance dos meus investimentos e auxiliar os investidores a tomar melhores decisões.""")
    st.write("""Finanças quantitativas é uma disciplina que se concentra na aplicação de modelos matemáticos, finanças e tecnologia para analisar e tomar decisões financeiras. Essa abordagem usa dados históricos e algoritmos para avaliar riscos, precificar ativos e otimizar portfólios, tornando-se uma ferramenta valiosa para investidores e profissionais financeiros na tomada de decisões baseadas em evidências numéricas.
                No menu ao lado você encontra as principais ferramentas para obter informações sobre os mais diversos ativos, tirar insights e analisar portfolios da forma que deseja.""")
    st.write('< Escolha a opção no menu ao lado')
    st.markdown('---')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(" Linktree: [@perdigao](https://linktr.ee/perdigao)", icon='📱')
        st.success(" GitHub: [@robsonperdigao](https://github.com/robsonperdigao)", icon='🤖')
    with col2:    
        st.info(" LinkedIn: [@robsonperdigao](https://www.linkedin.com/in/robsonperdigao/)", icon='🧔🏻‍♂️')
        st.error(" YouTube: [@robson.perdigao](https://www.youtube.com/@robson.perdigao)", icon='📹')
        st.warning(" [Abra sua conta](https://bit.ly/rp_abrirconta) na XP Investimentos e tenha a minha assessoria")
    with col3:
        st.info(" TikTok: [@robson.perdigao](https://www.tiktok.com/@robson.perdigao)", icon='🤳🏻')
        st.warning(" Instagram: [@robson.perdigao](https://www.instagram.com/robson.perdigao/)", icon='📸')

main()
