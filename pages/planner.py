import streamlit as st
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import numpy_financial as npf
import yfinance as yf
from matplotlib.ticker import FuncFormatter
from fpdf import FPDF
from io import BytesIO
import tempfile
from src import utils

st.set_page_config(page_title='Planejamento Financeiro', 
                   page_icon='📊',
                   layout='wide')
st.title('Planejamento Financeiro')

st.write("""Um bom planejamento financeiro oferece uma abordagem abrangente para ajudar você a atingir seus objetivos no curto, médio e longo prazo. Nesta página você poderá inserir informações sobre suas finanças pessoais, incluindo receitas, despesas, investimentos atuais e seus planos de aposentadoria desejados, e automaticamente será realizada uma projeção precisa da sua situação financeira.
Usando algoritmos avançados, é calculada sua capacidade de poupança e projetado como seu patrimônio evoluirá ao longo do tempo. Isso é apresentado de forma visual em gráficos fáceis de entender, permitindo que você visualize seu caminho financeiro. Além disso, é possível visualizar a evolução do seu patrimônio após a aposentadoria, seja mantendo um patrimônio que gera renda vitalícia ou usando-o até os 100 anos.
Futuramente será incluída a funcionalidade de Asset Alocation, que é basicamente como sua carteira fica melhor distribuída de acordo com o seu perfil e objetivos, ajudando a maximizar seu potencial de retorno e minimizar riscos.
Através desse raio-X financeiro você terá uma visão clara e estratégica de suas finanças, permitindo que tome decisões informadas e trabalhe em direção a um futuro financeiro sólido e seguro. Estou aqui para ajudá-lo a alcançar seus objetivos financeiros com confiança e clareza.

Preencha as informações abaixo:""")
st.markdown('---')


@st.cache_data
def calcula_patrimonio(idade, idade_indep, patrim_atual, cap_poup_ano, renda_mensal_indep, tx_juro_ano): 
    anos_invest = idade_indep - idade
    meses_invest = anos_invest * 12
    meses_consumo = anos_consumo * 12
    juro_mensal = (1+tx_juro_ano)**(1/12)-1
    patrim_acumulado = npf.fv(tx_juro_ano, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    tempo_consumo_meses = round(float(npf.nper(juro_mensal, renda_mensal_indep, -patrim_acumulado)),0)
    pat_vitalicio = round(renda_mensal_indep / juro_mensal, 2)
    parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -patrim_atual, -pat_vitalicio).round(2)
    pat_consumo = npf.pv(juro_mensal, meses_consumo, -renda_mensal_indep, 0).round(2)
    parcela_consumo = npf.pmt(juro_mensal, meses_invest, 0, -pat_consumo).round(2)
    patrim_consumo = npf.fv(tx_juro_ano, anos_invest, -parcela_consumo * 12, -patrim_atual)

    evo_ano = list(range(0, anos_invest + 1))
    df = pd.DataFrame(columns=['Idade', 'Valor Investido', 'Patrimônio Acumulado', 
                                        'Vitalício', 'Consumo Patrimônio'], 
                                index=evo_ano)
    for i in evo_ano:
        valor_investido_ano = npf.fv(0, evo_ano, -cap_poup_ano, -patrim_atual).round(2)
        patrimonio = npf.fv(tx_juro_ano, evo_ano, -cap_poup_ano, -patrim_atual).round(2)
        vitalicio = npf.fv(tx_juro_ano, evo_ano, -parcela_vitalicio * 12, -patrim_atual).round(2)
        consumo = npf.fv(tx_juro_ano, evo_ano, -parcela_consumo * 12, -patrim_atual).round(2)
        df['Idade'].loc[i] = idade + i
        df['Valor Investido'] = valor_investido_ano
        df['Patrimônio Acumulado'] = patrimonio
        df['Vitalício'] = vitalicio
        df['Consumo Patrimônio'] = consumo
    df = df.set_index('Idade')
    return df

@st.cache_data
def calcula_independencia(idade, idade_indep, patrim_atual, cap_poup_ano, renda_mensal_indep, tx_juro_ano):
    anos_invest = idade_indep - idade
    anos_consumo = 100 - idade_indep
    meses_invest = anos_invest * 12
    juro_mensal = (1+tx_juro_ano)**(1/12)-1
    renda_indep_anual = renda_mensal_indep * 12
    evo_ano_indep = list(range(idade_indep, 101))
    tempo_uso = list(range(0, anos_consumo + 1))
    tempo_consumo = list(range(anos_consumo, -1, -1))
    pat_vitalicio = round(renda_mensal_indep / juro_mensal, 2)
    valor_inv = npf.fv(0, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -patrim_atual, -pat_vitalicio).round(2)
    patrim_vitalicio = npf.fv(tx_juro_ano, anos_invest, -parcela_vitalicio * 12, -patrim_atual).round(2)
    patrim_acumulado = npf.fv(tx_juro_ano, anos_invest, -cap_poup_ano, -patrim_atual).round(2)
    df = pd.DataFrame({'Idade': evo_ano_indep,
                                    'Valor Investido': valor_inv,
                                    'Patrimônio Acumulado': 0,
                                    'Vitalício': patrim_vitalicio, 
                                    'Consumo Patrimônio': 0,
                                    'Tempo de usufruto': tempo_uso},
                                    index=tempo_consumo)

    for i in tempo_consumo:
        pat_consumo = npf.pv(tx_juro_ano, i, -renda_indep_anual).round(2)
        df['Consumo Patrimônio'].loc[i] = pat_consumo

    df = df.set_index('Tempo de usufruto')

    for i in tempo_uso:
        patrim_acum = npf.fv(tx_juro_ano, i, 0, -patrim_acumulado).round(2)
        df['Patrimônio Acumulado'].loc[i] = patrim_acum

    df = df.set_index('Idade')
    return df

def calcula_gerenc_risco(patrimonio, saque_anual=0.0, tx_juros=0.04):
    try:
        anos = round(float(npf.nper(tx_juros, -saque_anual, patrimonio, 0)))
    except OverflowError:
        anos = 1

    anos_lista = list(range(1, anos + 1))
    patrimonio_lista = []
    saque_lista = []
    
    for ano in anos_lista:
        patrimonio *= (1 + tx_juros)
        patrimonio -= saque_anual
        patrimonio_lista.append(round(patrimonio, 2))
        saque_lista.append(round(saque_anual, 2))
    
    df = pd.DataFrame({
        'Ano': anos_lista,
        'Patrimônio': patrimonio_lista,
        })
    df = df.set_index('Ano')
    return df, anos


@st.cache_data(experimental_allow_widgets=True)
def categoria_invest(categoria, key): 
    match categoria:
        case 'Ações':
            carteira_acoes = st.multiselect('Selecione o(s) papel(is)', utils.lista_ativos_b3(), placeholder='Digite o ticker', key=f'acoes{key}')
        case 'FIIs':
            carteira_fiis = st.multiselect('Selecione o(s) papel(is)', utils.lista_fiis_b3(), placeholder='Digite o ticker', key=f'fii{key}')
        case 'Renda Fixa':
            carteira_renda_fixa = st.text_input('Digite o(s) ativo(s)', key=f'rf{key}')
        case 'Tesouro Direto':
            carteira_tesouro = st.text_input('Digite o(s) ativo(s)', key=f'td{key}')
        case 'Fundos de Ações':
            carteira_fundos_acoes = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_acoes{key}')
        case 'Fundos de Renda Fixa':
            carteira_fundos_rf = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_rf{key}')
        case 'Fundos Multimercados':
            carteira_fundos_mult = st.text_input('Digite o(s) nome(s) do(s) fundo(s)', key=f'fnd_mult{key}')
        case 'Moeda':
            carteira_moeda = st.text_input('Digite a(s) moeda(s)', key=f'moeda{key}')
        case 'Cripto':
            carteira_cripto = st.text_input('Digite o(s) ativo(s)', key=f'cripto{key}')
        case 'ETFs':
            carteira_etf = st.text_input('Digite o(s) ativo(s)', key=f'etf{key}')
        case 'Stocks':
            carteira_stocks = st.text_input('Digite o(s) ativo(s)', key=f'stocks{key}')
        case 'REITs':
            carteira_reits = st.text_input('Digite o(s) ativo(s)', key=f'reits{key}')
        case 'Bonds':
            carteira_bonds = st.text_input('Digite o(s) ativo(s)', key=f'bonds{key}')
        case 'Treasures':
            carteira_treasures = st.text_input('Digite o(s) ativo(s)', key=f'treasures{key}')
        case 'Funds':
            carteira_funds = st.text_input('Digite o(s) ativo(s)', key=f'funds{key}')
        case 'Mutual Funds':
            carteira_mutual_funds = st.text_input('Digite o(s) ativo(s)', key=f'mutual_funds{key}')
    return

class PDFWithFooter(FPDF):
    def header(self):
        self.image('img/QUANTIQ.png', x=65, y=5, w=80)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I',size=9)
        self.cell(0, 4, 'robson.perdigao@quantiq.trade     |     11 98047-3370     |     www.quantiq.trade', align='C')

def gerar_pdf(grafico_receita, grafico_receita_despesa, grafico_patrimonio, grafico_geren_risco, grafico_consol):
    
    pdf = PDFWithFooter()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_draw_color(153, 102, 255)
    mes = date.today().strftime('%B')
    ano = date.today().strftime('%Y')
    meses = {
        'January': 'Janeiro',
        'February': 'Fevereiro',
        'March': 'Março',
        'April': 'Abril',
        'May': 'Maio',
        'June': 'Junho',
        'July': 'Julho',
        'August': 'Agosto',
        'September': 'Setembro',
        'October': 'Outubro',
        'November': 'Novembro',
        'December': 'Dezembro'} 
    mes_em_portugues = meses.get(mes, mes)
  
    # Capa
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', size=18)
    pdf.set_title('Diagnóstico do Cliente')
    pdf.multi_cell(0, 100, ' ', align='C')
    pdf.multi_cell(0, 9, f"Diagnóstico do Cliente\n{nome_cliente}", align='C')
    pdf.multi_cell(0, 18, ' ', align='C')
    pdf.set_font('Helvetica', size=14)
    #pdf.multi_cell(0, 9, f"Assessor de Investimentos\nRobson Perdigão Assessor", align='C')
    pdf.multi_cell(0, 120, ' ', align='C')
    pdf.multi_cell(0, 9, f'{mes_em_portugues}/{ano}', align='C')
    
    # Página 1
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', size=18)
    pdf.ln(30)
    pdf.cell(0, 9, 'Planejamento Financeiro')
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', size=12)
    pdf.multi_cell(0, 9, f"{nome_cliente},", align='L')
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 9, f"Esse estudo foi desenvolvido exclusivamente para você.\n\nFoi considerado sua capacidade de poupança para atingir seus objetivos de curto, médio e longo prazo, adequando esses períodos ao atual cenário econômico. Lembre-se que é importante levar em conta sua necessidade cotidiana, orçamento pessoal, passando por rentabilidade e riscos de seus investimentos.", align='L')
    pdf.multi_cell(0, 9, f"\nO principal objetivo deste planejamento é que você encontre os melhores investimentos direcionados ao seu perfil e consiga fazer com que seu dinheiro renda para garantir a realização de seus planos de vida. Para isso, precisaremos de um acompanhamento e troca de informações constantes.", align='L')
    pdf.multi_cell(0, 9, f"\nA seguir você encontrará todas as informações coletadas e organizadas para seguir um bom planejamento financeiro, bem como os próximos passos que você deverá seguir.", align='L')
    
    
    # Página 2
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', size=18)
    #pdf.multi_cell(0, 20, ' ', align='C')
    pdf.ln(30)
    #pdf.multi_cell(0, 9, '\nAnálise do Perfil\n\n', align='L')
    pdf.cell(0, 9, 'Análise do Perfil')
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', size=12)
    pdf.multi_cell(0, 9, 'Aspectos Comportamentais e Pessoais:')
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 9, f'{perfil_comportamental}', align='L')
    pdf.set_font('Helvetica', 'B', size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 9, 'Aspectos Técnicos e Específicos:')
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 9, f'{perfil_tecnico}', align='L')
    
    if grafico_receita is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            grafico_receita.savefig(tmp_file, format='png', dpi=300, transparent=True)
            image_buffer_receita = tmp_file.name
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', size=18)
        pdf.ln(30)
        pdf.cell(0, 9, 'Contexto Atual Financeiro')
        pdf.ln(20)
        pdf.set_font('Helvetica', size=12)
        if outras_receitas > 0 and receita_conjuge == 0:
            pdf.multi_cell(0, 9, f"Sua receita atual é de R$ {receita_mensal:.2f}.\nAlém disso, possui outras receitas que compõem um valor de R$ {outras_receitas:.2f}.\nTotalizando R$ {receita_total:.2f} mensais.", align='L')
            pdf.image(image_buffer_receita, w=80, x=55, y=80)
        if outras_receitas > 0 and receita_conjuge > 0:
            pdf.multi_cell(0, 9, f"Sua receita atual é de R$ {receita_mensal:.2f}.\nA receita do cônjuge é de R$ {receita_conjuge:.2f}.\nAlém disso, possui outras receitas que compõem um valor de R$ {outras_receitas:.2f}.\nTotalizando R$ {receita_total:.2f} mensais.", align='L')
            pdf.image(image_buffer_receita, w=80, x=55, y=80)
        if outras_receitas == 0 and receita_conjuge > 0:
            pdf.multi_cell(0, 9, f"Sua receita atual é de R$ {receita_mensal:.2f}.\nA receita do cônjuge é de R$ {receita_conjuge:.2f}.\nTotalizando R$ {receita_total:.2f} mensais.", align='L')
            pdf.image(image_buffer_receita, w=80, x=55, y=80)
        if outras_receitas == 0 and receita_conjuge == 0:
            pdf.multi_cell(0, 9, f"Sua receita atual é de R$ {receita_mensal:.2f}.", align='L')
            pdf.image(image_buffer_receita, w=80, x=55, y=65)
        pdf.ln(70)
        
    if grafico_receita_despesa is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            grafico_receita_despesa.savefig(tmp_file, format='png', dpi=300, transparent=True)
            image_buffer_rec_desp = tmp_file.name
        pdf.multi_cell(0, 9, f'Em relação ao seu orçamento doméstico, suas despesas mensais somam R$ {despesa_mensal:.2f}, logo, sua capacidade de poupança é de R$ {cap_poupanca:.2f} mensais.')
        pdf.image(image_buffer_rec_desp, w=90, x=55, y=170)
        
    if grafico_patrimonio is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            grafico_patrimonio.savefig(tmp_file, format='png', dpi=300, transparent=True)
            image_buffer_patrim = tmp_file.name
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', size=18)
        pdf.ln(30)
        pdf.cell(0, 9, 'Independência Financeira')
        pdf.ln(20)
        pdf.set_font('Helvetica', size=12)
        pdf.multi_cell(0, 9, f"Considerando sua capacidade de poupança atual de R$ {cap_poupanca:.2f} e uma taxa de juros real de {(juro_real*100):.2f}% ao ano, você irá obter um patrimônio de R$ {patrim_acumulado:.2f} aos {idade_indep} anos de idade.\nPara atingir o objetivo de independência financeira com renda mensal vitalícia de R$ {renda_indep:.2f} é necessário um patrimônio de R$ {pat_vitalicio:.2f}.\nE o valor de patrimônio para consumir até os 100 anos de idade é de R$ {pat_consumo:.2f}.", align='L')  
        pdf.image(image_buffer_patrim, w=180, y=100)
        pdf.ln(85)
        if parcela_vitalicio > cap_poupanca:
            pdf.multi_cell(0, 9, f'Para obter o patrimônio que gera renda vitalícia, é necessário um incremento na sua capacidade de poupança atual de R$ {parcela_vitalicio - cap_poupanca:.2f}.')
        if parcela_consumo > cap_poupanca:
            pdf.multi_cell(0, 9, f'Para obter o patrimônio de consumo até os 100 anos, é necessário um incremendo na sua capacidade de poupança atual de R$ {parcela_consumo - cap_poupanca:.2f}.')
    
    if filhos == 'Sim':
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', size=18)
        pdf.ln(30)
        pdf.cell(0, 9, 'Custos com Dependentes')
        pdf.ln(20)
        pdf.set_font('Helvetica', size=12)
        pdf.multi_cell(0, 9, f"Devido aos custos com {nome_filho1}, os recursos necessários serão de R$ {vlr_nec_educ1:.2f} até os {prz_term_estudos1:.0f} anos.", align='L')  
        
    if grafico_geren_risco is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            grafico_geren_risco.savefig(tmp_file, format='png', dpi=300, transparent=True)
            image_buffer_ger_risco = tmp_file.name
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', size=18)
        pdf.ln(30)
        pdf.cell(0, 9, 'Gerenciamento de Risco e Inventário')
        pdf.ln(20)
        pdf.set_font('Helvetica', size=12)
        pdf.multi_cell(0, 9, f"Em caso de ausência, a família irá consumir o patrimônio financeiro em {tempo_despesa} anos, conforme gráfico:", align='L')
        pdf.image(image_buffer_ger_risco, w=120, x=50, y=65)
        pdf.ln(85)
        pdf.multi_cell(0, 9, f'Previdência Privada: R$ {prev_atual:.2f}\nSeguro Invalidez: R$ {seg_atual:.2f}\nFGTS: R$ {fgts:.2f}\nProteções Totais: R$ {protect:.2f}', align='L')
        pdf.multi_cell(0, 9, f'Patrimônio Financeiro: R$ {invest_atual:.2f}\nPatrimônio Imobilizado: R$ {bens_atual:.2f}')
        pdf.multi_cell(0, 9, f"O valor Necessário para cobertura das despesas é de R$ {vlr_nec_cap_hoje:.2f}\nO valor total das despesas + inventário é de R$ {custo_total_despesa:.2f}", align='L')
        pdf.multi_cell(0, 9, f"Custo do Inventário de Ativos Financeiros: R$ {custo_inv_fin:.2f}\nCusto do Inventário de Bens R$ {custo_inv_bens:.2f}\nCusto Total do Inventário: R$ {custo_inventario:.2f}", align='L') 

        
    if grafico_consol is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            grafico_consol.savefig(tmp_file, format='png', dpi=300, transparent=True)
            image_buffer_consol = tmp_file.name
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', size=18)
        pdf.ln(30)
        pdf.cell(0, 9, 'Consolidação')
        pdf.ln(20)
        pdf.set_font('Helvetica', size=12)
        if custo_sucessorio > invest_atual_protec:
            pdf.multi_cell(0, 9, f"Em caso de ausência, os custos totais de sucessão serão de aproximadamente R$ {custo_sucessorio:.2f}. Como sua proteção atual é de R$ {protect:.2f}, o valor não é suficiente para arcar com os custos de sucessão.", align='L')  
        else:
            pdf.multi_cell(0, 9, f"Em caso de ausência, os custos totais de sucessão serão de aproximadamente R$ {custo_sucessorio:.2f}. Como sua proteção atual é de R$ {protect:.2f}, o valor é suficiente para arcar com os custos de sucessão.", align='L')  
        pdf.image(image_buffer_consol, w=120, x=50, y=75)
        pdf.ln(85)
        pdf.multi_cell(0, 9, demais_info, align='L')
    
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', size=18)
    pdf.ln(30)
    pdf.cell(0, 9, 'Conclusão')
    pdf.ln(20)
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 9, conclusao, align='L')
    pdf.set_font('Helvetica', 'B', size=18)
    pdf.ln(20)
    pdf.cell(0, 9, 'Próximos Passos')
    pdf.ln(20)
    pdf.set_font('Helvetica', size=12)
    pdf.multi_cell(0, 9, proximos_passos, align='L')
        
        
    # Exporta o PDF
    gen_pdf = pdf.output(dest='S').encode('latin1')
    
    return gen_pdf


st.markdown('### Núcelo Familiar')
col1, col2, col3, col4 = st.columns(4)
with col1:
    nome_cliente = st.text_input('Nome')

with col2:
    profissao_cliente = st.text_input('Profissão')
    
with col3:
    nascimento_cliente = st.date_input('Data de Nascimento', format='DD/MM/YYYY')
    idade_cliente = utils.calcula_idade(nascimento_cliente)  
    st.write(str(idade_cliente), 'anos')
    
with col4:
    lista_estado_civil = ['Solteiro(a)', 'Casado(a) / União Estável', 'Viúvo(a)', 'Divorciado(a)']
    estado_civil = st.selectbox('Estado Civil', lista_estado_civil)
    
st.markdown('---')
if estado_civil == 'Casado(a) / União Estável':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nome_conjuge = st.text_input('Nome Cônjuge')

    with col2:
        profissao_conjuge = st.text_input('Profissão Cônjuge')
        
    with col3:
        nascimento_conjuge = st.date_input('Data de Nascimento Cônjuge', format='DD/MM/YYYY')
        idade_conjuge = utils.calcula_idade(nascimento_conjuge)
        st.write(str(idade_conjuge), 'anos')
        
    with col4:
        lista_regime = ['Comunhão Parcial de Bens', 'Comunhão Total de Bens', 'Separação Total de Bens']
        regime_casamento = st.selectbox('Regime de Casamento', lista_regime)
    st.markdown('---')
    
filhos = st.radio('Possui Filhos?', ['Não', 'Sim'], horizontal=True, )
if filhos == 'Sim':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        nome_filho1 = st.text_input('Nome Filho(a)', key='nome_filho1')
        nascimento_filho1 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho1')
        idade_filho1 = utils.calcula_idade(nascimento_filho1)
        st.write(str(idade_filho1), 'anos')
        
    with col2:
        nome_filho2 = st.text_input('Nome Filho(a)', key='nome_filho2')
        nascimento_filho2 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascimento_filho2')
        idade_filho2 = utils.calcula_idade(nascimento_filho2)
        st.write(str(idade_filho2), 'anos')
        
    with col3:
        nome_filho3 = st.text_input('Nome Filho(a)', key='nome_filho3')
        nascimento_filho3 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho3')
        idade_filho3 = utils.calcula_idade(nascimento_filho3)
        st.write(str(idade_filho3), 'anos')

    with col4:
        nome_filho4 = st.text_input('Nome Filho(a)', key='nome_filho4')
        nascimento_filho4 = st.date_input('Data de Nascimento Filho(a)', format='DD/MM/YYYY', key='nascim_filho4')
        idade_filho4 = utils.calcula_idade(nascimento_filho4)
        st.write(str(idade_filho4), 'anos')
st.markdown('---')


st.markdown('### Orçamento Doméstico')
st.markdown('##### Receitas')
col1, col2, col3, col4 = st.columns(4)
with col1:
    receita_mensal = st.number_input('Receita Mensal')
    receita_conjuge = 0
    receita_familia = 0
with col2:
    outras_receitas = st.number_input('Outras Receitas')
    
with col3:
    if estado_civil == 'Casado(a) / União Estável':
        receita_conjuge = st.number_input('Receita Cônjuge')

with col4:
    if estado_civil == 'Casado(a) / União Estável':
        receita_total = receita_mensal + outras_receitas + receita_conjuge
        st.metric('Receita total familiar', f'R$ {receita_total:.2f}') 
    else:
        receita_total = receita_mensal + outras_receitas
        st.metric('Receita total familiar', f'R$ {receita_total:.2f}') 
    
st.markdown('##### Despesas')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    despesa_mensal = st.number_input('Despesa Mensal')
    
st.markdown('##### Capacidade de Poupança')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    cap_poupanca = receita_total - despesa_mensal
    cap_poupanca_anual = cap_poupanca * 12
    st.metric('Sua capacidade de poupança mensal é', f'R$ {cap_poupanca:.2f}')
with col2:
    st.metric('Sua capacidade de poupança anual é', f'R$ {cap_poupanca_anual:.2f}')
st.markdown('---')


st.markdown('### Investimentos')
md_invest = st.toggle('Adicionar investimentos atuais')
invest_atual = 0
custo_inventario = 0
custo_sucessorio = 0
if md_invest:
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        categorias = ['Ações', 'FIIs', 'Renda Fixa', 'Tesouro Direto', 'Fundos de Ações',
                    'Fundos de Renda Fixa', 'Fundos Multimercados', 'Moeda', 'ETFs', 'Cripto']
        cat1 = st.selectbox('Categoria', categorias, key='cat1')
        cat2 = st.selectbox('Categoria', categorias, key='cat2', index=1)
        cat3 = st.selectbox('Categoria', categorias, key='cat3', index=2)
        cat4 = st.selectbox('Categoria', categorias, key='cat4', index=3)
        cat5 = st.selectbox('Categoria', categorias, key='cat5', index=4)
        cat6 = st.selectbox('Categoria', categorias, key='cat6', index=7)
        cat7 = st.selectbox('Categoria', categorias, key='cat7', index=8)
        
    with col2:
        categoria_invest(cat1, 1)
        categoria_invest(cat2, 2)
        categoria_invest(cat3, 3)
        categoria_invest(cat4, 4)
        categoria_invest(cat5, 5)
        categoria_invest(cat6, 6)
        categoria_invest(cat7, 7)
            
    with col3:
        valor_ativos1 = st.number_input('Valor total dos ativos', key='val1')
        valor_ativos2 = st.number_input('Valor total dos ativos', key='val2')
        valor_ativos3 = st.number_input('Valor total dos ativos', key='val3')
        valor_ativos4 = st.number_input('Valor total dos ativos', key='val4')
        valor_ativos5 = st.number_input('Valor total dos ativos', key='val5')
        valor_ativos6 = st.number_input('Valor total dos ativos', key='val6')
        valor_ativos7 = st.number_input('Valor total dos ativos', key='val7')
        invest_atual = valor_ativos1 + valor_ativos2 + valor_ativos3 + valor_ativos4 + valor_ativos5 + valor_ativos6 + valor_ativos7
        st.metric('Patrimônio Atual', f'R$ {invest_atual:.2f}')
st.markdown('---')

st.markdown('### Investimentos Internacionais')
md_offshore = st.toggle('Adicionar investimentos internacionais')
invest_atual_offshore = 0
if md_offshore:
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        categorias_internacional = ['Stocks', 'REITs', 'Bonds', 'Treasures', 'Funds', 'Mutual Funds', 'ETFs']
        offshore1 = st.selectbox('Categoria', categorias_internacional, key='offshore1')
        offshore2 = st.selectbox('Categoria', categorias_internacional, key='offshore2', index=1)
        offshore3 = st.selectbox('Categoria', categorias_internacional, key='offshore3', index=2)
        offshore4 = st.selectbox('Categoria', categorias_internacional, key='offshore4', index=3)
        offshore5 = st.selectbox('Categoria', categorias_internacional, key='offshore5', index=4)
        offshore6 = st.selectbox('Categoria', categorias_internacional, key='offshore6', index=5)
        
    with col2:
        categoria_invest(offshore1, 1)
        categoria_invest(offshore2, 2)
        categoria_invest(offshore3, 3)
        categoria_invest(offshore4, 4)
        categoria_invest(offshore5, 5)
        categoria_invest(offshore6, 6)
            
    with col3:
        valor_ativos_offshore1 = st.number_input('Valor total dos ativos', key='valoff1')
        valor_ativos_offshore2 = st.number_input('Valor total dos ativos', key='valoff2')
        valor_ativos_offshore3 = st.number_input('Valor total dos ativos', key='valoff3')
        valor_ativos_offshore4 = st.number_input('Valor total dos ativos', key='valoff4')
        valor_ativos_offshore5 = st.number_input('Valor total dos ativos', key='valoff5')
        valor_ativos_offshore6 = st.number_input('Valor total dos ativos', key='valoff6')
        invest_atual_offshore = valor_ativos_offshore1 + valor_ativos_offshore2 + valor_ativos_offshore3 + valor_ativos_offshore4 + valor_ativos_offshore5 + valor_ativos_offshore6
        st.metric('Patrimônio Internacional Atual', f'R$ {invest_atual_offshore:.2f}')      
st.markdown('---')   


st.markdown('### Seguros e Previdência')
md_protect = st.toggle('Adicionar seguros e previdências')
protect = 0
prev_atual = 0
seg_atual = 0
seg_atual_conj = 0
fgts = 0
seguro_vida = 0
if md_protect:
    col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 1])
    with col1:
        op_prev = st.selectbox('Possui Previdência Privada?', ['Sim', 'Não'], index=1)
    if op_prev == 'Sim':
        with col2:
            nome_prev = st.text_input('Nome da Previdência')
        with col3:
            inst_prev = st.text_input('Instituição')
        with col4:
            tipo_prev = st.selectbox('Tipo de Previdência', ['PGBL', 'VGBL'])
        with col5:    
            reg_trib_prev = st.selectbox('Regime Tributário', ['Progressivo', 'Regressivo'])
        with col6:    
            prev_atual = st.number_input('Valor da Previdência')
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            op_seg = st.selectbox('Possui Seguro de Vida?', ['Sim', 'Não'], index=1) 
            if op_seg == 'Sim':
                with col2:
                    seguradora = st.text_input('Seguradora')
                with col3:
                    seg_atual = st.number_input('Valor do Prêmio')
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        if estado_civil == 'Casado(a) / União Estável':
            with col1:
                op_seg_conj = st.selectbox('Cônjuge Possui Seguro de Vida?', ['Sim', 'Não'], index=1) 
                if op_seg_conj == 'Sim':
                    with col2:
                        seguradora_conj = st.text_input('Seguradora', key='seg_conj')
                    with col3:
                        seg_atual_conj = st.number_input('Valor do Prêmio', key='vlr_seg_coj')
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            op_fgts = st.selectbox('Possui FGTS?', ['Sim', 'Não'], index=1) 
            if op_fgts == 'Sim':                
                with col3:
                    fgts = st.number_input('Valor do FGTS') 
    seguro_vida = seg_atual + seg_atual_conj
    protect = prev_atual + seg_atual + seg_atual_conj + fgts
    st.metric('Proteções Totais', f'R$ {(protect):.2f}')   
st.markdown('---')   


st.markdown('### Bens Mobiliários e Imobiliários')
md_bens = st.toggle('Adicionar bens móveis e imóveis')
bens_atual = 0
if md_bens:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1]) 
    with col1:
        categorias_bens = ['Imóvel', 'Automóvel', 'Aeronave/Embarcação', 'Precatório', 'Outro']
        catbens1 = st.selectbox('Categoria', categorias_bens, key='catbens1')
        catbens2 = st.selectbox('Categoria', categorias_bens, key='catbens2', index=1)
        catbens3 = st.selectbox('Categoria', categorias_bens, key='catbens3', index=2)
        catbens4 = st.selectbox('Categoria', categorias_bens, key='catbens4', index=3)
        catbens5 = st.selectbox('Categoria', categorias_bens, key='catbens5', index=4)
        catbens6 = st.selectbox('Categoria', categorias_bens, key='catbens6', index=4)
        catbens7 = st.selectbox('Categoria', categorias_bens, key='catbens7', index=4)
        
    with col2:
        bem1 = st.text_input('Descrição', key='bem1')
        bem2 = st.text_input('Descrição', key='bem2')
        bem3 = st.text_input('Descrição', key='bem3')
        bem4 = st.text_input('Descrição', key='bem4')
        bem5 = st.text_input('Descrição', key='bem5')
        bem6 = st.text_input('Descrição', key='bem6')
        bem7 = st.text_input('Descrição', key='bem7')
            
    with col3:
        valor_bens1 = st.number_input('Valor do bem', key='valbens1')
        valor_bens2 = st.number_input('Valor do bem', key='valbens2')
        valor_bens3 = st.number_input('Valor do bem', key='valbens3')
        valor_bens4 = st.number_input('Valor do bem', key='valbens4')
        valor_bens5 = st.number_input('Valor do bem', key='valbens5')
        valor_bens6 = st.number_input('Valor do bem', key='valbens6')
        valor_bens7 = st.number_input('Valor do bem', key='valbens7')
        bens_atual = valor_bens1 + valor_bens2 + valor_bens3 + valor_bens4 + valor_bens5 + valor_bens6 + valor_bens7
        st.metric('Patrimônio em Bens Atual', f'R$ {bens_atual:.2f}') 
        
    with col4:
        op_venda = ['Selecione', 'Sim', 'Não', 'N/A']
        vendavel1 = st.selectbox('Vendável', op_venda, key='vendavel1')
        vendavel2 = st.selectbox('Vendável', op_venda, key='vendavel2')
        vendavel3 = st.selectbox('Vendável', op_venda, key='vendavel3')
        vendavel4 = st.selectbox('Vendável', op_venda, key='vendavel4')
        vendavel5 = st.selectbox('Vendável', op_venda, key='vendavel5')
        vendavel6 = st.selectbox('Vendável', op_venda, key='vendavel6')
        vendavel7 = st.selectbox('Vendável', op_venda, key='vendavel7')
    
    with col5:
        renda_bens1 = st.number_input('Renda do bem', key='rendabens1')
        renda_bens2 = st.number_input('Renda do bem', key='rendabens2')
        renda_bens3 = st.number_input('Renda do bem', key='rendabens3')
        renda_bens4 = st.number_input('Renda do bems', key='rendabens4')
        renda_bens5 = st.number_input('Renda do bem', key='rendabens5')
        renda_bens6 = st.number_input('Renda do bem', key='rendabens6')
        renda_bens7 = st.number_input('Renda do bem', key='rendabens7')
st.markdown('---')

patrimonio_total = invest_atual + bens_atual + invest_atual_offshore

st.markdown('### Independência Financeira')
col1, col2, col3, col4 = st.columns(4)  
with col1:
    idade_indep = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=50, step=1)
   
with col2:
    renda_indep = st.number_input('Renda Mensal Desejada')
    renda_indep_anual = renda_indep * 12
    
with col3:
    juro_real = st.number_input('Taxa de Juros Real', value=4.0, step=0.5) / 100
    juro_mensal = (1+juro_real)**(1/12)-1

anos_invest = idade_indep - idade_cliente
meses_invest = anos_invest * 12
anos_consumo = 100 - idade_indep
meses_consumo = anos_consumo * 12
patrim_acumulado = npf.fv(juro_real, anos_invest, -cap_poupanca_anual, -invest_atual).round(2)
pat_consumo = npf.pv(juro_mensal, meses_consumo, -renda_indep, 0).round(2)
parcela_consumo = npf.pmt(juro_mensal, meses_invest, -invest_atual, -pat_consumo).round(2)
patrim_consumo = npf.fv(juro_real, anos_invest, -parcela_consumo * 12, -invest_atual)
pat_vitalicio = round(renda_indep / juro_mensal, 2)
parcela_vitalicio = npf.pmt(juro_mensal, meses_invest, -invest_atual, -pat_vitalicio).round(2)
patrim_vitalicio = npf.fv(juro_real, anos_invest, -parcela_vitalicio * 12, -invest_atual).round(2)
valor_inv = npf.fv(0, anos_invest, -cap_poupanca_anual, -invest_atual).round(2)

df_patrimonio = calcula_patrimonio(idade_cliente, idade_indep, invest_atual, cap_poupanca_anual, renda_indep, juro_real)
df_independencia = calcula_independencia(idade_cliente, idade_indep, invest_atual, cap_poupanca_anual, renda_indep, juro_real)
df_evolucao = pd.concat([df_patrimonio, df_independencia]).drop_duplicates('Patrimônio Acumulado')

fig_patr, ax_patr = plt.subplots(figsize=(12, 6))
ax_patr.plot(df_evolucao.index, df_evolucao['Valor Investido'], label='Valor Investido')
ax_patr.plot(df_evolucao.index, df_evolucao['Patrimônio Acumulado'], label='Patrimônio Acumulado')
ax_patr.plot(df_evolucao.index, df_evolucao['Vitalício'], label='Vitalício')
ax_patr.plot(df_evolucao.index, df_evolucao['Consumo Patrimônio'], label='Consumo Patrimônio')

ax_patr.set_xlabel('Idade')
ax_patr.set_ylabel('Valor')
ax_patr.set_title('Evolução Patrimonial')
ax_patr.legend()

def millions_formatter(x, pos):
    return f'{x / 1e6:.1f}M'
ax_patr.yaxis.set_major_formatter(FuncFormatter(millions_formatter))



tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução Patrimonial", "Acumulação de Patrimônio", "Independência Financeira", "🗃 Dados"])
with tab1:
    st.subheader('Evolução Patrimonial')
    st.line_chart(df_evolucao)
    
with tab2:
    st.subheader('Acumulação de Patrimônio')
    st.line_chart(df_patrimonio)
    
with tab3:
    st.subheader('Independência Financeira')
    st.line_chart(df_independencia)
    
with tab4:
    st.subheader('Dados Detalhados')
    st.dataframe(df_evolucao)

col1, col2, col3 = st.columns(3)  
with col1:
    st.metric('Projeção de Patrimônio', f'R$ {patrim_acumulado:.2f}')
    st.write('')
    st.metric('Aportes Mensais', f'R$ {cap_poupanca:.2f}')
    
with col2:
    st.metric('Patrimônio para consumo até os 100 anos', f'R$ {patrim_consumo:.2f}', f'{(patrim_acumulado/patrim_consumo-1)*100:.2f}%')
    st.metric('Aportes Mensais', f'R$ {parcela_consumo:.2f}')
    
with col3:
    st.metric('Patrimônio para renda vitalícia', f'R$ {patrim_vitalicio:.2f}', f'{(patrim_acumulado/patrim_vitalicio-1)*100:.2f}%')
    st.metric('Aportes Mensais', f'R$ {parcela_vitalicio:.2f}')

st.markdown('---')

cenario2 = st.toggle('Simular outro cenário')
if cenario2:
    st.markdown('### Cenário 2')
    
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        idade_indep_2 = st.slider('Idade da Independência Financeira', min_value=18, max_value=100, value=60, step=1)

    with col2:
        renda_indep_2 = st.number_input('Renda Mensal Desejada', key='RendaIndep2')
        renda_indep_anual_2 = renda_indep_2 * 12
        
    with col3:
        juro_real_2 = st.number_input('Taxa de Juros Real', value=5.0, step=0.5) / 100
        juro_mensal_2 = (1+juro_real_2)**(1/12)-1
        
    with col4:
        cap_poupanca_anual_2 = st.number_input('Capacidade de Poupança Anual')
     
    anos_invest_2 = idade_indep_2 - idade_cliente
    meses_invest_2 = anos_invest_2 * 12
    anos_consumo_2 = 100 - idade_indep_2
    meses_consumo_2 = anos_consumo_2 * 12
    patrim_acumulado_2 = npf.fv(juro_real_2, anos_invest_2, -cap_poupanca_anual_2, -invest_atual).round(2)
    pat_consumo_2 = npf.pv(juro_mensal_2, meses_consumo_2, -renda_indep_2, 0).round(2)
    parcela_consumo_2 = npf.pmt(juro_mensal_2, meses_invest_2, -invest_atual, -pat_consumo_2).round(2)
    patrim_consumo_2 = npf.fv(juro_real_2, anos_invest_2, -parcela_consumo_2 * 12, -invest_atual)
    pat_vitalicio_2 = round(renda_indep_2 / juro_mensal_2, 2)
    parcela_vitalicio_2 = npf.pmt(juro_mensal_2, meses_invest_2, -invest_atual, -pat_vitalicio_2).round(2)
    patrim_vitalicio_2 = npf.fv(juro_real_2, anos_invest_2, -parcela_vitalicio_2 * 12, -invest_atual).round(2)
    valor_inv_2 = npf.fv(0, anos_invest_2, -cap_poupanca_anual_2, -invest_atual).round(2)

    df_patrimonio_2 = calcula_patrimonio(idade_cliente, idade_indep_2, invest_atual, cap_poupanca_anual_2, renda_indep_2, juro_real_2)
    df_independencia_2 = calcula_independencia(idade_cliente, idade_indep_2, invest_atual, cap_poupanca_anual_2, renda_indep_2, juro_real_2)
    df_evolucao_2 = pd.concat([df_patrimonio_2, df_independencia_2]).drop_duplicates('Patrimônio Acumulado')

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução Patrimonial", "Acumulação de Patrimônio", "Independência Financeira", "🗃 Dados"])
    with tab1:
        st.subheader('Evolução Patrimonial')
        st.line_chart(df_evolucao_2)
        
    with tab2:
        st.subheader('Acumulação de Patrimônio')
        st.line_chart(df_patrimonio_2)
        
    with tab3:
        st.subheader('Independência Financeira')
        st.line_chart(df_independencia_2)
        
    with tab4:
        st.subheader('Dados Detalhados')
        st.dataframe(df_evolucao_2)  
   
    with col1:
        st.metric('Projeção de Patrimônio', f'R$ {patrim_acumulado_2:.2f}')
        st.write('')
        st.metric('Aportes Mensais', f'R$ {cap_poupanca_anual_2 / 12:.2f}')
        
    with col2:
        st.metric('Patrimônio para consumo até os 100 anos', f'R$ {patrim_consumo_2:.2f}', f'{(patrim_acumulado_2/patrim_consumo_2-1)*100:.2f}%')
        st.metric('Aportes Mensais', f'R$ {parcela_consumo_2:.2f}')
        
    with col3:
        st.metric('Patrimônio para renda vitalícia', f'R$ {patrim_vitalicio_2:.2f}', f'{(patrim_acumulado_2/patrim_vitalicio_2-1)*100:.2f}%')
        st.metric('Aportes Mensais', f'R$ {parcela_vitalicio_2:.2f}')
st.markdown('---')


if receita_mensal > 0 and despesa_mensal > 0:
    st.write('### Receitas')
    col1, col2, col3, col4 = st.columns(4)
    valores_receita = [receita_mensal]
    rotulos_receita = ['Receita']
    if outras_receitas > 0:
        valores_receita = [receita_mensal, outras_receitas]
        rotulos_receita = ['Receita', 'Outras Receitas']
    if estado_civil == 'Casado(a) / União Estável':
        valores_receita = [receita_mensal, receita_conjuge, outras_receitas]
        rotulos_receita = ['Receita', 'Receita do Cônjuge', 'Outras Receitas']
      
    with col1:
        st.write('Distribuição das Receitas')
        fig_receita, ax_rec = plt.subplots(figsize=(3,3))
        ax_rec.pie(valores_receita, labels=rotulos_receita, autopct='%1.1f%%', 
            startangle=90, radius=1, center=(1, 1))
        ax_rec.axis('equal')
        st.pyplot(fig_receita)
        
    with col3:
        st.write('Receitas x Despesas')
        x = [receita_total, despesa_mensal, cap_poupanca]
        rotulos_rec_desp = ['Receita Total', 'Despesa Mensal', 'Capacidade de Poupança']
        fig_rec_desp, ax_rec_desp = plt.subplots(figsize=(3,3))
        ax_rec_desp.pie(x, labels=rotulos_rec_desp, autopct='%1.1f%%', 
            startangle=90, radius=1, center=(1, 1))
        
        st.pyplot(fig_rec_desp)
        
          
        
        
            
        
        
    st.markdown('---')


if patrim_acumulado > 0:
    st.write('### Gerenciamento de Risco')
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        invest_atual_protec = invest_atual + seguro_vida
        receita_familia = receita_conjuge + outras_receitas
        
        st.metric('Seguro Invalidez Atual', f'R$ {seguro_vida:.2f}')
        st.metric('Investimentos Atuais', f'R$ {invest_atual:.2f}')
        st.metric('Capital Total + Proteção', f'R$ {invest_atual_protec:.2f}')
        st.metric('Despesas Anuais', f'R$ {(despesa_mensal * 12):.2f}')
        st.metric('Salário Cônjuge Anual + Outras Receitas', f'R$ {(receita_familia * 12):.2f}')
        if receita_familia < despesa_mensal:
            reposicao_despesa = despesa_mensal - receita_familia
            resgate_anual_bruto = reposicao_despesa * 12 / 0.85
            st.metric('Reposição das Despesas', f'R$ {(reposicao_despesa * 12):.2f}', f'{(receita_familia/despesa_mensal-1)*100:.2f}%')
        else:
            resgate_anual_bruto = 0.0
    with col2:
        
        df_gerenc_risco, anos_gerenc_risco = calcula_gerenc_risco(invest_atual_protec, resgate_anual_bruto, juro_real)
        tab1, tab2 = st.tabs(["📈 Tempo de Consumo Capital", "🗃 Dados"])
        with tab1:
            st.subheader('Tempo de Consumo Capital')
            st.line_chart(df_gerenc_risco)
        with tab2:
            st.subheader('Dados Detalhados')
            st.dataframe(df_gerenc_risco) 
    with col3:
        
        st.metric('Tempo de Uso do Capital', f'{anos_gerenc_risco} anos')
        st.metric('Idade Que Termina o Capital', f'{idade_cliente + anos_gerenc_risco} anos')

        fig_ger_risco, ax_ger_risco = plt.subplots(figsize=(8, 6))

        ax_ger_risco.plot(df_gerenc_risco.index, df_gerenc_risco['Patrimônio'])
        ax_ger_risco.set_xlabel('Ano')
        ax_ger_risco.set_ylabel('Patrimônio')
        ax_ger_risco.set_title('Gerenciamento de Risco')
    
    
    st.markdown('---')
    
    
    st.write('### Inventário')
    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
    with col1:
        itcmd = st.number_input('Alíquota ITCMD', value=4.0, step=0.05) / 100
        tx_adv = st.number_input('Outras Taxas', value=10.0, step=0.5) / 100
        pct_inventario = st.number_input('Porcentagem do Inventário', value=50, step=1) / 100
    with col2:    
        st.metric('Previdência Privada Atual', f'R$ {prev_atual:.2f}')
        invest_atual_protec = invest_atual + seguro_vida
        st.metric('Seguro Vida Atual', f'R$ {seguro_vida:.2f}')
        st.metric('FGTS', f'R$ {(fgts):.2f}')
        st.metric('Proteções Totais', f'R$ {protect:.2f}')
    with col3:
        custo_inv = itcmd + tx_adv
        custo_inv_fin = invest_atual * custo_inv
        custo_inv_bens = bens_atual * pct_inventario * custo_inv
        st.metric('Patrimônio Financeiro', f'R$ {invest_atual:.2f}')
        st.metric('Patrimônio Imobilizado', f'R$ {bens_atual:.2f}')
    with col4:
        st.metric('Custo Inventário Ativos Financeiros', f'R$ {custo_inv_fin:.2f}')
        st.metric('Custo Inventário Bens Imobilizados', f'R$ {custo_inv_bens:.2f}')
        custo_inventario = custo_inv_fin + custo_inv_bens
        st.metric('Custo Total de Inventário', f'R$ {custo_inventario:.2f}')
    st.markdown('---')
    
    
    if receita_familia < despesa_mensal:
        st.write('### Despesas')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            tempo_despesa = st.number_input('Tempo para cobrir as despesas', value=5.0, step=0.5)
            vlr_nec_cap_hoje = npf.pv(juro_real, tempo_despesa, -reposicao_despesa * 12, 0)
            custo_total_despesa = vlr_nec_cap_hoje + custo_inventario
            st.metric(f'Valor Necessário p/ Cobertura de Despesa por {tempo_despesa:.0f} anos', f'R$ {vlr_nec_cap_hoje:.2f}')
            st.metric('Custo Total Despesas + Inventário', f'R$ {custo_total_despesa:.2f}')
        with col2:
            st.metric('Despesas Anuais', f'R$ {(despesa_mensal * 12):.2f}')
        with col3:
            st.metric('Salário Cônjuge Anual + Outras Receitas', f'R$ {(receita_familia * 12):.2f}')
        with col4:
            st.metric('Reposição das Despesas', f'R$ {(reposicao_despesa * 12):.2f}', f'{(receita_familia/despesa_mensal-1)*100:.2f}%')
        st.markdown('---')
    else: 
        custo_total_despesa = 0    
        tempo_despesa = 1
        vlr_nec_cap_hoje = 0
        


    custo_educacao = 0
    if filhos == 'Sim':    
        st.write('### Proteção de Dependentes')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            idade_term_estudos1 = st.slider('Idade de Término com Dependente', min_value=17, max_value=100, value=24, step=1)
            gasto_estudo1 = st.number_input('Custo Mensal')
            prz_term_estudos1 = idade_term_estudos1 - idade_filho1
            vlr_nec_educ1 = npf.pv(juro_real, prz_term_estudos1, -gasto_estudo1, 0) * 12
            st.metric(nome_filho1, f'R$ {vlr_nec_educ1:.2f}', f'{prz_term_estudos1:.0f} anos restantes', delta_color='off')
        with col2:
            vlr_nec_educ2 = 0
            if idade_filho2 > 0:
                idade_term_estudos2 = st.slider('Idade de Término com Dependente', min_value=17, max_value=100, value=24, step=1)
                gasto_estudo2 = st.number_input('Custo Mensal')
                prz_term_estudos2 = idade_term_estudos2 - idade_filho2
                vlr_nec_educ2 = npf.pv(juro_real, prz_term_estudos2, -gasto_estudo2, 0) * 12
                st.metric(nome_filho2, f'R$ {vlr_nec_educ2:.2f}',f'{prz_term_estudos2:.0f} anos restantes', delta_color='off')
        with col3:
            vlr_nec_educ3 = 0
            if idade_filho3 > 0:
                idade_term_estudos3 = st.slider('Idade de Término com Dependente', min_value=17, max_value=100, value=24, step=1)
                gasto_estudo3 = st.number_input('Custo Mensal')
                prz_term_estudos3 = idade_term_estudos3 - idade_filho3
                vlr_nec_educ3 = npf.pv(juro_real, prz_term_estudos3, -gasto_estudo3, 0) * 12
                st.metric(nome_filho3, f'R$ {vlr_nec_educ3:.2f}',f'{prz_term_estudos3:.0f} anos restantes', delta_color='off')
        with col4:
            vlr_nec_educ4 = 0
            if idade_filho4 > 0:
                idade_term_estudos4 = st.slider('Idade de Término com Dependente', min_value=17, max_value=100, value=24, step=1)
                gasto_estudo4 = st.number_input('Custo Mensal')
                prz_term_estudos4 = idade_term_estudos4 - idade_filho4
                vlr_nec_educ4 = npf.pv(juro_real, prz_term_estudos4, -gasto_estudo4, 0) * 12
                st.metric(nome_filho4, f'R$ {vlr_nec_educ4:.2f}',f'{prz_term_estudos4:.0f} anos restantes', delta_color='off')
        custo_educacao = vlr_nec_educ1 + vlr_nec_educ2 + vlr_nec_educ3 + vlr_nec_educ4
        st.metric('Custo Total Com Dependentes', f'R$ {custo_educacao:.2f}')
        st.markdown('---')
    
    
    st.write('### Consolidação')
    col1, col2, col3 = st.columns(3)
    custo_sucessorio = round(custo_educacao + custo_total_despesa, 2)
    df_consol = pd.DataFrame([{'Custo Sucessório': custo_sucessorio},
                              {'Proteções Atuais': invest_atual_protec}])
    
    with col1:
        st.metric('Custo Sucessório', f'R$ {custo_sucessorio:.2f}')
        st.metric('Proteções Totais', f'R$ {invest_atual_protec:.2f}')
        st.metric('Diferença', f'R$ {custo_sucessorio - invest_atual_protec:.2f}', f'{(invest_atual_protec/custo_sucessorio-1)*100:.2f}%')
    with col2:
        st.bar_chart(df_consol)
    st.markdown('---')

    consol_cat = ['Custo Sucessório', 'Proteções Atuais']
    consol_vlr = [custo_sucessorio, invest_atual_protec]

    fig_consol, ax_consol = plt.subplots(figsize=(8, 6))

    ax_consol.bar(consol_cat, consol_vlr)
    ax_consol.set_ylabel('Valor')
    ax_consol.set_title('Custo Sucessório vs. Proteções Atuais')
    

    perfil_comportamental = st.text_area('Aspectos comportamentais e pessoais do cliente')
    perfil_tecnico = st.text_area('Aspectos técnicos e específicos do cliente')
    demais_info = st.text_area('Informações complementares')
    conclusao = st.text_area('Conclusão')
    proximos_passos = st.text_area('Próximos Passos')
    st.markdown('---')

    pdf = gerar_pdf(fig_receita, fig_rec_desp, fig_patr, fig_ger_risco, fig_consol)
    st.download_button("Baixar PDF", pdf, key="download_pdf", mime="application/pdf")


st.sidebar.header('Resumo')
if idade_cliente > 0:
    st.sidebar.write(nome_cliente)
    st.sidebar.write(str(idade_cliente), 'anos')
    if estado_civil == 'Casado(a) / União Estável':
        st.sidebar.write(f'Casado(a) com {nome_conjuge}')
    if filhos == 'Sim':
        st.sidebar.write('Com o(s) Filhos(as)')
        st.sidebar.write(f'{nome_filho1} de {idade_filho1:.0f} ano(s)')
        if idade_filho2 > 0:
            st.sidebar.write(f'{nome_filho2} de {idade_filho2:.0f} ano(s)')
        if idade_filho3 > 0:
            st.sidebar.write(f'{nome_filho3} de {idade_filho3:.0f} ano(s)')
        if idade_filho4 > 0:    
            st.sidebar.write(f'{nome_filho4} de {idade_filho4:.0f} ano(s)')
    st.sidebar.write(f'Receita mensal familiar de R$ {receita_total:.2f}')
    st.sidebar.write(f'Despesa mensal familiar de R$ {despesa_mensal:.2f}')
    st.sidebar.write(f'Cap. poupança mensal de R$ {cap_poupanca:.2f}')
    st.sidebar.write(f'Investimentos R$ {invest_atual:.2f}')
    st.sidebar.write(f'Inv. Internacional R$ {invest_atual_offshore:.2f}')
    st.sidebar.write(f'Previdência R$ {prev_atual:.2f}')
    st.sidebar.write(f'Seguro de Vida R$ {seguro_vida:.2f}')
    st.sidebar.write(f'FGTS R$ {fgts:.2f}')
    st.sidebar.write(f'Valores em bens atuais R$ {bens_atual:.2f}')
    st.sidebar.write(f'Custo Inventário R$ {custo_inventario:.2f}')
    if receita_familia < despesa_mensal:
        st.sidebar.write(f'Cobertura da Despesa por {tempo_despesa:.0f} anos\nR$ {vlr_nec_cap_hoje:.2f}')
    if filhos == 'Sim':
        st.sidebar.write(f'Custos Educacionais R$ {custo_educacao:.2f}')
    st.sidebar.write(f'Proteções Totais R$ {protect:.2f}')
    st.sidebar.write(f'Custo Sucessório R$ {custo_sucessorio:.2f}')
    