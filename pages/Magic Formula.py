import streamlit as st
import requests
import pandas as pd
import fundamentus as fd

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
        
        
        def dados_ativo(papel):
            info_papel = fd.get_detalhes_papel(papel)
            st.write('**Empresa:**', info_papel['Empresa'][0])
            st.write('**Setor:**', info_papel['Setor'][0])
            st.write('**Segmento:**', info_papel['Subsetor'][0])
            st.markdown('---')
            st.write('**Cotação:**', f"R$ {float(info_papel['Cotacao'][0]):,.2f}")
            st.write('**Data Última Cotação:**', info_papel['Data_ult_cot'][0])
            st.write('**Liquidez Média 2 Meses:**', info_papel['Vol_med_2m'][0])
            st.write('**EV/EBITDA:**', f"{float(info_papel['EV_EBITDA'][0])/100:,.2f}")
            st.write('**ROIC:**', info_papel['ROIC'][0])
            st.write('**Valor de Mercado:**', f"R$ {float(info_papel['Valor_de_mercado'][0]):,.2f}")
            st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel['Patrim_Liq'][0]):,.2f}")
            st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel['Receita_Liquida_12m'][0]):,.2f}")
            st.write('**Lucro Líquido 12m:**', f"R$ {float(info_papel['Lucro_Liquido_12m'][0]):,.2f}")
            st.write('**Dívida Bruta:**', f"R$ {float(info_papel['Div_Bruta'][0]):,.2f}")
            st.write('**Dívida Líquida:**', f"R$ {float(info_papel['Div_Liquida'][0]):,.2f}")
            st.write('**P/L:**', f"{float(info_papel['PL'][0])/100:,.2f}")
            st.write('**P/VP:**', f"{float(info_papel['PVP'][0])/100:,.2f}")
            st.write('**Dividend Yield:**', info_papel['Div_Yield'][0])   
            st.write('**Margem Bruta:**', info_papel['Marg_Bruta'][0])  
            st.write('**Margem Líquida:**', info_papel['Marg_Liquida'][0]) 
            st.markdown('---') 
            st.write('**Último Balanço Processado:**', info_papel['Ult_balanco_processado'][0]) 
        
        col1, col2 = st.columns(2)
        with col1:
            for acao in tabela.index:
                with st.expander(acao, expanded=False):
                    dados_ativo(acao)