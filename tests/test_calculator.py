import pytest
import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import (
    simular_juros_compostos,
    simular_financiamento_sac,
    validar_entrada_simulacao,
    extrair_numeros,
)


class TestCalculadoraJurosCompostos:
    """Testes para a calculadora de juros compostos."""

    def test_calculo_basico(self):
        """Testa cálculo básico de juros compostos."""
        resultado = simular_juros_compostos(1000, 100, 10.5, 12)

        assert resultado["valor_inicial"] == 1000.0
        assert resultado["aporte_mensal"] == 100.0
        assert resultado["meses"] == 12
        assert resultado["total_investido"] == 2200.0
        assert resultado["saldo_final"] > resultado["total_investido"]

    def test_sem_aporte_mensal(self):
        """Testa cálculo apenas com valor inicial, sem aporte."""
        resultado = simular_juros_compostos(1000, 0, 10.5, 12)

        assert resultado["aporte_mensal"] == 0.0
        assert resultado["total_investido"] == 1000.0
        assert resultado["saldo_final"] > 1000.0

    def test_taxa_zero(self):
        """Testa com taxa de juros zero."""
        resultado = simular_juros_compostos(1000, 100, 0, 12)

        assert resultado["total_juros"] == 0.0
        assert resultado["saldo_final"] == resultado["total_investido"]

    def test_precisao_decimal(self):
        """Verifica se os valores têm exatamente 2 casas decimais."""
        resultado = simular_juros_compostos(1000.123, 100.456, 10.5, 12)

        assert len(str(resultado["valor_inicial"]).split(".")[-1]) <= 2
        assert len(str(resultado["saldo_final"]).split(".")[-1]) <= 2


class TestCalculadoraSAC:
    """Testes para a calculadora de Tabela SAC."""

    def test_calculo_basico_sac(self):
        """Testa cálculo básico de SAC."""
        resultado = simular_financiamento_sac(100000, 12, 360)

        assert resultado["valor_total"] == 100000.0
        assert resultado["meses"] == 360
        assert resultado["primeira_parcela"] > 0
        assert resultado["ultima_parcela"] > 0
        assert resultado["primeira_parcela"] > resultado["ultima_parcela"]
        assert resultado["total_pago"] > resultado["valor_total"]

    def test_sac_juros_corretos(self):
        """Verifica se os juros totais estão corretos."""
        resultado = simular_financiamento_sac(100000, 12, 360)

        juros_calculados = resultado["total_pago"] - resultado["valor_total"]
        assert abs(resultado["total_juros"] - juros_calculados) < 0.01

    def test_sac_parcela_decrescente(self):
        """Verifica se as parcelas são decrescentes na SAC."""
        resultado = simular_financiamento_sac(100000, 12, 360)

        # Na SAC, primeira parcela > última parcela (juros diminuem)
        assert resultado["primeira_parcela"] > resultado["ultima_parcela"]

    def test_sac_com_taxa_zero(self):
        """Testa SAC com taxa zero."""
        resultado = simular_financiamento_sac(100000, 0, 360)

        # Sem juros, primeira = última (todas iguais)
        assert abs(resultado["primeira_parcela"] - resultado["ultima_parcela"]) < 0.01
        assert resultado["total_juros"] == 0.0


class TestValidacaoEntrada:
    """Testes para validação de entrada."""

    def test_valor_negativo_rejeitado(self):
        """Verifica se valores negativos são rejeitados."""
        valido, erro = validar_entrada_simulacao(valor_inicial=-1000)

        assert valido is False
        assert "deve ser positivo" in erro.lower()
        assert "-1000" in erro

    def test_valor_zero_rejeitado(self):
        """Verifica se zero é rejeitado."""
        valido, erro = validar_entrada_simulacao(valor_inicial=0)

        assert valido is False
        assert "deve ser positivo" in erro.lower()

    def test_valor_acima_limite_rejeitado(self):
        """Verifica se valores > 1M são rejeitados."""
        valido, erro = validar_entrada_simulacao(valor_inicial=2000000)

        assert valido is False
        assert "não pode exceder" in erro.lower()
        assert "1,000,000" in erro

    def test_valor_no_limite_aceito(self):
        """Verifica se 1M é aceito."""
        valido, erro = validar_entrada_simulacao(valor_inicial=1000000)

        assert valido is True
        assert erro == ""

    def test_valor_valido_aceito(self):
        """Verifica se valor válido é aceito."""
        valido, erro = validar_entrada_simulacao(valor_inicial=50000)

        assert valido is True
        assert erro == ""

    def test_multiplos_valores_um_invalido(self):
        """Verifica se rejeita quando um valor é inválido."""
        valido, erro = validar_entrada_simulacao(
            valor_inicial=10000,
            aporte_mensal=-500,
            taxa_anual=10.5
        )

        assert valido is False
        assert "aporte mensal" in erro.lower()

    def test_todos_valores_validos(self):
        """Verifica se aceita quando todos os valores são válidos."""
        valido, erro = validar_entrada_simulacao(
            valor_inicial=10000,
            aporte_mensal=500,
            taxa_anual=10.5,
            meses=12
        )

        assert valido is True


class TestExtrairNumeros:
    """Testes para extração de números do texto."""

    def test_extrai_numero_positivo(self):
        """Extrai número positivo simples."""
        numeros = extrair_numeros("simular com 1000")

        assert len(numeros) > 0
        assert 1000 in numeros

    def test_extrai_numero_negativo(self):
        """Extrai número negativo."""
        numeros = extrair_numeros("simular com -500")

        assert -500 in numeros

    def test_extrai_multiplos_numeros(self):
        """Extrai múltiplos números de uma string."""
        numeros = extrair_numeros("simular 5000 com 200 em 24 meses")

        assert len(numeros) >= 2
        assert 5000 in numeros
        assert 200 in numeros
        assert 24 in numeros

    def test_extrai_numero_decimal(self):
        """Extrai número com decimal."""
        numeros = extrair_numeros("taxa de 10.5")

        assert 10.5 in numeros

    def test_sem_numeros(self):
        """Retorna lista vazia quando não há números."""
        numeros = extrair_numeros("qual a diferença entre CDB e Tesouro")

        assert len(numeros) == 0


# ============================================================================
# TESTES DE GUARDRAILS (SEGURANÇA)
# ============================================================================

class TestGuardrailsPII:
    """Testes para proteção de PII (LGPD)."""

    def test_mascara_cpf_simples(self):
        """Verifica se CPF é mascarado."""
        from prompt import sanitizar_entrada

        texto = "Meu CPF é 123.456.789-00"
        texto_limpo, contem_pii = sanitizar_entrada(texto)

        assert contem_pii is True
        assert "[CPF-REDACTED]" in texto_limpo
        assert "123.456.789-00" not in texto_limpo

    def test_detecta_pii(self):
        """Verifica se detecta presença de PII."""
        from prompt import sanitizar_entrada

        texto = "Meu CPF é 987.654.321-11"
        _, contem_pii = sanitizar_entrada(texto)

        assert contem_pii is True

    def test_sem_pii_nao_alerta(self):
        """Verifica se não detecta PII quando não há."""
        from prompt import sanitizar_entrada

        texto = "Quanto rendo com 1000 reais em 12 meses?"
        _, contem_pii = sanitizar_entrada(texto)

        assert contem_pii is False

    def test_cpf_sem_formatacao(self):
        """Verifica se mascara CPF sem formatação."""
        from prompt import sanitizar_entrada

        texto = "Meu CPF é 12345678900"
        texto_limpo, contem_pii = sanitizar_entrada(texto)

        assert contem_pii is True
        assert "[CPF-REDACTED]" in texto_limpo


class TestGuardrailsRecomendacoes:
    """Testes para guardrail de recomendações diretas."""

    def test_rejeita_recomendacao_compra(self):
        """Verifica se rejeita "qual ação comprar"."""
        query = "qual ação devo comprar agora".lower()

        # Simula a lógica de guardrail
        recomendacao_trigger = any(k in query for k in ["compre", "comprar", "qual", "melhor"])

        assert recomendacao_trigger is True

    def test_rejeita_predicao_mercado(self):
        """Verifica se rejeita previsões de mercado."""
        query = "vai subir ou descer a bolsa".lower()

        previsao_trigger = any(k in query for k in ["vai", "subir", "descer", "previsão"])

        assert previsao_trigger is True

    def test_permite_pergunta_educativa(self):
        """Verifica se permite perguntas educativas."""
        query = "qual a diferença entre CDB e Tesouro".lower()

        # Não contém triggers de recomendação
        recomendacao_trigger = any(k in query for k in ["compre", "venda", "recomenda"])
        previsao_trigger = any(k in query for k in ["vai subir", "vai descer"])

        assert recomendacao_trigger is False
        assert previsao_trigger is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
