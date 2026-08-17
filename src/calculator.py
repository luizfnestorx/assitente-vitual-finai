import re


def extrair_numeros(texto: str) -> list[float]:
    """Extrai todos os números (incluindo negativos e decimais) de uma string.

    Exemplo: "investir -500 com taxa de 10.5%" → [-500.0, 10.5]
    Usado para parsear o input do usuário e extrair valores para as simulações.
    """
    # Regex: -? (negativo opcional) \d+ (dígitos) (?:\.?,?\d+)* (decimais opcionais)
    numeros = re.findall(r'-?\d+(?:\.?,?\d+)*', texto.replace(',', '.'))
    # Converte para float e remove strings vazias
    return [float(n) for n in numeros if n]


def validar_entrada_simulacao(valor_inicial: float = None, aporte_mensal: float = None,
                               valor_total: float = None, taxa_anual: float = None,
                               meses: int = None, max_valor: float = 1_000_000) -> tuple[bool, str]:
    """Valida parâmetros de entrada para simulações financeiras.

    Regras:
    - Rejeita valores ≤ 0 (negativos ou zero)
    - Rejeita valores > max_valor (padrão: R$ 1 milhão)

    Retorna: (é_válido, mensagem_erro)
    """
    # Dicionário de parâmetros a validar (None = parâmetro não fornecido)
    limites = {
        "valor_inicial": valor_inicial,
        "aporte_mensal": aporte_mensal,
        "valor_total": valor_total,
        "taxa_anual": taxa_anual,
        "meses": meses
    }

    # Itera sobre cada parâmetro fornecido
    for campo, valor in limites.items():
        if valor is None:
            continue  # Pula parâmetros não fornecidos

        # Rejeita valores não-positivos (negativos ou zero)
        if valor <= 0:
            return False, f"❌ {campo.replace('_', ' ').title()} deve ser positivo. Recebido: {valor}"

        # Rejeita valores acima do limite máximo
        if valor > max_valor:
            return False, f"❌ {campo.replace('_', ' ').title()} não pode exceder R$ {max_valor:,.0f}. Recebido: {valor:,.0f}"

    # Se passou em todas as validações, retorna sucesso
    return True, ""


def simular_juros_compostos(valor_inicial: float, aporte_mensal: float, taxa_anual: float, meses: int) -> dict:
    """Calcula rentabilidade com juros compostos em sandbox Python de forma determinística.

    Fórmula: Montante = (Valor Inicial + Aporte * N) * (1 + taxa_mensal)^N
    Garante precisão matemática SEM alucinações de IA.

    Retorna dict com valores consolidados.
    """
    # Converte taxa anual em taxa mensal (composição mensal)
    taxa_mensal = (1 + (taxa_anual / 100)) ** (1 / 12) - 1

    # Inicializa o saldo com o valor inicial
    saldo = valor_inicial

    # Total investido = valor inicial + aporte mensal repetido N vezes
    total_investido = valor_inicial + (aporte_mensal * meses)

    # Simula mês a mês: adiciona aporte, aplica juros
    for _ in range(meses):
        saldo = (saldo + aporte_mensal) * (1 + taxa_mensal)

    # Calcula juros totais acumulados
    total_juros = saldo - total_investido

    # Retorna resultado formatado com 2 casas decimais
    return {
        "valor_inicial": round(valor_inicial, 2),
        "aporte_mensal": round(aporte_mensal, 2),
        "meses": meses,
        "total_investido": round(total_investido, 2),
        "total_juros": round(total_juros, 2),
        "saldo_final": round(saldo, 2)
    }


def simular_financiamento_sac(valor_total: float, taxa_anual: float, meses: int) -> dict:
    """Simula amortização via Tabela SAC (Sistema de Amortização Constante) sem alucinações.

    A Tabela SAC reduz a parcela ao longo do tempo (parcelas decrescentes).
    Garante precisão matemática determinística via código Python isolado.

    Retorna dict com primeira parcela, última parcela, total pago e total de juros.
    """
    # Amortização constante = valor total dividido pelo número de meses
    amortizacao = valor_total / meses

    # Taxa mensal = taxa anual / 12 / 100
    taxa_mensal = taxa_anual / 100 / 12

    # Primeira parcela = amortização + juros sobre o saldo inicial (valor_total)
    primeira_parcela = amortizacao + (valor_total * taxa_mensal)

    # Última parcela = amortização + juros sobre a última amortização
    ultima_parcela = amortizacao + (amortizacao * taxa_mensal)

    # Calcula total pago iterando sobre cada mês
    # Juros decrescem conforme o saldo devedor diminui
    total_pago = sum(
        amortizacao + ((valor_total - (i * amortizacao)) * taxa_mensal)
        for i in range(meses)
    )

    # Retorna resultado com 2 casas decimais
    return {
        "valor_total": round(valor_total, 2),
        "meses": meses,
        "primeira_parcela": round(primeira_parcela, 2),
        "ultima_parcela": round(ultima_parcela, 2),
        "total_pago": round(total_pago, 2),
        "total_juros": round(total_pago - valor_total, 2)
    }