# 🎙️ Pitch do Agente: FinAI

## 1. O Problema
Iniciantes em finanças pessoais enfrentam duas barreiras principais: **o excesso de jargões técnicos** que afasta o público leigo e a **falta de ferramentas confiáveis** para simular cenários reais. Além disso, a aplicação ingênua de IA Generativa no setor financeiro traz riscos sérios de **alucinações matemáticas** e vazamento de dados pessoais (PII).

## 2. A Solução (FinAI)
O **FinAI** é um assistente virtual educativo que alia a interface conversacional amigável dos modelos de linguagem à **execução determinística via código Python em sandbox**. Ele permite que usuários entendam conceitos, organizem o orçamento doméstico e simulem rendimentos sem alucinações numéricas.

## 3. Principais Inovações e Segurança
- **Zero Alucinação Numérica:** Toda matemática financeira é calculada exclusivamente via código Python isolado. LLM atua apenas para consultas gerais.
- **Orquestração Determinística:** Keywords precisos garantem fluxo correto (simulações vs. LLM fallback) — sem ambiguidade.
- **Privacidade e LGPD:** Filtro automatizado detecta e mascara dados sensíveis (CPF) antes do processamento.
- **Compliance e Guardrails:** Bloqueio rígido a recomendações diretas de investimentos + disclaimer obrigatório em todas simulações.

## 4. Roadmap v2 (Futuro)
- **RAG Híbrido com Busca Vetorial:** Embeddings (BM25 + dense retrieval) para melhor contexto em consultas gerais.
- **Indicadores em Tempo Real:** Integração com APIs do Banco Central para taxas Selic, CDI e IPCA atualizadas diariamente.
- **Análise Educativa Enriquecida:** Respostas com contexto pedagógico mais profundo e dicas práticas.
- **Amortizações Imobiliárias:** Expansão para Tabela PRICE e outras modalidades de financiamento.
