# 💡 FinAI - Assistente Virtual Educativo de Finanças Pessoais

> Projeto desenvolvido para o Lab **"Construa Seu Assistente Virtual Com Inteligência Artificial"** da Digital Innovation One (DIO)[cite: 3].

---

## 🎯 Visão Geral
O **FinAI** é um assistente virtual voltado à educação financeira pessoal[cite: 3]. Ele auxilia usuários a entenderem conceitos sobre renda fixa, simularem investimentos/financiamentos com **precisão matemática exata via código Python** e organizarem o orçamento familiar sem o uso de jargões complexos[cite: 2, 3].

### Diferenciais Principais:
- **Zero Alucinação Matemática:** Cálculos de juros e financiamentos executados em sandbox via Python[cite: 3].
- **Segurança e Privacidade (LGPD):** Sanitização automática de PII (CPFs e dados sensíveis)[cite: 2, 3].
- **Conformidade Legal:** Inclusão automática de disclaimers operacionais em todas as simulações[cite: 3].

---

## 📁 Estrutura do Repositório

```text
finai-assistente/
├── data/                    # Dados de suporte e perfil
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   └── transacoes.csv
├── docs/                    # Documentação do desafio DIO
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
├── src/                     # Código da aplicação
│   ├── app.py               # Interface gráfica Streamlit
│   ├── calculator.py        # Calculadora determinística em Python
│   └── prompt.py            # System Prompts e Guardrails
├── requirements.txt         # Dependências do projeto
└── README.md                # Apresentação do projeto
🛠️ Tecnologias Utilizadas
Linguagem: Python 3.10+

Interface Gráfica: Streamlit

Manipulação de Dados: Pandas

Arquitetura: RAG Híbrido + Calculadora Sandbox

🚀 Como Executar Localmente
Pré-requisitos
Python 3.10 ou superior

Pip instalado

Passos
Clone o repositório:

Bash
git clone [https://github.com/SEU-USUARIO/finai-assistente.git](https://github.com/SEU-USUARIO/finai-assistente.git)
cd finai-assistente
Crie e ative um ambiente virtual (opcional, mas recomendado):

Bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate   # Windows
Instale as dependências:

Bash
pip install -r requirements.txt
Execute o aplicativo:

Bash
streamlit run src/app.py
Acesse no navegador em http://localhost:8501.