import pandas as pd
from collections import OrderedDict
import requests
import streamlit as st
from datetime import date, datetime, timedelta
from fpdf import FPDF
import tempfile
import holidays
from workadays import workdays as wd



def from_pt_br(val):
    """
    from_pt_br: fix key/label by removing pt-br stuff
    Input:
        Series, i.e., a DataFrame column
    """
    res = val

    res.replace( to_replace=r'[?]'  , value=''  , regex=True, inplace=True )
    res.replace( to_replace=r'[(]'  , value=''  , regex=True, inplace=True )
    res.replace( to_replace=r'[)]'  , value=''  , regex=True, inplace=True )
    res.replace( to_replace=r'[$]'  , value=''  , regex=True, inplace=True )
    res.replace( to_replace=r'[.]'  , value=''  , regex=True, inplace=True )
    res.replace( to_replace=r'[/]'  , value=''  , regex=True, inplace=True )

    res.replace( to_replace=r'[ç]'  , value='c' , regex=True, inplace=True )
    res.replace( to_replace=r'[âáã]', value='a' , regex=True, inplace=True )
    res.replace( to_replace=r'[ôóõ]', value='o' , regex=True, inplace=True )
    res.replace( to_replace=r'[êé]' , value='e' , regex=True, inplace=True )
    res.replace( to_replace=r'[îí]' , value='i' , regex=True, inplace=True )
    res.replace( to_replace=r'[ûú]' , value='u' , regex=True, inplace=True )
    res.replace( to_replace=r'[ÛÚ]' , value='U' , regex=True, inplace=True )

    res.replace( to_replace=r'[ ]'  , value='_' , regex=True, inplace=True )
    res.replace( to_replace=r'__'   , value='_' , regex=True, inplace=True )

    return res


def fmt_dec(val):
    """
    Fix percent:
      - replace string in pt-br
      - from '45,56%' to '45.56%'

    Input:
        Series, i.e., a DataFrame column
    """

    res = val
    res = res.replace( to_replace=r'[%]', value='' , regex=True )
    res = res.replace( to_replace=r'[.]', value='' , regex=True )
    res = res.replace( to_replace=r'[,]', value='.', regex=True )
#   res = res.astype(float)
    try:
        res = res.astype(float) / 100
    except:
        res = 0
#   res = '{:4.2f}%'.format(res)

    return res


def perc_to_float(val):
    """
    Percent to float
      - replace string in pt-br to float
      - from '45,56%' to 0.4556

    Input:
        (DataFrame, column_name)
    """

    res = val
    res = res.replace( to_replace=r'[%]', value='' , regex=True )
    res = res.replace( to_replace=r'[.]', value='' , regex=True )
    res = res.replace( to_replace=r'[,]', value='.', regex=True )
    try:
      res = res.astype(float)
    except:
      res = 0

    return res


def fundamentos_ativo(ativo): #verificar se pode substituir as funções detalhes_ativo e detalhes_ativo_magic_formula
    """
    Obtém detalhes fundamentaliastas do ativo selecionado.
    Input: str
    Output: DataFrame
    """
    url = f'https://www.fundamentus.com.br/detalhes.php?papel={ativo}'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
            'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            }
    r = requests.get(url, headers=header)
    tables = pd.read_html(r.text, decimal=',', thousands='.')

    keys = []
    values = []

    ## Table 0
    ## 'top header/summary'
    df = tables[0]
    df[0] = from_pt_br(df[0])
    df[2] = from_pt_br(df[2])

    keys = keys + list(df[0]) # Summary: Papel
    values = values + list(df[1])

    keys = keys + list(df[2]) # Summary: Cotacao
    values = values + list(df[3])

    ## Table 1
    ## Valor de mercado
    df = tables[1]
    df[0] = from_pt_br(df[0])
    df[2] = from_pt_br(df[2])

    keys = keys + list(df[0])
    values = values + list(df[1])

    keys = keys + list(df[2])
    values = values + list(df[3])

    ## Table 2
    ## 0/1: oscilacoes
    ## 2/3: indicadores
    df = tables[2].drop(0)      # remove extra header
    df[0] = from_pt_br(df[0])
    df[2] = from_pt_br(df[2])
    df[4] = from_pt_br(df[4])

    df[0] = 'Oscilacao_' + df[0]  # more specific key name

    df[1] = fmt_dec(df[1]) * 100    # oscilacoes
    df[3] = fmt_dec(df[3])    # indicadores 1
    df[5] = fmt_dec(df[5])    # indicadores 2

    keys = keys + list(df[0]) # oscilacoes
    values = values + list(df[1]) 

    keys = keys + list(df[2]) # Indicadores 1
    values = values + list(df[3])

    keys = keys + list(df[4]) # Indicadores 2
    values = values + list(df[5])

    ## Table 3
    ## balanco patrimonial
    df = tables[3].drop(0)    # remove extra line/header
    df[0] = from_pt_br(df[0])
    df[2] = from_pt_br(df[2])

    keys = keys + list(df[0])
    values = values + list(df[1])

    keys = keys + list(df[2])
    values = values + list(df[3])

    ## Table 4
    ## DRE
    tables[4] = tables[4].drop(0)   # remove: line/header
    tables[4] = tables[4].drop(1)   # remove: 'Ultimos x meses'
    df = tables[4]
    df[0] = from_pt_br(df[0])

    df[0] = df[0] + '_12m'

    keys = keys + list(df[0])
    values = values + list(df[1])

    dict = OrderedDict()
    for i, k in enumerate(keys):
        if pd.notna(k):
            dict[k] = values[i]
    fundamentos = pd.DataFrame(dict, index=[ativo])
    colunas = ['Div_Yield', 'Cres_Rec_5a', 'Marg_Bruta', 'Marg_EBIT', 'Marg_Liquida', 'EBIT_Ativo', 'ROIC', 'ROE']
    for coluna in colunas:
        fundamentos[coluna] = fundamentos[coluna] * 100
 
    return fundamentos


def lista_ativos_setores_b3(setor=None):
    """
    Setores:
      1 - Agropecuária
      2 - Água e Saneamento
      3 - Alimentos Processados
      4 - Serv.Méd.Hospit. Análises e Diagnósticos
      5 - Automóveis e Motocicletas
      6 - Bebidas
      7 - Comércio
      8 - Comércio e Distribuição
      9 - Computadores e Equipamentos
      10 - Construção Civil
      11 - Construção e Engenharia
      12 - Diversos
      13 - 
      14 - Energia Elétrica
      15 - Equipamentos
      16 - Exploração de Imóveis
      17 - Gás
      18 - Holdings Diversificadas
      19 - Hoteis e Restaurantes
      20 - Intermediários Financeiros
      21 - Madeira e Papel
      22 - Máquinas e Equipamentos
      23 - Materiais Diversos
      24 - Material de Transporte
      25 - Medicamentos e Outros Produtos
      26 - Mídia
      27 - Mineração
      28 - Outros
      29 - 
      30 - Petróleo, Gás e Biocombustíveis
      31 - Previdência e Seguros
      32 - Produtos de Uso Pessoal e de Limpeza
      33 - Programas e Serviços
      34 - Químicos
      35 - 
      36 - Serviços Diversos
      37 - Serviços Financeiros Diversos
      38 - Siderurgia e Metalurgia
      39 - Tecidos, Vestuário e Calçados
      40 - Telecomunicações
      41 - Transporte
      42 - Utilidades Domésticas
      43 - Viagens e Lazer
    
    Output:
      List
    """

    ## GET: setor
    url = f'http://www.fundamentus.com.br/resultado.php?setor={setor}'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201' ,
           'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01' ,
           'Accept-Encoding': 'gzip, deflate' ,
           }
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text,  decimal=',', thousands='.')[0]
    return list(df['Papel'])


def lista_ativos_b3():
    """
    Papel: Get list of tickers
      URL:
        http://fundamentus.com.br/detalhes.php

    Output:
      List
    """

    url = 'http://fundamentus.com.br/detalhes.php'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
           'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
           'Accept-Encoding': 'gzip, deflate',
           }
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text)[0]

    return list(df['Papel'])


def lista_fiis_b3():
    url = 'https://fundamentus.com.br/fii_resultado.php'
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
            'Accept': 'text/html, text/plain, text/css, text/sgml, */*;q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            }
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text)[0]
    return list(df['Papel'])


def detalhes_ativo_summary(ativo):
    info_papel = fundamentos_ativo(ativo)
    st.write('**Empresa:**', info_papel['Empresa'][0])
    st.write('**Setor:**', info_papel['Setor'][0])
    st.write('**Segmento:**', info_papel['Subsetor'][0])
    st.markdown('---')
    return info_papel


def detalhes_ativo(info_papel):
    st.write('**Cotação:**', f"R$ {float(info_papel['Cotacao'][0]):,.2f}")
    st.write('**Data Última Cotação:**', info_papel['Data_ult_cot'][0])
    st.write('**Valor de Mercado:**', f"R$ {float(info_papel['Valor_de_mercado'][0]):,.2f}")
    st.write('**Patrimônio Líquido:**', f"R$ {float(info_papel['Patrim_Liq'][0]):,.2f}")
    if info_papel['Setor'][0] != 'Intermediários Financeiros':
        st.write('**Receita Líquida 12m:**', f"R$ {float(info_papel['Receita_Liquida_12m'][0]):,.2f}")
        st.write('**Dívida Bruta:**', f"R$ {float(info_papel['Div_Bruta'][0]):,.2f}")
        st.write('**Dívida Líquida:**', f"R$ {float(info_papel['Div_Liquida'][0]):,.2f}")
        st.write('**Disponibilidades:**', f"R$ {float(info_papel['Disponibilidades'][0]):,.2f}")
        st.write('**Ativo Circulante:**', f"R$ {float(info_papel['Ativo_Circulante'][0]):,.2f}")
    else:
        st.write('**Cartas de Crédito:**', f"R$ {float(info_papel['Cart_de_Credito'][0]):,.2f}")
        st.write('**Depósitos:**', f"R$ {float(info_papel['Depositos'][0]):,.2f}")
        st.write('**Resultado Interm. Financ. 12m:**', f"R$ {float(info_papel['Result_Int_Financ_12m'][0]):,.2f}")
        st.write('**Receita de Serviços:**', f"R$ {float(info_papel['Rec_Servicos_12m'][0]):,.2f}")
    st.write('**Lucro Líquido 12m:**', f"R$ {float(info_papel['Lucro_Liquido_12m'][0]):,.2f}")
    st.write('**P/L:**', f"{float(info_papel['PL'][0]):,.2f}")
    st.write('**P/VP:**', f"{float(info_papel['PVP'][0]):,.2f}")
    st.write('**Dividend Yield:**', f"{float(info_papel['Div_Yield'][0]):,.2f}")
    st.write('**Margem Bruta:**', f"{float(info_papel['Marg_Bruta'][0]):,.2f}")
    st.write('**Margem Líquida:**', f"{float(info_papel['Marg_Liquida'][0]):,.2f}")
    st.markdown('---')
    st.write('**Último Balanço Processado:**', info_papel['Ult_balanco_processado'][0])


def detalhes_ativo_magic_formula(info_papel):
    st.write('**Liquidez Média 2 Meses:**', info_papel['Vol_med_2m'][0])
    st.write('**EV/EBITDA:**', f"{float(info_papel['EV_EBITDA'][0]):,.2f}")
    st.write('**ROIC:**', info_papel['ROIC'][0])
    detalhes_ativo(info_papel)
    

def magic_formula(liquidez, qtd_ativos):
    ranking = ativos_fundamentus()
    
    ranking = ranking[['Papel', 'Cotação', 'EV/EBIT', 'ROIC', 'Liq.2meses', 'P/L']]
    ranking['Empresa'] = ranking['Papel'].str[:4]
    
    int_financ = lista_ativos_setores_b3(20)
    prev_seg = lista_ativos_setores_b3(31)
    empresas_fora = int_financ + prev_seg
    mascara = ranking['Papel'].isin(empresas_fora)
    
    ranking = ranking[~mascara]
    ranking = ranking.drop_duplicates(subset='Empresa')
    ranking = ranking.set_index('Papel')
    ranking = ranking[ranking['Liq.2meses'] > liquidez]
    ranking = ranking[ranking['P/L'] > 0]
    ranking = ranking[ranking['EV/EBIT'] > 0]
    ranking = ranking[ranking['ROIC'] > 0]
    ranking = ranking.drop(columns = ['Empresa', 'P/L', 'Liq.2meses'])
    ranking['RANKING_EV/EBIT'] = ranking['EV/EBIT'].rank(ascending = True)
    ranking['RANKING_ROIC'] = ranking['ROIC'].rank(ascending = False)
    ranking['RANKING_TOTAL'] = ranking['RANKING_EV/EBIT'] + ranking['RANKING_ROIC']
    ranking = ranking.sort_values('RANKING_TOTAL')
    ranking = ranking.head(qtd_ativos)
   
    return ranking


def ativos_fundamentus():
    url = 'http://www.fundamentus.com.br/resultado.php'
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
    r = requests.get(url, headers=header)
    df = pd.read_html(r.text,  decimal=',', thousands='.')[0]
    for coluna in ['Div.Yield', 'Mrg Ebit', 'Mrg. Líq.', 'ROIC', 'ROE', 'Cresc. Rec.5a']:
        df[coluna] = df[coluna].str.replace('.', '')
        df[coluna] = df[coluna].str.replace(',', '.')
        df[coluna] = df[coluna].str.rstrip('%').astype('float')
    return df


def lista_setores():
    setores = {1: 'Agropecuária', 
               2: 'Água e Saneamento', 
               3: 'Alimentos Processados', 
               4: 'Serv.Méd.Hospit. Análises e Diagnósticos', 
               5: 'Automóveis e Motocicletas', 
               6: 'Bebidas', 
               7: 'Comércio', 
               8: 'Comércio e Distribuição', 
               9: 'Computadores e Equipamentos', 
               10: 'Construção Civil', 
               11: 'Construção e Engenharia', 
               12: 'Diversos', 
               14: 'Energia Elétrica', 
               15: 'Equipamentos', 
               16: 'Exploração de Imóveis', 
               17: 'Gás', 
               18: 'Holdings Diversificadas', 
               19: 'Hoteis e Restaurantes', 
               20: 'Intermediários Financeiros', 
               21: 'Madeira e Papel', 
               22: 'Máquinas e Equipamentos', 
               23: 'Materiais Diversos', 
               24: 'Material de Transporte', 
               25: 'Medicamentos e Outros Produtos', 
               26: 'Mídia', 
               27: 'Mineração', 
               28: 'Outros', 
               30: 'Petróleo, Gás e Biocombustíveis', 
               31: 'Previdência e Seguros', 
               32: 'Produtos de Uso Pessoal e de Limpeza', 
               33: 'Programas e Serviços', 
               34: 'Químicos', 
               36: 'Serviços Diversos', 
               37: 'Serviços Financeiros Diversos', 
               38: 'Siderurgia e Metalurgia', 
               39: 'Tecidos, Vestuário e Calçados', 
               40: 'Telecomunicações', 
               41: 'Transporte', 
               42: 'Utilidades Domésticas', 
               43: 'Viagens e Lazer'}
    return setores


def consulta_bc(codigo_bcb, data_ini = '01/01/1900', data_fim = date.today().strftime('%d/%m/%Y')):
  url = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_bcb}/dados?formato=json&dataInicial={data_ini}&dataFinal={data_fim}'
  df = pd.read_json(url)
  df['data'] = pd.to_datetime(df['data'], dayfirst=True)
  df.set_index('data', inplace=True)
  return df


def calcula_imposto_rf(lucro, prazo):
    if prazo <= 6:
        ir = lucro * 0.225
    elif prazo <= 12:
        ir = lucro * 0.20
    elif prazo <= 24:
        ir = lucro * 0.175
    else:
        ir = lucro * 0.15
    return ir


def calcula_indicadores_macro():
    selic_ano = float(consulta_bc(432).iloc[-1].values)
    cdi_ano = float(consulta_bc(1178).iloc[-1:].values)
    ipca_ano = round(float(consulta_bc(433).iloc[-12:].sum().values), 2)
    return selic_ano, cdi_ano, ipca_ano


def calcula_idade(nascimento): 
    hoje = date.today() 
    try:  
        nasc = nascimento.replace(year = hoje.year) 
  
    except ValueError:  
        nasc = nascimento.replace(year = hoje.year, 
                  month = nascimento.month + 1, day = 1) 
  
    if nasc > hoje: 
        return hoje.year - nascimento.year - 1
    else: 
        return hoje.year - nascimento.year 
    

class PDFWithFooter(FPDF):
    def header(self):
        self.image('img/logo_investsmart.png', x=65, y=5, w=84, h=22)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I',size=9)
        self.cell(0, 4, 'robson.perdigao@solutiadigital.com.br     |     11 98047-3370     |     www.solutiadigital.com.br', align='L')

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
    pdf.multi_cell(0, 9, f"Assessor de Investimentos\nRobson Perdigão Assessor", align='C')
    pdf.multi_cell(0, 100, ' ', align='C')
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
    pdf.multi_cell(0, 9, f"Esse estudo foi desenvolvido exclusivamente para você.\n\nConsiderei sua capacidade de poupança para atingir seus objetivos de curto, médio e longo prazo, adequando esses períodos ao atual cenário econômico. Conforme discutimos, é importante levar em conta sua necessidade cotidiana, orçamento pessoal, passando por rentabilidade e riscos de seus investimentos.", align='L')
    pdf.multi_cell(0, 9, f"\nMinha meta é te assessorar para que você encontre os melhores investimentos direcionados ao seu perfil e consiga fazer com que seu dinheiro renda para garantir a realização de seus planos de vida. Para isso, precisaremos de um acompanhamento e troca de informações constantes.", align='L')
    
    
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
        pdf.multi_cell(0, 9, f"Devido aos custos com {nome_filho1}, os recursos necessários serão de R$ {vlr_nec_educ1:.2f} até os {prz_term_estudos1:.2f} anos.", align='L')  
        
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


# Lista as datas de vencimentos semanais
def vencimentos_opcoes():
    # Obter o mês e ano atuais
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    ano_fim = ano_atual + 1
     
    sextas_feiras = []
    # Criar um objeto de feriados para o Brasil
    brazil_holidays = holidays.Brazil(years=[ano_atual, ano_fim])
    
    for ano in range(ano_atual, ano_fim):
        for mes in range(mes_atual, mes_atual + 13):
            # Ajustar o mês se ele ultrapassar 12
            if mes > 12:
                mes -= 12
                ano += 1
            # Obter o primeiro dia do mês
            primeiro_dia = datetime(ano, mes, 1).date()
            # Encontrar a sexta-feira do mês
            sexta_feira = primeiro_dia + timedelta(days=(4 - primeiro_dia.weekday()) % 7)
            # Verificar se a sexta-feira é um feriado brasileiro
            while sexta_feira.month == mes:
                # Verificar se a sexta-feira é um feriado brasileiro
                if sexta_feira in brazil_holidays:
                    # Se for um feriado, retornar o dia útil anterior
                    sexta_feira = sexta_feira - timedelta(days=1)
                    while sexta_feira.weekday() >= 5: # Enquanto for fim de semana
                        sexta_feira -= timedelta(days=1)
                sextas_feiras.append(sexta_feira)
                # Avançar para a próxima sexta-feira
                sexta_feira += timedelta(days=7)
    hoje = datetime.now().date()
    vencimentos = [data for data in sextas_feiras if data > hoje]
    vencimentos = [data.strftime('%d/%m/%Y') for data in vencimentos]
    
    return vencimentos


