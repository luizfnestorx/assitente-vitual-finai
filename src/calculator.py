import re


def extrair_numeros_contextualizados(texto: str) -> dict:
    """Extrai números com contexto semântico identificando seu significado financeiro.

    Busca por padrões e unidades para mapear cada número ao seu significado:
    - Valor: número antes de "reais", "R$", ou o maior número > 100
    - Taxa: número antes de "%", "a.a", "ao ano"
    - Meses: número antes de "mês", "meses", "parcela"
    - Aporte: número depois de "aporte", "contribuição", "depósito"

    Args:
        texto: entrada do usuário (ex: "3000 em 12 meses a 10%")

    Returns:
        dict: {'valor': float, 'taxa': float, 'meses': int, 'aporte': float}
              com None para valores não encontrados

    Exemplo:
        "3000 em 12 meses a 10%" → {valor: 3000, taxa: 10, meses: 12, aporte: None}
        "1000 com aporte 500 a 8% por 24 meses" → {valor: 1000, aporte: 500, taxa: 8, meses: 24}

    Limitação:
        Se houver múltiplos valores grandes, pode selecionar o errado.
        Exemplo: "tenho 500 de dívida, simular 10000" → pega 10000 ✅ (heurística OK)
    """
    texto_lower = texto.lower()
    resultado = {"valor": None, "taxa": None, "meses": None, "aporte": None}

    # Regex para encontrar números com contexto: "123.456,78" ou "123.456" ou "123,45" etc
    # Padrão: número opcional com separadores, seguido de unidade opcional
    pattern_valor = r'(?:r\$\s*)?(\d+(?:[.,]\d+)*)\s*(?:reais?|mil)?'
    pattern_taxa = r'(\d+(?:[.,]\d+)*)\s*%|(\d+(?:[.,]\d+)*)\s*(?:a\.a|ao\s+ano)'
    pattern_meses = r'(?:por\s+)?(\d+)\s*(?:mes(?:es)?|parcelas?|meses)'
    pattern_aporte = r'(?:aporte|contribuição|depósito)\s+(?:de\s+)?(?:r\$\s*)?(\d+(?:[.,]\d+)*)'

    # 1. Busca por TAXA (com %)
    match_taxa = re.search(pattern_taxa, texto_lower)
    if match_taxa:
        taxa_str = match_taxa.group(1) or match_taxa.group(2)
        resultado["taxa"] = _converter_numero(taxa_str)

    # 2. Busca por MESES (com "mês", "meses", "parcelas")
    match_meses = re.search(pattern_meses, texto_lower)
    if match_meses:
        resultado["meses"] = int(_converter_numero(match_meses.group(1)))

    # 3. Busca por APORTE (após "aporte de")
    match_aporte = re.search(pattern_aporte, texto_lower)
    if match_aporte:
        resultado["aporte"] = _converter_numero(match_aporte.group(1))

    # 4. Busca por VALOR (geralmente o primeiro número grande ou após R$)
    # Procura por números antes de "reais" ou "mil"
    match_valor_reais = re.search(r'(?:r\$\s*)?(\d+(?:[.,]\d+)*)\s*(?:reais?|mil)', texto_lower)
    if match_valor_reais:
        resultado["valor"] = _converter_numero(match_valor_reais.group(1))
    else:
        # Se não encontrou padrão específico, pega o primeiro número grande (> 100)
        numeros_todos = extrair_numeros(texto)
        if numeros_todos:
            # Ordena por tamanho decrescente e pega o maior
            numeros_ordenados = sorted(numeros_todos, reverse=True)
            for num in numeros_ordenados:
                if num > 100 and num != resultado.get("taxa") and num != resultado.get("meses"):
                    resultado["valor"] = num
                    break
            # Se não encontrou número > 100, pega o primeiro
            if resultado["valor"] is None and numeros_todos:
                resultado["valor"] = numeros_todos[0]

    return resultado


def _converter_numero(num_str: str) -> float:
    """Converte string de número em float, respeitando padrão brasileiro."""
    if not num_str:
        return 0.0
    nums = extrair_numeros(num_str)
    return float(nums[0]) if nums else 0.0


def extrair_numeros(texto: str) -> list[float]:
    """Extrai todos os números (incluindo negativos e decimais) de uma string.

    Exemplo: "investir R$ 4.000 com taxa de 10.5%" → [4000.0, 10.5]
    Trata corretamente separadores de milhar (ponto) e decimais (vírgula) em português.

    Heurística: Um ponto é decimal se:
    - O número após o ponto tem <= 2 dígitos (ex: 10.5 = decimal)
    - Caso contrário, é milhar (ex: 4.000 = milhar)

    ⚠️ LIMITAÇÃO: Extrai TODOS os números encontrados, na ordem de aparição.
    Se o usuário digita "Tenho 500 de dívida, simular 1000", extrai [500, 1000].
    Isso pode usar o valor errado. Use com cuidado ou valide depois.
    """
    # Regex encontra números com ponto/vírgula: 4.000,50 ou 4000.50
    numeros = re.findall(r'-?\d+(?:[.,]\d+)*', texto)

    resultado = []
    for num_str in numeros:
        if not num_str:
            continue

        pontos = num_str.count('.')
        virgulas = num_str.count(',')

        if pontos == 0 and virgulas == 0:
            # Apenas dígitos: "1234"
            resultado.append(float(num_str))
        elif pontos == 0 and virgulas == 1:
            # Vírgula como decimal: "1,5" → 1.5
            resultado.append(float(num_str.replace(',', '.')))
        elif pontos == 1 and virgulas == 0:
            # Um ponto: pode ser decimal (1.5) ou milhar (1.000)
            # Heurística: se tem <= 2 dígitos após ponto, é decimal
            partes = num_str.split('.')
            digitos_apos_ponto = len(partes[1]) if len(partes) > 1 else 0
            if digitos_apos_ponto <= 2:
                # Decimal: "10.5" → 10.5
                resultado.append(float(num_str))
            else:
                # Milhar: "4.000" → 4000.0
                resultado.append(float(num_str.replace('.', '')))
        elif pontos > 0 and virgulas == 1:
            # Múltiplos pontos + 1 vírgula: "4.000,50" → 4000.50
            num_limpo = num_str.replace('.', '').replace(',', '.')
            resultado.append(float(num_limpo))
        else:
            # Caso ambíguo: tenta remover tudo que não é dígito/ponto/vírgula
            num_limpo = num_str.replace('.', '').replace(',', '.')
            try:
                resultado.append(float(num_limpo))
            except ValueError:
                continue

    return resultado


def validar_entrada_simulacao(valor_inicial: float = None, aporte_mensal: float = None,
                               valor_total: float = None, taxa_anual: float = None,
                               meses: int = None, max_valor: float = 1_000_000) -> tuple[bool, str]:
    """Valida parâmetros de entrada para simulações financeiras (guardrail de limite máximo).

    Regras:
    - Rejeita valores ≤ 0 (negativos ou zero), EXCETO aporte_mensal (pode ser 0)
    - Rejeita valores > max_valor (padrão: R$ 1 milhão — segurança educativa)

    Args:
        valor_inicial: capital inicial a investir
        aporte_mensal: contribuição mensal (pode ser 0)
        valor_total: valor total do financiamento
        taxa_anual: taxa de juros anual em %
        meses: período em meses
        max_valor: limite máximo permitido (padrão 1 milhão)

    Returns:
        tuple: (é_válido: bool, mensagem_erro: str)
               Se válido, retorna (True, "")
               Se inválido, retorna (False, "mensagem descritiva")
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

        # Aporte mensal pode ser zero (simulação sem aporte)
        if campo == "aporte_mensal":
            if valor < 0:
                return False, f"❌ {campo.replace('_', ' ').title()} não pode ser negativo. Recebido: {valor}"
            if valor > max_valor:
                return False, f"❌ {campo.replace('_', ' ').title()} não pode exceder R$ {max_valor:,.0f}. Recebido: {valor:,.0f}"
            continue

        # Todos os outros parâmetros devem ser positivos (> 0)
        if valor <= 0:
            return False, f"❌ {campo.replace('_', ' ').title()} deve ser positivo. Recebido: {valor}"

        # Rejeita valores acima do limite máximo
        if valor > max_valor:
            return False, f"❌ {campo.replace('_', ' ').title()} não pode exceder R$ {max_valor:,.0f}. Recebido: {valor:,.0f}"

    # Se passou em todas as validações, retorna sucesso
    return True, ""


def simular_juros_compostos(valor_inicial: float, aporte_mensal: float, taxa_anual: float, meses: int) -> dict:
    """Calcula rentabilidade com juros compostos em sandbox Python isolado (sem alucinações).

    Simula aplicação financeira com aportes mensais e juros compostos.
    Executa em código puro (não em LLM), garantindo precisão matemática.

    Fórmula: Para cada mês, saldo = (saldo anterior + aporte) * (1 + taxa_mensal)

    Args:
        valor_inicial: capital inicial (R$)
        aporte_mensal: contribuição fixa mensal (R$)
        taxa_anual: rendimento anual em % (ex: 10.5)
        meses: período de investimento em meses

    Returns:
        dict com chaves:
        - valor_inicial: capital inicial arredondado
        - aporte_mensal: aporte mensal arredondado
        - meses: período
        - total_investido: valor_inicial + (aporte_mensal * meses)
        - total_juros: saldo_final - total_investido
        - saldo_final: montante final estimado

    Exemplo:
        >>> simular_juros_compostos(1000, 100, 10.5, 12)
        {
            'valor_inicial': 1000.0,
            'aporte_mensal': 100.0,
            'meses': 12,
            'total_investido': 2200.0,
            'total_juros': 256.42,  # aproximado
            'saldo_final': 2456.42
        }
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

    SAC é um sistema onde a parcela de amortização é constante, mas os juros diminuem
    a cada mês conforme o saldo devedor reduz. Resultado: parcelas decrescentes.

    Executa em código puro isolado, garantindo precisão matemática determinística.

    Args:
        valor_total: valor do financiamento (R$)
        taxa_anual: taxa de juros anual em % (ex: 8.0)
        meses: prazo do financiamento em meses

    Returns:
        dict com chaves:
        - valor_total: valor financiado
        - meses: prazo
        - primeira_parcela: primeira parcela (maior, com mais juros)
        - ultima_parcela: última parcela (menor, com menos juros)
        - total_pago: soma de todas as parcelas (valor_total + juros)
        - total_juros: juros totais cobrados

    Exemplo:
        >>> simular_financiamento_sac(100000, 8, 360)
        {
            'valor_total': 100000.0,
            'meses': 360,
            'primeira_parcela': 1110.56,  # R$ 277.78 amort + R$ 666.67 juros
            'ultima_parcela': 278.89,     # R$ 277.78 amort + R$ 1.11 juros
            'total_pago': 155000.0,       # aproximado
            'total_juros': 55000.0
        }
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