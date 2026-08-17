import json

import requests
import pandas as pd
import streamlit as st
from calculator import (
    simular_juros_compostos,
    simular_financiamento_sac,
    validar_entrada_simulacao,
    extrair_numeros,
)
from prompt import DISCLAIMER_LEGAL, SYSTEM_PROMPT, sanitizar_entrada

# Configuração básica da interface Streamlit
st.set_page_config(page_title="FinAI - Educador Financeiro", page_icon="💡", layout="centered")
st.title("💡 FinAI - Assistente de Finanças Pessoais")
st.caption("Aprenda sobre investimentos e faça simulações com precisão matemática exata.")


# Carrega dados estruturados (JSON e CSV) que alimentam as respostas do assistente
@st.cache_data
def carregar_base():
    """Carrega a base de conhecimento: produtos financeiros, perfil e transações."""
    with open("data/produtos_financeiros.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)
    with open("data/perfil_investidor.json", "r", encoding="utf-8") as f:
        perfil = json.load(f)
    transacoes = pd.read_csv("data/transacoes.csv")
    return produtos, perfil, transacoes


produtos_db, perfil_db, transacoes_df = carregar_base()

# Inicializa o histórico de conversa na sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o FinAI. Como posso te ajudar a entender ou organizar suas finanças hoje?"}
    ]

# Painel lateral com informações do usuário
st.sidebar.header("👤 Perfil do Usuário")
st.sidebar.markdown(f"**Perfil:** {perfil_db['perfil_investidor']}")
st.sidebar.markdown(f"**Meta:** {perfil_db['meta_financeira']}")
st.sidebar.markdown("---")
st.sidebar.header("📊 Indicadores de Referência")
st.sidebar.info("• SELIC: 10.50% a.a.\n• CDI: 10.40% a.a.\n• IPCA: 3.90% a.a.")

# Renderiza o histórico de mensagens no chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# Constrói o prompt de sistema com contexto personalizado
def construir_system_prompt() -> str:
    """Monta o system prompt incluindo os dados estruturados (perfil, produtos, indicadores)."""
    # Serializa base de conhecimento em JSON para incluir no prompt
    produtos_txt = json.dumps(produtos_db, ensure_ascii=False, indent=2)
    perfil_txt = json.dumps(perfil_db, ensure_ascii=False, indent=2)

    # Combina system prompt base + dados contextuais personalizados
    return (
        SYSTEM_PROMPT
        + f"""

PERFIL DO USUÁRIO:
{perfil_txt}

CATÁLOGO DE PRODUTOS FINANCEIROS:
{produtos_txt}

INDICADORES DE MERCADO (referência):
- SELIC: 10.50% a.a.
- CDI: 10.40% a.a.
- IPCA: 3.90% a.a.
"""
    )


# Função que chama o modelo LLM local (Ollama) para respostas conversacionais
def chamar_ollama(historico: list) -> str:
    """Envia o histórico de conversa ao Ollama e retorna a resposta do modelo.

    Trata erros de conexão e timeout.
    """
    try:
        # Filtra apenas mensagens com role válido (user/assistant)
        mensagens = [m for m in historico if m["role"] in ("user", "assistant")]

        # Remove mensagens de assistant do início (garante que começa com user)
        while mensagens and mensagens[0]["role"] != "user":
            mensagens.pop(0)

        # Validação: garante que há pelo menos uma mensagem
        if not mensagens:
            return "Por favor, faça uma pergunta."

        # Formata histórico em texto simples (USER: ... ASSISTANT: ...)
        historico_texto = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in mensagens
        )

        # Monta prompt final = system + histórico + instrução de resposta
        prompt = f"""{construir_system_prompt()}

HISTÓRICO DA CONVERSA:
{historico_texto}

RESPOSTA:"""

        # Chama API REST do Ollama em localhost:11434
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,                # Desativa streaming (resposta completa)
                "temperature": 0.7,             # Controla criatividade (0-1)
            },
            timeout=600,                        # Aguarda até 10 minutos
        )

        # Levanta exceção se status != 2xx
        response.raise_for_status()

        # Extrai resposta do JSON retornado
        return response.json().get("response", "Erro ao gerar resposta.").strip()

    except requests.exceptions.ConnectionError:
        # Ollama não está rodando em localhost:11434
        return (
            "❌ Ollama não está rodando. Abra outro terminal e execute: `ollama serve`"
        )
    except Exception as e:
        # Outros erros (timeout, parsing, etc)
        return f"❌ Erro: {str(e)[:200]}"


if user_input := st.chat_input("Digite sua dúvida, peça uma simulação ou resumo de gastos..."):
    # Sanitiza o input removendo dados sensíveis (CPF, etc) conforme LGPD
    texto_limpo, contem_pii = sanitizar_entrada(user_input)
    st.session_state.messages.append({"role": "user", "content": texto_limpo})
    st.chat_message("user").write(texto_limpo)

    # Avisa o usuário se dados sensíveis foram detectados
    if contem_pii:
        alerta = "⚠️ *Dados sensíveis (CPF) foram identificados e ocultados para sua segurança (LGPD).*"
        st.session_state.messages.append({"role": "assistant", "content": alerta})
        st.chat_message("assistant").write(alerta)

    query = texto_limpo.lower()
    resposta = None

    # FLUXO 1: Se o usuário pede simulação de financiamento (SAC)
    if any(k in query for k in ("financiamento", "sac", "parcela", "empréstimo")):
        numeros = extrair_numeros(texto_limpo)

        # Define valores padrão ou extrai do input do usuário
        valor_total = numeros[0] if numeros else 100000.0
        taxa_anual = numeros[1] if len(numeros) > 1 else 12.0
        meses = int(numeros[2]) if len(numeros) > 2 else 360

        # Valida os números antes de executar a simulação
        valido, erro = validar_entrada_simulacao(
            valor_total=valor_total,
            taxa_anual=taxa_anual,
            meses=meses
        )

        if not valido:
            resposta = erro
        else:
            res = simular_financiamento_sac(valor_total, taxa_anual, meses)
            resposta = (
                f"Simulação de financiamento — Tabela SAC (R$ {valor_total:,.0f} | {taxa_anual}% a.a. | {meses} meses):\n\n"
                f"- 🏦 **Primeira Parcela:** R$ {res['primeira_parcela']:.2f}\n"
                f"- 📉 **Última Parcela:** R$ {res['ultima_parcela']:.2f}\n"
                f"- 💸 **Total Pago:** R$ {res['total_pago']:.2f}\n"
                f"- 💡 **Total de Juros:** R$ {res['total_juros']:.2f}"
                f"{DISCLAIMER_LEGAL}"
            )
    # FLUXO 2: Se o usuário pede simulação de juros compostos
    elif any(k in query for k in ("simular", "quanto rende", "simulação", "rendimento")):
        numeros = extrair_numeros(texto_limpo)

        # Define valores padrão ou extrai do input do usuário
        valor_inicial = numeros[0] if numeros else 1000.0
        aporte_mensal = numeros[1] if len(numeros) > 1 else 100.0
        taxa_anual = numeros[2] if len(numeros) > 2 else 10.5
        meses = int(numeros[3]) if len(numeros) > 3 else 12

        # Valida os números antes de executar a simulação
        valido, erro = validar_entrada_simulacao(
            valor_inicial=valor_inicial,
            aporte_mensal=aporte_mensal,
            taxa_anual=taxa_anual,
            meses=meses
        )

        if not valido:
            resposta = erro
        else:
            res = simular_juros_compostos(valor_inicial, aporte_mensal, taxa_anual, meses)
            resposta = (
                f"Simulação de juros compostos ({taxa_anual}% a.a., {meses} meses):\n\n"
                f"- 💵 **Total Investido:** R$ {res['total_investido']:.2f}\n"
                f"- 📈 **Juros Acumulados:** R$ {res['total_juros']:.2f}\n"
                f"- 💰 **Saldo Final Estimado:** R$ {res['saldo_final']:.2f}"
                f"{DISCLAIMER_LEGAL}"
            )
    elif any(k in query for k in ("gastos", "extrato", "orçamento", "transações", "transacoes")):
        # FLUXO 3: Análise de gastos do usuário usando dados do CSV
        # Filtra transações com tipo "Saida" e soma os valores (já negativos)
        total_saidas = abs(transacoes_df[transacoes_df["tipo"] == "Saida"]["valor"].sum())

        # Filtra transações com tipo "Entrada" e soma os valores
        total_entradas = transacoes_df[transacoes_df["tipo"] == "Entrada"]["valor"].sum()

        # Monta resposta com resumo financeiro
        resposta = (
            f"Resumo do histórico de transações:\n\n"
            f"- 💚 **Total de Entradas:** R$ {total_entradas:.2f}\n"
            f"- 🔴 **Total de Saídas:** R$ {total_saidas:.2f}\n"
            f"- 📊 **Saldo:** R$ {(total_entradas - total_saidas):.2f}\n\n"
            "Quer sugestões para otimizar seu orçamento?"
        )
    else:
        # FLUXO 4: Para dúvidas gerais, chama o modelo LLM (Ollama)
        # Não é uma simulação específica, então usa IA conversacional
        with st.spinner("Pensando..."):
            resposta = chamar_ollama(st.session_state.messages)

    # Renderiza a resposta no chat e salva no histórico
    if resposta:
        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.chat_message("assistant").write(resposta)
