# 💡 FinAI - Assistente Virtual de Finanças Pessoais

> Projeto desenvolvido para o Lab **"Construa Seu Assistente Virtual Com Inteligência Artificial"** da Digital Innovation One (DIO).

---

## 🎯 Sobre o Projeto

O **FinAI** é um assistente virtual educativo focado em educação financeira pessoal. Auxilia usuários a entenderem conceitos sobre investimentos, simularem rendimentos com precisão matemática e organizarem seu orçamento, sem jargões técnicos.

### ✨ Diferenciais

- **Zero Alucinação Matemática** — Cálculos em sandbox Python isolado
- **Segurança LGPD** — CPF automaticamente mascarado
- **Guardrails** — Recusa recomendações diretas e previsões
- **Disclaimer Legal** — Obrigatório em todas as simulações

---

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+
- Ollama local (opcional) ou Chave Anthropic API

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/luizfnestorx/assitente-vitual-finai.git
cd assitente-vitual-finai

# 2. Crie ambiente virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Inicie o Ollama (em outro terminal)
ollama serve

# 5. Execute a aplicação
streamlit run src/app.py
```

Acesse em `http://localhost:8501`

---

## 📁 Estrutura

```
src/
├── app.py              # Interface Streamlit
├── calculator.py       # Simulações (juros, SAC)
└── prompt.py           # System prompt + Segurança LGPD

data/
├── perfil_investidor.json
├── produtos_financeiros.json
├── transacoes.csv
└── historico_atendimento.csv

docs/
├── 01-documentacao-agente.md
├── 02-base-de-conhecimento.md
├── 03-prompts.md
├── 04-metricas.md
└── 05-pitch.md

requirements.txt        # Dependências
README.md              # Este arquivo
```

---

## 📊 Tecnologias

- **Python 3.10+** — Linguagem
- **Streamlit** — Interface
- **Ollama/Anthropic** — LLM
- **Pandas** — Dados
- **Regex** — Segurança LGPD

---

## 🧪 Como Usar

```
"simular com 1000"                          → Simulação de juros
"financiar 100000 por 10 anos com taxa 8"  → Tabela SAC
"quanto rendo em 12 meses?"                 → Cálculo determinístico
"qual a diferença entre CDB e Tesouro?"    → Explicação educativa
"Meu CPF é 123.456.789-00"                 → Sanitizado automaticamente
```

---

## 📚 Documentação

Veja a documentação completa em `docs/`:

- **01-documentacao-agente.md** — Arquitetura técnica
- **02-base-de-conhecimento.md** — RAG Híbrido
- **03-prompts.md** — System prompts
- **04-metricas.md** — Testes e qualidade
- **05-pitch.md** — Pitch do projeto

---

## 📝 Licença

MIT License - Veja LICENSE para detalhes.
