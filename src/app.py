import json
import os
import sys
from datetime import datetime

import requests
import pandas as pd
import streamlit as st
from calculator import (
    simular_juros_compostos,
    simular_financiamento_sac,
    validar_entrada_simulacao,
    extrair_numeros,
    extrair_numeros_contextualizados,
)
from prompt import DISCLAIMER_LEGAL, SYSTEM_PROMPT, sanitizar_entrada

# Define caminho base do projeto para arquivos estáticos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")


def validar_arquivos_necessarios():
    """Valida se todos os arquivos estruturados existem antes de iniciar."""
    arquivos_obrigatorios = [
        os.path.join(DATA_DIR, "produtos_financeiros.json"),
        os.path.join(DATA_DIR, "perfil_investidor.json"),
        os.path.join(DATA_DIR, "transacoes.csv"),
    ]

    arquivos_faltando = [arq for arq in arquivos_obrigatorios if not os.path.exists(arq)]

    if arquivos_faltando:
        st.error(f"❌ Arquivos estruturados faltando:\n{chr(10).join(arquivos_faltando)}")
        st.stop()



# Formata valor monetário em Real (padrão brasileiro: R$ X.XXX,XX)
def formatar_moeda(valor: float) -> str:
    """Formata número como moeda brasileira respeitando padrão BR: R$ X.XXX,XX.

    Exemplo:
        4000.5 → "R$ 4.000,50"
        8.53 → "R$ 8,53"
    """
    formatado = f"R$ {valor:,.2f}"
    return formatado.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


# Registra atendimento em log (historico_atendimento.csv)
def registrar_atendimento(pergunta: str, tipo: str, resumo: str):
    """Registra cada interação do usuário para auditoria e análise de qualidade.

    Args:
        pergunta: entrada do usuário (texto bruto ou sanitizado)
        tipo: classificação da interação ("Simulação SAC", "Simulação Juros", "Análise Gastos", "Consulta Educativa", "Erro")
        resumo: descrição breve do resultado (máx. 100 caracteres)

    Note:
        Falhas no logging não interrompem o app — registra apenas em stderr se houver erro.
    """
    try:
        # Cria dataframe com nova linha
        novo_registro = pd.DataFrame({
            "data": [datetime.now().strftime("%Y-%m-%d")],
            "assunto": [tipo],
            "resumo": [resumo[:100]]  # Limita a 100 caracteres
        })

        # Carrega histórico existente
        historico_path = os.path.join(DATA_DIR, "historico_atendimento.csv")
        try:
            historico = pd.read_csv(historico_path)
            historico = pd.concat([historico, novo_registro], ignore_index=True)
        except FileNotFoundError:
            historico = novo_registro

        # Salva de volta
        historico.to_csv(historico_path, index=False)
    except Exception as e:
        import sys
        print(f"WARN: Falha ao registrar atendimento: {e}", file=sys.stderr)

# Configuração básica da interface Streamlit
st.set_page_config(page_title="FinAI - Educador Financeiro", page_icon="💡", layout="centered")

# Valida arquivos estruturados na inicialização
validar_arquivos_necessarios()

st.title("💡 FinAI - Assistente de Finanças Pessoais")
st.caption("Aprenda sobre investimentos e faça simulações com precisão matemática exata.")


# Carrega dados estruturados (JSON e CSV) que alimentam as respostas do assistente
@st.cache_data
def carregar_base():
    """Carrega a base de conhecimento: produtos financeiros, perfil e transações."""
    with open(os.path.join(DATA_DIR, "produtos_financeiros.json"), "r", encoding="utf-8") as f:
        produtos = json.load(f)
    with open(os.path.join(DATA_DIR, "perfil_investidor.json"), "r", encoding="utf-8") as f:
        perfil = json.load(f)
    transacoes = pd.read_csv(os.path.join(DATA_DIR, "transacoes.csv"))
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
    """Monta o system prompt incluindo dados estruturados (perfil, produtos, indicadores).

    Combina:
    - System prompt base com diretrizes de comportamento e guardrails
    - Perfil do usuário (tipo de investidor, meta financeira)
    - Catálogo de produtos financeiros disponíveis
    - Indicadores de mercado de referência (SELIC, CDI, IPCA)

    Returns:
        str: prompt completo pronto para enviar ao LLM
    """
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
    """Chama o LLM local (Ollama) via API REST para respostas conversacionais educativas.

    Args:
        historico: lista de dicts com role ('user'/'assistant') e content (texto da mensagem)

    Returns:
        str: resposta do modelo Mistral

    Raises:
        ConnectionError: se Ollama não estiver rodando em localhost:11434
        Exception: para outros erros (parsing, API, etc)

    Note:
        Timeout: 600s (10 min) para dar tempo ao Mistral rodar localmente.
        Spinner mostra "Pensando..." durante a espera.
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
            timeout=600,                       # 10 minutos para Ollama local responder
        )

        # Levanta exceção se status != 2xx
        response.raise_for_status()

        # Extrai resposta do JSON retornado
        return response.json().get("response", "Erro ao gerar resposta.").strip()

    except requests.exceptions.ConnectionError:
        # Ollama não está rodando em localhost:11434
        raise ConnectionError("❌ Ollama não está rodando. Abra outro terminal e execute: `ollama serve`")
    except Exception as e:
        # Outros erros (parsing, etc)
        raise Exception(f"❌ Erro ao chamar Ollama: {str(e)[:200]}")


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
    numeros = extrair_numeros(texto_limpo)

    # FLUXO 1: Se o usuário pede simulação de financiamento (SAC)
    if any(k in query for k in ("financiamento", "financiar", "sac", "parcela", "empréstimo")) and numeros:
        # Usa parsing inteligente para mapear números ao seu significado
        params = extrair_numeros_contextualizados(texto_limpo)

        valor_total = params["valor"] if params["valor"] else 100000.0
        taxa_anual = params["taxa"] if params["taxa"] else 12.0
        meses = params["meses"] if params["meses"] else 360

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
                f"Simulação de financiamento — Tabela SAC ({formatar_moeda(valor_total)} | {taxa_anual}% a.a. | {meses} meses):\n\n"
                f"- Primeira Parcela: {formatar_moeda(res['primeira_parcela'])}\n"
                f"- Última Parcela: {formatar_moeda(res['ultima_parcela'])}\n"
                f"- Total Pago: {formatar_moeda(res['total_pago'])}\n"
                f"- Total de Juros: {formatar_moeda(res['total_juros'])}\n"
                f"{DISCLAIMER_LEGAL}"
            )

    # FLUXO 2: Se o usuário pede simulação de juros compostos (tem números + palavra-chave de simulação)
    # Só executa se FLUXO 1 não foi acionado (resposta ainda é None)
    elif resposta is None and (any(k in query for k in ("simular", "quanto rende", "simulação", "rendimento", "composto", "investir", "aplicar", "rende", "ganhar")) and numeros):
        # Usa parsing inteligente para mapear números ao seu significado
        params = extrair_numeros_contextualizados(texto_limpo)

        valor_inicial = params["valor"] if params["valor"] else 1000.0
        aporte_mensal = params["aporte"] if params["aporte"] else 0.0
        taxa_anual = params["taxa"] if params["taxa"] else 10.5
        meses = params["meses"] if params["meses"] else 12

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
                f"- Total Investido: {formatar_moeda(res['total_investido'])}\n"
                f"- Juros Acumulados: {formatar_moeda(res['total_juros'])}\n"
                f"- Saldo Final Estimado: {formatar_moeda(res['saldo_final'])}\n"
                f"{DISCLAIMER_LEGAL}"
            )

    # FLUXO 3: Análise de gastos (só executa se Fluxo 1 e 2 não foram acionados)
    elif resposta is None and any(k in query for k in ("gastos", "extrato", "orçamento", "transações", "transacoes")):
        # Valida se há dados no CSV
        if transacoes_df.empty:
            resposta = "⚠️ Nenhuma transação encontrada na base de dados. Adicione transações para análise."
        else:
            # Filtra transações com tipo "Saida" e soma os valores (já negativos)
            total_saidas = abs(transacoes_df[transacoes_df["tipo"] == "Saida"]["valor"].sum())

            # Filtra transações com tipo "Entrada" e soma os valores
            total_entradas = transacoes_df[transacoes_df["tipo"] == "Entrada"]["valor"].sum()

            # Monta resposta com resumo financeiro
            resposta = (
                f"Resumo do histórico de transações:\n\n"
                f"- Total de Entradas: {formatar_moeda(total_entradas)}\n"
                f"- Total de Saídas: {formatar_moeda(total_saidas)}\n"
                f"- Saldo: {formatar_moeda(total_entradas - total_saidas)}\n\n"
                "Quer sugestões para otimizar seu orçamento?"
            )

    else:
        # FLUXO 4: Para dúvidas gerais, chama o modelo LLM (Ollama)
        # Só executa se nenhum outro fluxo foi acionado (resposta é None)
        if resposta is None:
            try:
                with st.spinner("Pensando..."):
                    resposta = chamar_ollama(st.session_state.messages)
            except (ConnectionError, Exception) as e:
                st.error(str(e))
                resposta = None

    # Renderiza a resposta no chat e salva no histórico
    if resposta:
        # Registra o atendimento no histórico
        if any(k in query for k in ("financiamento", "financiar", "sac", "parcela", "empréstimo")):
            registrar_atendimento(texto_limpo, "Simulação SAC", f"Financiamento simulado")
        elif any(k in query for k in ("simular", "quanto rende", "simulação", "rendimento", "composto", "investir", "aplicar", "rende", "ganhar")):
            registrar_atendimento(texto_limpo, "Simulação Juros", f"Juros compostos simulados")
        elif any(k in query for k in ("gastos", "extrato", "orçamento", "transações", "transacoes")):
            registrar_atendimento(texto_limpo, "Análise Gastos", f"Resumo de transações")
        else:
            registrar_atendimento(texto_limpo, "Consulta Educativa", f"LLM respondeu")

        st.session_state.messages.append({"role": "assistant", "content": resposta})
        st.chat_message("assistant").write(resposta)
