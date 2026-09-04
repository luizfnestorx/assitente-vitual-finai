# Edge Cases e Limitações do Parsing de Números

## 📋 Resumo

O módulo `calculator.py` extrai e interpreta números em português brasileiro.
Funciona bem em ~95% dos casos, mas tem limitações conhecidas documentadas aqui.

---

## ✅ Casos que Funcionam Bem

### Padrão Brasileiro Completo
```
"simular 1.000,50" → 1000.5 ✅
"taxa de 10,5%" → 10.5 ✅
"R$ 4.500,00" → 4500.0 ✅
```

### Múltiplos Números com Contexto
```
"3000 em 12 meses a 10%" 
→ valor: 3000, meses: 12, taxa: 10 ✅
```

### Heurística de Valor Principal
```
"tenho 500 de dívida mas simular 10000"
→ valor: 10000 (maior número > 100) ✅
```

---

## ⚠️ Casos Problemáticos (Edge Cases)

### 1. **Números Muito Próximos em Contexto**
```
"financiar 5000 com aporte 5000"
→ Pode confundir qual é valor e qual é aporte
Solução: Ser específico ("com aporte de 500" ou "aporte 500 reais")
```

### 2. **Números com Notação Científica**
```
"investir 1e6" (1 milhão em notação científica)
→ NÃO RECONHECIDO (regex não cobre)
Solução: Digitar "1.000.000" ou "1000000"
```

### 3. **Números Formatados Inconsistentes**
```
"R$ 1.000,00 e R$ 2000,50"
→ Pode pegar só o primeiro e ignorar o segundo
Solução: Ser consistente na formatação
```

### 4. **Ponto como Separador Ambíguo**
```
"10.5 taxa" → Interpretado como 10.5 (decimal, certo)
"100.0" → Interpretado como 100 (milhar removido, certo)
"1.000.000" → Interpretado como 1 milhão (certo)
```
Heurística: Se ≤2 dígitos após ponto = decimal, senão = milhar ✅

### 5. **Valor Zero Interpretado como Ausente**
```
"aporte de 0 reais"
→ Retorna None (interpretado como não fornecido)
Solução: Validação posterior trata aporte zero como válido
```

### 6. **Períodos Mistos (dia/mês/ano)**
```
"em 2 anos" → Não capturado como 24 meses
"em 18 semanas" → Não capturado como 4 meses
Solução: Sempre usar "meses" ou "parcelas"
```

---

## 🛡️ Proteções Implementadas

### Validação de Entrada
- ✅ Rejeita valores ≤ 0 (exceto aporte_mensal)
- ✅ Rejeita valores > R$ 1 milhão
- ✅ Valida período (meses > 0)

### Tratamento de Erro
- ✅ Se parsing falha, retorna None
- ✅ Se valor falta, usa default educativo (ex: R$ 1.000)
- ✅ Sempre mostra os valores usados na resposta

### LGPD
- ✅ Sanitiza CPF automaticamente
- ✅ Não armazena dados pessoais

---

## 📖 Recomendações ao Usuário

Ao digitar uma pergunta, seja o mais claro possível:

❌ **Ruim:**
```
"simule com alguns números"
"quanto rende isso?"
"10000 1000 24 12%"
```

✅ **Bom:**
```
"simular R$ 10.000 com aporte de R$ 1.000 por 24 meses a 12% a.a."
"investir 5000 reais em 12 meses com taxa 10,5%"
"financiar 100.000 por 60 meses com taxa 6%"
```

---

## 🔮 Melhorias Futuras

1. Adicionar suporte a períodos em dias/semanas/anos com conversão automática
2. Usar ML/NLP para disambiguar valores (estimar qual é valor vs aporte)
3. Adicionar validação de entrada mais inteligente (ex: perguntar ao usuário se houver ambiguidade)
4. Suporte a notação científica (1e6, 2.5e3)
5. Log detalhado de parsing para debug

---

## 🧪 Como Testar Edge Cases

```bash
# Rode os testes
pytest tests/test_calculator.py -v

# Teste manual com exemplos edge
python3 -c "
from src.calculator import extrair_numeros_contextualizados
print(extrair_numeros_contextualizados('tenho 500 de dívida mas simular 10000 com taxa 8%'))
"
```

---

**Última atualização:** 2025-09-04
**Status:** Production-ready com limitações documentadas ✅
