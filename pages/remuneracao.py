import streamlit as st

def calcular_irrf_anual(salario_base_mensal, dependentes, despesa_educacao_titular=0, despesa_educacao_dependentes=0, despesas_medicas=0):
    salario_base_anual = salario_base_mensal * 12
    dependentes_anual = dependentes

    inss_anual = 0.1 * salario_base_anual  # Considerando uma alíquota de 10% para o INSS anualmente

    base_calculo_anual = salario_base_anual - inss_anual - (dependentes_anual * 189.59 * 12)  # Dedução de R$ 189,59 por dependente anualmente

    # Adicionando deduções anualmente
    base_calculo_anual -= despesa_educacao_titular * 12
    base_calculo_anual -= despesa_educacao_dependentes * 12
    base_calculo_anual -= despesas_medicas * 12

    # Tabela progressiva do imposto de renda - alíquotas e parcela a deduzir
    faixas = [(24511.93, 0, 0),
              (33919.80, 0.075, 1838.39),
              (45012.60, 0.15, 4382.38),
              (55976.16, 0.225, 7758.32),
              (0, 0.275, 10557.13)]

    # Cálculo do IRRF anual
    irrf_anual = 0
    for faixa in reversed(faixas):
        if base_calculo_anual > faixa[0]:
            irrf_anual = (base_calculo_anual - faixa[0]) * faixa[1] + faixa[2]
            break

    # Cálculo do salário líquido anual
    salario_liquido_anual = salario_base_anual - inss_anual - irrf_anual

    return {'inss_anual': inss_anual, 'irrf_anual': irrf_anual, 'salario_liquido_anual': salario_liquido_anual}

# Exemplo de uso
salario_mensal = float(input("Digite o salário base mensal: "))
dependentes = int(input("Digite a quantidade de dependentes: "))
despesa_educacao_titular = float(input("Digite a despesa com educação do titular: "))
despesa_educacao_dependentes = float(input("Digite a despesa com educação dos dependentes: "))
despesas_medicas = float(input("Digite o valor das despesas médicas: "))

resultado_anual = calcular_irrf_anual(salario_mensal, dependentes, despesa_educacao_titular, despesa_educacao_dependentes, despesas_medicas)

print(f"Imposto de Renda Retido na Fonte (IRRF) anual: R$ {resultado_anual['irrf_anual']:.2f}")
print(f"INSS anual: R$ {resultado_anual['inss_anual']:.2f}")
print(f"Salário líquido anual: R$ {resultado_anual['salario_liquido_anual']:.2f}")

class util:
    def __init__(self, resultado):
        self.resultado = 1+1
