# 🧠 Documentação da Base de Conhecimento e Estratégia de Dados (FinAI)

## 1. Visão Geral e Objetivos de Dados

A base de conhecimento do **FinAI** alimenta o motor conversacional (LLM) e a calculadora em sandbox com dados financeiros estruturados e seguros.

O ecossistema atende a dois propósitos fundamentais:
1. **Personalização da Experiência:** Orientar o usuário considerando seu perfil e objetivo (faixa etária de 20–35 anos, iniciantes em finanças, famílias).
2. **Confiabilidade e Precisão:** Manter dados e produtos alinhados aos indicadores oficiais (SELIC, CDI, IPCA).
3. **Privacidade e Conformidade (LGPD):** Bloquear a persistência e processamento não autorizado de Dados Pessoais Identificáveis (PII).

---

## 2. Estrutura de Dados Estruturados (`data/`)

### A. Perfil do Cliente (`data/perfil_investidor.json`)
Caracterização simplificada de risco e metas do usuário para contextualizar as respostas do agente.

```json
{
  "cliente_id": "CLI-102938",
  "faixa_etaria": "25-30",
  "perfil_investidor": "Moderado",
  "meta_financeira": "Reserva de Emergência e Viagem",
  "horizonte_investimento": "Médio Prazo (1 a 3 anos)",
  "experiencia_previa": "Iniciante"
}
```

### B. Catálogo de Produtos Financeiros (`data/produtos_financeiros.json`)
Catálogo simplificado de produtos para consultas educativas e comparações neutras.

```json
[
  {
    "id": "PROD-01",
    "nome": "CDB Liquidez Diária",
    "categoria": "Renda Fixa",
    "indexador": "CDI",
    "rentabilidade": "100% do CDI",
    "risco": "Baixo",
    "liquidez": "Diária (D+0)",
    "garantia_fgc": true,
    "indicacao": "Reserva de Emergência"
  },
  {
    "id": "PROD-02",
    "nome": "Tesouro Selic 2029",
    "categoria": "Renda Fixa Pública",
    "indexador": "SELIC",
    "rentabilidade": "Selic + 0.05%",
    "risco": "Muito Baixo",
    "liquidez": "Diária (D+1)",
    "garantia_fgc": false,
    "indicacao": "Preservação de Capital"
  }
]
```

### C. Histórico de Transações (`data/transacoes.csv`)
Base de apoio para simulações de organização de orçamento doméstico.

```csv
data,categoria,descricao,valor,tipo
2026-08-01,Alimentacao,Supermercado Central,-250.00,Saida
2026-08-02,Transporte,Posto de Combustivel,-180.00,Saida
2026-08-03,Rendimento,Proventos CDB,+45.20,Entrada
2026-08-04,Lazer,Restaurante,-120.00,Saida
2026-08-05,Investimento,Aporte CDB Liquidez Diaria,-500.00,Saida
```

---

## 3. Estratégia de Recuperação de Contexto (Versão Atual)

O **FinAI** utiliza uma abordagem **simples e determinística** de carregamento de dados:

```mermaid
flowchart TD
    A[Prompt Sanitizado do Usuário] --> B{Tipo de Requisição?}
    
    B -->|Simulação: Financiamento| C[Fluxo 1: SAC]
    B -->|Simulação: Juros| D[Fluxo 2: Juros Compostos]
    B -->|Análise: Gastos| E[Fluxo 3: Extrato]
    B -->|Consulta Geral| F[Fluxo 4: LLM + Contexto]
    
    C --> G[Calculadora Python]
    D --> G
    E --> H[Análise CSV]
    F --> I[LLM recebe contexto]
    
    G --> J[Resposta com Disclaimer]
    H --> J
    I --> J
```

### Componentes de Busca (Atuais):
1. **Identificação de Intenção (Keywords):** Regex e keywords determinísticos detectam tipo de requisição
2. **Dados Estáticos em Memória:** `produtos_financeiros.json` e `perfil_investidor.json` carregados ao iniciar
3. **Passagem de Contexto ao LLM:** Dados são serializados em JSON e incluídos no system prompt para consultas gerais

### Indicadores de Referência:
Os valores de SELIC, CDI e IPCA são **atualizados manualmente** no código quando há mudanças oficiais. Não há atualização automática.

---

## 4. Governança, Proteção de Dados (LGPD) e Integridade

1. **Anonimização de PII na Entrada:** O sistema mascareia dados pessoais sensíveis antes do armazenamento ou envio ao LLM (ex.: substitui CPFs por `[CPF-REDACTED]`).
2. **Separação de Papéis:** O contexto estruturado serve apenas para o LLM receber informações. Toda operação matemática é delegada à Calculadora Sandbox em Python.
3. **Trilha de Auditoria (Audit Trail):** Registro em log estruturado contendo apenas o prompt sanitizado, as ferramentas consultadas e os resultados numéricos retornados.
