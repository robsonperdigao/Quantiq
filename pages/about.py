import streamlit as st

 
def main():
    st.set_page_config(page_title='About - Quantiq Trade',
                        page_icon='🪪',
                        initial_sidebar_state='expanded',
                        layout='wide')
    
    col1, col2, col3, col4 = st.columns(4)
    st.markdown('---')
    with col1:
        st.image('img/foto_perfil.png')
    with col2:
        st.markdown('# Robson Perdigão')
        st.markdown('### Finanças Quantitativas')
        #st.write(" LinkedIn: [@robsonperdigao](https://www.linkedin.com/in/robsonperdigao/)")
    st.write("Me chamo Robson Perdigão, Engenheiro Civil de formação, Investidor desde 2012, Trader desde 2018, Assessor de Investimentos desde 2020 e um apaixonado pelo mercado financeiro e tecnologia.") 
    st.write("Inicialmente decidi unir minha paixão por investimentos com o uso da tecnologia para otimizar os meus investimentos e obtive resultados acima da média e com pouca interferência humana na tomada de decisão.")
    st.write("Com os resultados positivos e experiência com Assessoria de Investimentos, nasceu a Quantiq Trade com o foco em proporcionar otimizações e ganhos acima da média aos investidores.")         
    
    st.markdown('---')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(" Linktree: [@perdigao](https://linktr.ee/perdigao)", icon='📱')
        st.success(" GitHub: [@robsonperdigao](https://github.com/robsonperdigao)", icon='🤖')
    with col2:    
        st.info(" LinkedIn: [@robsonperdigao](https://www.linkedin.com/in/robsonperdigao/)", icon='🧔🏻‍♂️')
        st.error(" YouTube: [@robson.perdigao](https://www.youtube.com/@robson.perdigao)", icon='📹')
    with col3:
        st.info(" TikTok: [@robson.perdigao](https://www.tiktok.com/@robson.perdigao)", icon='🤳🏻')
        st.warning(" Instagram: [@robson.perdigao](https://www.instagram.com/robson.perdigao/)", icon='📸')

main()
