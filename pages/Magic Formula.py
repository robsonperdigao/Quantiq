import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title='Magic Formula', 
                   page_icon='🎯',
                   layout='wide')
st.title('Magic Formula')
st.write("""Em 'The Little Book That Beats the Market' (A Fórmula Mágica de Joel Greenblatt para bater o mercado de ações, tradução para o Brasil), Joel Greenblatt compartilha uma estratégia de investimento que desafia a sabedoria convencional de Wall Street. Sua abordagem gira em torno da chamada "fórmula mágica", uma fórmula simples que utiliza dois critérios-chave para selecionar ações. 
         O primeiro é o Rendimento de Lucros (Earning Yield), que mede o quão baratas as ações são em relação aos lucros que geram. 
         O segundo é o Retorno sobre o Capital (Return on Capital), que avalia a eficácia das empresas na alocação de capital.
         Greenblatt argumenta que, ao classificar as ações com base nesses critérios e investir nas melhores classificadas, os investidores podem superar consistentemente o desempenho do mercado. Uma das grandes vantagens dessa estratégia é sua simplicidade. Mesmo investidores iniciantes podem entender e aplicar a fórmula mágica com facilidade.""")
st.write("""O autor também enfatiza a importância de manter uma perspectiva de longo prazo. Ele destaca que, embora a estratégia possa não funcionar bem a cada trimestre ou ano, ao longo de vários anos, ela tende a superar o mercado de forma impressionante. Greenblatt sustenta essa afirmação ao fornecer uma série de exemplos históricos de sucesso da fórmula mágica.
         No entanto, ele também faz questão de alertar que nenhum método de investimento é infalível e que os investidores ainda enfrentam riscos. A estratégia de Greenblatt não se concentra na diversificação, o que significa que os investidores podem estar expostos a riscos específicos de empresas individuais.
         Em resumo, 'The Little Book That Beats the Market' oferece uma abordagem clara e acessível para investir com sabedoria, baseada na seleção de ações de empresas de qualidade a preços atrativos. É uma estratégia que se baseia em princípios sólidos, mas que requer disciplina e paciência para ser eficaz a longo prazo. O livro é uma leitura valiosa para investidores interessados em uma abordagem diferente e potencialmente lucrativa para o mercado de ações.""")
st.write("""Eu fiz questão de adaptar a Fórmula Mágica para o mercado brasileiro e deixar de forma ainda mais simples a obtenção das ações de acordo com os critérios do livro.
         Lembrando que os ativos aqui listados não são recomendação de invesitmentos.""")
st.write("""Altere os critérios abaixo conforme sua vontade, os valores padrões já consideram o recomendado no livro.""")

liquidez = st.slider('Qual a liquidez mínima desejada? (Ideal maior que 1.000.000)', 100000, 5000000, value=1000000, step=100000)
qtd_ativos = st.slider('Quantos ativos você deseja no Ranking Final?', 3, 30, value=15)

botao = st.button('Botão Mágico')
    
if botao:
    with st.spinner('Gerando o ranking da Magic Formula...'):    
        url = 'http://www.fundamentus.com.br/resultado.php'
        header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        r = requests.get(url, headers=header)
        tabela = pd.read_html(r.text,  decimal=',', thousands='.')[0]
        
        for coluna in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
            tabela[coluna] = tabela[coluna].str.replace('.', '')
            tabela[coluna] = tabela[coluna].str.replace(',', '.')
            tabela[coluna] = tabela[coluna].str.rstrip('%').astype('float') / 100
        
        
        tabela = tabela[['Papel', 'Cotação', 'EV/EBIT', 'ROIC', 'Liq.2meses', 'P/L']]
        tabela['Empresa'] = tabela['Papel'].str[:4]
        tabela = tabela.drop_duplicates(subset='Empresa')
        tabela = tabela.set_index('Papel')
        tabela = tabela[tabela['Liq.2meses'] > liquidez]
        tabela = tabela[tabela['P/L'] > 0]
        tabela = tabela[tabela['EV/EBIT'] > 0]
        tabela = tabela[tabela['ROIC'] > 0]
        tabela = tabela.drop(columns = ['Empresa', 'P/L', 'Liq.2meses'])
        tabela['RANKING_EV/EBIT'] = tabela['EV/EBIT'].rank(ascending = True)
        tabela['RANKING_ROIC'] = tabela['ROIC'].rank(ascending = False)
        tabela['RANKING_TOTAL'] = tabela['RANKING_EV/EBIT'] + tabela['RANKING_ROIC']
        tabela = tabela.sort_values('RANKING_TOTAL')
        tabela = tabela.head(qtd_ativos)
            
        ranking = tabela.index
        ranking = '\n'.join(f'{i+1}. {acao}' for i, acao in enumerate(ranking))
        st.markdown('**Ranking final da Magic Formula:**')
        st.write(ranking)