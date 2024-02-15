import streamlit as st
import pandas as pd
import fundamentus as fd

st.set_page_config(page_title='Análise Setorial de Ações',
                    page_icon='🗄️',
                    layout='wide')

st.title('Análise Setorial de Ações')

st.markdown('---')


setores = {
    'Agropecuária': 1,
    'Água e Saneamento': 2,
    'Alimentos Processados': 3,
    'Serv.Méd.Hospit. Análises e Diagnósticos': 4,
    'Automóveis e Motocicletas': 5,
    'Bebidas': 6,
    'Comércio': 7,
    'Comércio e Distribuição': 8,
    'Computadores e Equipamentos': 9,
    'Construção Civil': 10,
    'Construção e Engenharia': 11,
    'Diversos': 12,
    'Energia Elétrica': 14,
    'Equipamentos': 15,
    'Exploração de Imóveis': 16,
    'Gás': 17,
    'Holdings Diversificadas': 18,
    'Hoteis e Restaurantes': 19,
    'Intermediários Financeiros': 20,
    'Madeira e Papel': 21,
    'Máquinas e Equipamentos': 22,
    'Materiais Diversos': 23,
    'Material de Transporte': 24,
    'Medicamentos e Outros Produtos': 25,
    'Mídia': 26,
    'Mineração': 27,
    'Outros': 28,
    'Petróleo, Gás e Biocombustíveis': 30,
    'Previdência e Seguros': 31,
    'Produtos de Uso Pessoal e de Limpeza': 32,
    'Programas e Serviços': 33,
    'Químicos': 34,
    'Serviços Diversos': 36,
    'Serviços Financeiros Diversos': 37,
    'Siderurgia e Metalurgia': 38,
    'Tecidos, Vestuário e Calçados': 39,
    'Telecomunicações': 40,
    'Transporte': 41,
    'Utilidades Domésticas': 42,
    'Viagens e Lazer': 43
}
setor = st.selectbox('Selecione o setor', list(setores.keys()))
acoes = fd.list_papel_setor(setores[setor])
acoes

det = fd.get_detalhes_papel('LEVE3')
st.write(det)
st.write(det.dtypes)
botao = st.button('Coletar Dados')
if botao:
    dados_acoes = []
    for acao in acoes:
        detalhes = fd.get_detalhes_papel(acao)
        dados_acoes.append(detalhes)
    
    df = pd.concat(dados_acoes, axis=0, ignore_index=True)
    for coluna in ['Data_ult_cot', 'Ult_balanco_processado']:
        df[coluna] = pd.to_datetime(df[coluna], format='%Y-%m-%d', errors='coerce').dt.date

    df
    st.write(df.dtypes)
