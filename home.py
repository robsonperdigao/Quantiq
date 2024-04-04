import streamlit as st
from st_pages import Page, Section, show_pages, add_indentation
 
def main():
    st.set_page_config(page_title='Quantiq Trade - Finanças Quantitativas',
                        page_icon='📈',
                        initial_sidebar_state='expanded',
                        layout='wide')
    #add_indentation()

    show_pages(
        [
            Page('home.py', 'Home', '🏠'),
            #Section("Planejamento", '📊'),
            Page('pages/planner.py', 'Planejamento Financeiro', '📊'),
            Page('pages/planner_ex.py', 'Exemplo Plan. Financeiro', '📝'),
            #Section("Quantiq", '💲'),
            Page('pages/opcoes.py', 'Estratégias com Opções', '❇️'),
            Page('pages/comparador_rentabilidade.py', 'Comparador de Rentabilidade', '🏅'),
            #Page('pages/quant/analise_portfolio.py', 'Análise de Carteira', '📈'),
            #Page('pages/quant/analise_setorial.py', 'Análise Setorial', '🗄️'),
            #Page('pages/quant/algotrading.py', 'Algotrading/Robô Trader', '🗄️'),
            #Page('pages/quant/factor_investing.py', 'Factor Investing', '🗄️'),
            #Page('pages/quant/quant_finance.py', 'Finanças Quantitativas', '🗄️'),
            Page('pages/calculadora.py', 'Calculadora Financeira', '🧮'),
            Page('pages/magic_formula.py', 'Magic Formula', '🪄'),
            Page('pages/value_investing.py', 'Ben Graham - Value Investing', '🔎'),
            Page('pages/fortuna_acoes.py', 'Método Bazin', '🎯'),
            Page('pages/fundos_investimentos.py', 'Mapa de Fundos de Investimentos', '🪙'),
            #Page('pages/quant/remuneracao.py', 'Remuneração', '🗄️'),
            Page('pages/fundamentos.py', 'Fundamentos', '📊'),
            Page('pages/batalha_acoes.py', 'Batalha de Ações', '🥊'),
            Page('pages/panorama_mercado.py', 'Panorama de Mercado', '📰'),
            #Page('pages/pmf/mapa-retornos.py', 'Mapa de Retornos Mensais', '📈'),
            Page('pages/about.py', 'About', '🪪')
        ]
    )

    col1, col2, col3 = st.columns(3)
    st.markdown('---')
            
    with col2:
        st.image('img/QUANTIQ.png', use_column_width=True)
            
    st.write("""A Quantiq Trade é uma empresa especializada em soluções financeiras. Nossos serviços abrangem análise quantitativa, estratégias automatizadas, pesquisa e modelagem de estratégias, consultoria financeira para investidores. 
             Oferecemos modelos de investimento avançados e consultoria financeira para auxiliar nossos clientes a tomar decisões embasadas e otimizar suas estratégias de investimento. Combinamos tecnologia com expertise financeira para fornecer soluções inovadoras e eficazes para as necessidades financeiras de nossos clientes.""")
    st.write("Do desenvolvimento de modelos de investimento com machine learning à orientação estratégica, nosso nome reflete nossa busca incansável por resolver os desafios financeiros mais complexos de maneira inteligente e eficaz.")
    st.write("⬅️ Escolha uma opção no menu ao lado")
    
main()
