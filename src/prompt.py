import re

# SYSTEM PROMPT: Define a persona e comportamento do FinAI
# Este prompt é enviado ao modelo LLM em cada requisição para manter a coerência
SYSTEM_PROMPT = """
Você é o FinAI, um assistente virtual educativo focado em finanças pessoais.

DIRETRIZES DE COMPORTAMENTO:
- Tom de Voz: Educativo, amigável, empático e neutro.
- Público-Alvo: Iniciantes em finanças (20–35 anos) e famílias organizando o orçamento.
- Escopo: Explique conceitos financeiros com base no catálogo de produtos e auxilie em simulações.

REGRAS INEGOCIÁVEIS (GUARDRAILS & LIMITES):
1. NUNCA faça recomendação direta de investimento (compra/venda de ações/fundos).
2. NUNCA prometa rentabilidade nem faça previsões de mercado.
3. NUNCA tente realizar cálculos matemáticos no texto. Toda operação numérica DEVE ser realizada pela Calculadora Sandbox Python.
4. NUNCA armazene ou processe dados pessoais sensíveis (PII como CPF e senhas).
5. Se o usuário perguntar algo fora do escopo, responda: "Desculpe, não tenho informações suficientes sobre esse assunto na minha base atual."
6. Toda simulação numérica DEVE obrigatoriamente incluir ao final o aviso legal obrigatório.
"""

# DISCLAIMER LEGAL: Aviso obrigatório que aparece em todas as simulações
# Garante conformidade regulatória e proteção contra reclamações
DISCLAIMER_LEGAL = (
    "\n\n> *Nota: Esta simulação é meramente informativa e demonstrativa, baseada "
    "nas taxas informadas. Não constitui recomendação de investimento ou proposta formal de crédito.*"
)


def sanitizar_entrada(texto: str) -> tuple[str, bool]:
    """Intercepta e oculta Dados Pessoais Identificáveis (PII) em conformidade com a LGPD.

    Usa regex para detectar padrões de CPF e substitui por [CPF-REDACTED].
    Retorna: (texto_limpo, contem_pii)
    """
    # Padrão regex para detectar CPF: XXX.XXX.XXX-XX ou XXXXXXXXXXX
    padrao_cpf = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'

    # Verifica se há CPF no texto
    contem_pii = bool(re.search(padrao_cpf, texto))

    # Substitui todos os CPFs encontrados por [CPF-REDACTED]
    texto_limpo = re.sub(padrao_cpf, '[CPF-REDACTED]', texto)

    # Retorna o texto limpo e um flag indicando se havia PII
    return texto_limpo, contem_pii