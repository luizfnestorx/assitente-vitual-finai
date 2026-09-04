import sys
sys.path.insert(0, 'src')

from calculator import extrair_numeros, validar_entrada_simulacao, simular_juros_compostos, simular_financiamento_sac
from prompt import sanitizar_entrada
import pytest


# ============================================================================
# TESTES DE CALCULADORA - JUROS COMPOSTOS (4 testes)
# ============================================================================

def test_simular_juros_compostos_basico():
    resultado = simular_juros_compostos(1000, 0, 10.5, 12)
    assert resultado['valor_inicial'] == 1000.0
    assert resultado['meses'] == 12
    assert resultado['saldo_final'] > 1000  # Deve ter ganho juros


def test_simular_juros_compostos_com_aporte():
    resultado = simular_juros_compostos(1000, 100, 10, 12)
    assert resultado['valor_inicial'] == 1000.0
    assert resultado['aporte_mensal'] == 100.0
    assert resultado['saldo_final'] > 1000 + (100 * 12)  # Capital + aportes + juros


def test_simular_juros_compostos_taxa_zero():
    resultado = simular_juros_compostos(1000, 0, 0, 12)
    assert resultado['total_juros'] == 0
    assert resultado['saldo_final'] == 1000.0


def test_simular_juros_compostos_valor_final():
    resultado = simular_juros_compostos(1000, 0, 10.5, 12)
    assert 1100 < resultado['saldo_final'] < 1300  # Intervalo esperado


# ============================================================================
# TESTES DE CALCULADORA - FINANCIAMENTO SAC (4 testes)
# ============================================================================

def test_simular_financiamento_sac_basico():
    resultado = simular_financiamento_sac(100000, 8, 36)
    assert resultado['valor_total'] == 100000.0
    assert resultado['meses'] == 36


def test_simular_financiamento_sac_valor_final():
    resultado = simular_financiamento_sac(100000, 8, 36)
    assert resultado['total_pago'] > 100000  # Deve ter juros


def test_simular_financiamento_sac_juros():
    resultado = simular_financiamento_sac(100000, 8, 36)
    assert resultado['total_juros'] > 0
    assert resultado['total_juros'] == round(resultado['total_pago'] - 100000, 2)


def test_simular_financiamento_sac_amortizacao():
    resultado = simular_financiamento_sac(100000, 8, 36)
    amortizacao_mensal = 100000 / 36
    # Verifica que a primeira parcela é maior que a última (parcelas decrescentes em SAC)
    assert resultado['primeira_parcela'] > resultado['ultima_parcela']



# ============================================================================
# TESTES DE VALIDAÇÃO (7 testes)
# ============================================================================

def test_validar_valor_negativo():
    valido, msg = validar_entrada_simulacao(valor_inicial=-500)
    assert not valido
    assert "positivo" in msg.lower()


def test_validar_valor_zero():
    valido, msg = validar_entrada_simulacao(valor_inicial=0)
    assert not valido


def test_validar_valor_acima_limite():
    valido, msg = validar_entrada_simulacao(valor_inicial=2000000)
    assert not valido
    assert "1" in msg and "000" in msg  # Verifica se menciona o limite de 1 milhão



def test_validar_limite_1_milhao():
    valido, msg = validar_entrada_simulacao(valor_inicial=1000000)
    assert valido


def test_validar_multiplos_campos():
    valido, msg = validar_entrada_simulacao(
        valor_inicial=1000,
        taxa_anual=-5,
        meses=12
    )
    assert not valido


def test_validar_valor_positivo():
    valido, msg = validar_entrada_simulacao(valor_inicial=1000)
    assert valido
    assert msg == ""


def test_validar_valor_pequeno():
    valido, msg = validar_entrada_simulacao(valor_inicial=1)
    assert valido


# ============================================================================
# TESTES DE EXTRAÇÃO DE NÚMEROS (5 testes)
# ============================================================================

def test_extrair_numeros_positivos():
    numeros = extrair_numeros("simular com 1000 reais")
    assert 1000.0 in numeros


def test_extrair_numeros_negativos():
    numeros = extrair_numeros("simule -500")
    assert -500.0 in numeros


def test_extrair_numeros_decimais():
    numeros = extrair_numeros("taxa de 10.5%")
    assert 10.5 in numeros


def test_extrair_multiplos_numeros():
    numeros = extrair_numeros("simule 1000 a 10.5% por 12 meses")
    assert len(numeros) >= 3
    assert 1000.0 in numeros
    assert 10.5 in numeros
    assert 12.0 in numeros


def test_extrair_vazio():
    numeros = extrair_numeros("qual a diferenca entre CDB e Tesouro?")
    assert len(numeros) == 0


# ============================================================================
# TESTES DE SEGURANÇA LGPD (4 testes)
# ============================================================================

def test_sanitizar_cpf_com_formatacao():
    texto, pii = sanitizar_entrada("Meu CPF é 123.456.789-00")
    assert "[CPF-REDACTED]" in texto
    assert pii == True


def test_sanitizar_cpf_sem_formatacao():
    texto, pii = sanitizar_entrada("CPF 12345678900 aqui")
    assert "[CPF-REDACTED]" in texto
    assert pii == True


def test_sanitizar_sem_cpf():
    texto, pii = sanitizar_entrada("Simule R$ 1000")
    assert "[CPF-REDACTED]" not in texto
    assert pii == False


def test_deteccao_pii():
    texto, pii = sanitizar_entrada("123.456.789-00")
    assert pii == True


# ============================================================================
# TESTES DE GUARDRAILS (3 testes)
# ============================================================================

def test_guardrail_recomendacao_compra():
    msg = "Qual ação comprar agora?"
    assert any(k in msg.lower() for k in ["compre", "comprar", "compra"])


def test_guardrail_previsao_mercado():
    msg = "Quanto o dólar vai subir?"
    assert any(k in msg.lower() for k in ["vai subir", "vai cair", "previsão"])


def test_permitir_pergunta_educativa():
    msg = "O que é juros compostos?"
    assert "juros" in msg.lower()
    assert not any(k in msg.lower() for k in ["compre", "venda", "prevejo"])
