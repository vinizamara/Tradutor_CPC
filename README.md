📘 Logic Processor — Tradução entre Português e Lógica Proposicional (CPC)

🎥 Link do vídeo demonstrando o uso do Agente de IA: https://www.youtube.com/watch?v=2OQvOgXMn2M

Este repositório contém um módulo em Python que implementa dois modos principais de conversão entre linguagem natural em português e fórmulas de Lógica Proposicional Clássica (CPC).
A aplicação usa SymPy, Streamlit e o modelo Gemini (Google Generative AI) para conduzir traduções precisas e estruturadas.

✔️ 1. Desenho da arquitetura do sistema e explicação de funcionamento.
A arquitetura do sistema segue um modelo híbrido combinando:
Processamento simbólico local (via SymPy)
Tradução semântica com LLMs (via Gemini – Google Generative AI)
Interface reativa e cacheamento (via Streamlit)
Módulo unificado de orquestração (logic_processor.py)

🔷 Visão geral da arquitetura
+---------------------------------------------------------------+
|                         Interface (UI)                       |
|                         (Streamlit)                          |
+------------------------------+--------------------------------+
                               |
                               v
+---------------------------------------------------------------+
|                       Camada de Aplicação                    |
|                      (logic_processor.py)                    |
+---------------------------------------------------------------+
|   Modo 1                         |     Modo 2               |
|  NL → CPC                        |   CPC → NL               |
|   translate_nl_to_cpc            |   translate_cpc_to_nl_AI |
|----------------------------------+----------------------------|
| - Prepara prompt                 | - Prepara prompt          |
| - Chama Gemini                   | - Chama Gemini            |
| - Retorna JSON estruturado       | - Retorna JSON estruturado|
+---------------------------------------------------------------+
                               |
                               v
+---------------------------------------------------------------+
|               Camada de Manipulação Lógica (local)           |
|                       (SymPy, Regex)                         |
+---------------------------------------------------------------+
| - Parsing de fórmulas                                         |
| - Substituição de conectivos ASCII/Unicode                    |
| - Extração de proposições                                     |
+---------------------------------------------------------------+

🔷 Funcionamento resumido
Modo 1 — Português → Lógica (NL → CPC)
Usuário digita uma sentença em português.
O sistema envia para Gemini um prompt altamente restrito que:
exige JSON,
exige a fórmula no padrão (&, |, ~, ->, <->),
exige proposições formais (P, Q, R...).
A resposta é limpa e convertida para dict Python.
A SymPy não é utilizada nesse modo, pois aqui só recebemos a fórmula já simbólica.
O sistema retorna:

{
  "formula": "...",
  "propositions": { ... }
}

Modo 2 — Lógica → Português (CPC → NL)
Usuário fornece fórmula simbólica, possivelmente com Unicode (→, ∧, ¬).
A função get_variables_from_formula converte Unicode → ASCII, detecta símbolos com regex e faz parsing com SymPy.

O sistema envia ao Gemini um prompt que inclui:
A fórmula já depurada.
Um mapeamento dado pelo usuário (opcional).
Um pedido para gerar frase natural em português.
O Gemini retorna JSON estruturado, com:
frase em PT-BR,
mapeamento final de proposições.

✔️ 2. Estratégia de tradução (regras, mapeamento, uso de LLMs) e exemplos com análise.
O sistema combina tradução baseada em regras com geração neural controlada (LLM).

🔷 Estratégia no modo NL → CPC
Regras explícitas usadas:
Proposições devem ser letras maiúsculas únicas.
Conectivos obrigatórios:

& (E)

| (OU)

~ (NÃO)

-> (IMPLICA)

<-> (SE E SOMENTE SE)

Saída obrigatoriamente em JSON.

O LLM atua como:
extrator de proposições,
mapeador semântico → fórmulas,
gerador de estrutura formal.
Exemplo realista

Input:
"Se João estudar, então ele passa na prova."
LLM Output esperado:

{
  "formula": "P -> Q",
  "propositions": {
    "P": "João estuda",
    "Q": "João passa na prova"
  }
}

Análise de acertos
Identifica corretamente uma implicação.
Cria proposições com significado claro.
Possíveis erros
Criar conectivos desnecessários (“João estuda e João passa”).
Ambiguidade com pronomes (ele → outro sujeito).

🔷 Estratégia no modo CPC → NL
Regras implementadas:
Parsing completo com SymPy, aceitando:
ASCII (->, <->)
Unicode (→, ¬, ∨, etc.)
Conversão prévia de operadores (>> para Implies, % para Equivalent).
Extração de variáveis via regex [A-Z].

O LLM atua como:
gerador de frase com preservação da estrutura lógica,
parafraseador natural,
expansor de significados.

Exemplo realista:
Input:
~P | (Q -> R)
Sem mapeamento fornecido.
Possível Output do LLM:
{
  "sentence": "Ou não acontece P, ou se Q ocorrer então R acontece.",
  "propositions": {
    "P": "um certo evento P",
    "Q": "um evento Q",
    "R": "um evento R"
  }
}

Acertos:
Mantém lógica disjuntiva entre ¬P e (Q → R).
Frase natural e compreensível.

Erros típicos:
Inserir ordem temporal inexistente ("antes", "depois").
Traduzir equivalência <-> como causalidade “porque”.
Criar significados de proposições muito genéricos ou redundantes.

✔️ 3. Discussão sobre limitações e possibilidades de melhoria.
🔷 Limitações do sistema atual
1. Dependência total de LLM para a tradução semântica
Não há regras formais garantidas para assegurar que a fórmula traduzida represente exatamente o que o usuário quis dizer.
LLM pode inventar proposições ou alterar nuances semânticas.

2. Falta de verificação lógica formal
Após a tradução NL → CPC, o sistema não valida:
tautologias,
contradições,
equivalências,
coerência sintática profunda.

3. Tratamento limitado de frases complexas
Ambiguidade:
“Maria e João estudam ou trabalham” → várias interpretações.
LLM pode escolher uma interpretação sem justificar.

4. Ausência de desambiguação linguística
Não há análise sintática real; tudo depende da inferência do modelo.

5. Parsing incompleto de Unicode
A conversão manual poderia falhar para fórmulas com caracteres menos comuns.

6. Cache baseado em Streamlit
Útil, mas não adequado para ambientes de produção real (multiusuário).

🔷 Possibilidades de melhoria
1. Implementar um módulo de desambiguação linguística
Uso de NLP tradicional (spaCy, Stanza) para identificar:
sujeito,
verbo,
estrutura condicional,
coordenação/subordinação.

2. Verificação formal da fórmula produzida
checagem automática com SymPy:
se a fórmula é válida,
se está bem formada,
se tem operadores não permitidos.

3. Modo explicativo
Adicionar ao retorno:
justificativa detalhada da tradução,
árvore sintática da fórmula,
árvore de dependências da frase.

4. Treinamento de um modelo especializado
Criar LLM fine-tuned para linguagem lógica, reduzindo alucinações.

5. Editor gráfico de fórmulas
Permitir ao usuário:
visualizar estrutura como árvore lógica,
corrigir partes manualmente.

6. Testes e métricas automáticas
Comparação sistemática entre:
fórmulas produzidas,
traduções inversas,
benchmarks de lógica.
