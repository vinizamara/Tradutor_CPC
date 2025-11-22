# logic_processor.py

import sympy
from sympy.logic.boolalg import Implies, Equivalent
import google.generativeai as genai
import json
import re
import streamlit as st


# ============================================================
# MODO 1 — Tradução de Português → Lógica (CPC)
# ============================================================

@st.cache_data
def translate_nl_to_cpc(sentence: str, api_key: str) -> dict:
    """
    Converte uma sentença em Português para uma fórmula de Lógica Proposicional (CPC)
    utilizando o modelo Gemini.
    
    A resposta é estruturada em JSON contendo:
    - formula: expressão lógica usando &, |, ~, ->, <-> 
    - propositions: mapeamento de proposições (P, Q, R...) para seus significados
    """
    try:
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0.1,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            generation_config=generation_config,
        )

        # Prompt especificando regras formais para a saída
        prompt_template = f"""
        Sua tarefa é atuar como um especialista em lógica proposicional.
        Traduza a seguinte sentença em português para uma fórmula de Cálculo Proposicional Clássico (CPC).

        Regras de Formatação da Saída:
        1. Use 'P', 'Q', 'R', etc.
        2. Conectivos aceitos:
           &  (E), | (OU), ~ (NÃO), -> (IMPLICA), <-> (SE E SOMENTE SE)
        3. Retorne somente o JSON especificado.

        JSON de exemplo:
        {{
          "formula": "P -> (Q | R)",
          "propositions": {{
            "P": "significado de P",
            "Q": "significado de Q",
            "R": "significado de R"
          }}
        }}

        Sentença de Entrada:
        "{sentence}"

        JSON de Saída:
        """

        response = model.generate_content(prompt_template)

        # Limpeza do bloco JSON retornado
        cleaned_response = (
            response.text.strip()
            .replace("```json\n", "")
            .replace("\n```", "")
        )

        return json.loads(cleaned_response)

    except Exception as e:
        print(f"Erro na API do Gemini: {e}")
        return {"error": str(e)}


# ============================================================
# Preparação de operadores para parsing (Modo 2)
# ============================================================

try:
    _A, _B = sympy.symbols('A B')
    OPERADOR_RSHIFT = sympy.sympify('_A >> _B').func   # usado para →
    OPERADOR_MOD = sympy.sympify('_A % _B').func       # usado para ↔
except Exception:
    OPERADOR_RSHIFT = None
    OPERADOR_MOD = None


# ============================================================
# Extrai variáveis de uma fórmula lógica
# ============================================================

@st.cache_data
def get_variables_from_formula(formula_str: str) -> set:
    """
    Recebe uma fórmula lógica e retorna o conjunto de variáveis encontradas.
    Aceita tanto ASCII (&, |, ->) quanto símbolos Unicode (∧, ∨, →).
    """
    if not formula_str:
        return set()

    try:
        # Converte conectivos Unicode para ASCII intermediários
        processed_str = (
            formula_str.replace("∧", "&")
                       .replace("∨", "|")
                       .replace("¬", "~")
                       .replace("→", "->")
                       .replace("↔", "<->")
                       .replace("<->", "%")     # operador equivalente
                       .replace("->", ">>")     # operador implica
        )

        # Identifica proposições maiúsculas (P, Q, R...)
        symbol_names = sorted(list(set(re.findall(r'[A-Z]', formula_str))))
        symbols_dict = {name: sympy.symbols(name) for name in symbol_names}

        # Interpreta a expressão usando SymPy
        parsed_formula = sympy.sympify(processed_str, locals=symbols_dict)

        # Substitui operadores intermediários pelos operadores lógicos corretos
        if OPERADOR_RSHIFT and ">>" in processed_str:
            parsed_formula = parsed_formula.subs(OPERADOR_RSHIFT, Implies)
        if OPERADOR_MOD and "%" in processed_str:
            parsed_formula = parsed_formula.subs(OPERADOR_MOD, Equivalent)

        # Retorna apenas símbolos atômicos encontrados
        atoms = parsed_formula.atoms(sympy.Symbol)
        return {str(atom) for atom in atoms}

    except Exception as e:
        print(f"Erro ao parsear a fórmula: {e}")
        return set()


# ============================================================
# MODO 2 — Tradução de Lógica → Português (CPC → NL)
# ============================================================

@st.cache_data
def translate_cpc_to_nl_AI(formula_str: str, api_key: str, user_propositions: dict = None) -> dict:
    """
    Converte uma fórmula de Lógica Proposicional (CPC) em uma frase em Português.

    Se user_propositions for fornecido:
        - O modelo deve usar exatamente essas definições ao montar a frase.

    Caso contrário:
        - O modelo cria proposições coerentes e as utiliza na geração da frase.

    Retorno em JSON inclui:
    - sentence: frase final em português
    - propositions: proposições usadas e seus significados
    """
    try:
        genai.configure(api_key=api_key)

        generation_config = {
            "temperature": 0.7,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            generation_config=generation_config,
        )

        # Texto explicando o mapa fornecido pelo usuário (se existir)
        if user_propositions:
            items = [f'"{k}": "{v}"' for k, v in sorted(user_propositions.items())]
            user_map_txt = (
                "Usar o seguinte mapeamento de proposições fornecido pelo usuário:\n"
                + "{ " + ", ".join(items) + " }\n\n"
            )
        else:
            user_map_txt = "Se o usuário não fornecer significados, crie proposições coerentes.\n\n"

        # Prompt detalhado
        prompt_template = f"""
        Sua tarefa é atuar como um professor de lógica criativo.
        Você receberá uma fórmula de Cálculo Proposicional Clássico (CPC).

        {user_map_txt}

        Instruções:
        1. Analise a fórmula: {formula_str}
        2. Use o mapeamento fornecido (se houver).
        3. Caso contrário, crie proposições simples e coerentes.
        4. Gere uma frase natural em português que represente fielmente a estrutura lógica.
        5. Retorne APENAS o JSON no formato especificado:

        {{
          "sentence": "Frase construída",
          "propositions": {{
            "P": "Significado de P",
            "Q": "Significado de Q"
          }}
        }}

        Fórmula:
        "{formula_str}"

        JSON de Saída:
        """

        response = model.generate_content(prompt_template)

        cleaned_response = (
            response.text.strip()
            .replace("```json\n", "")
            .replace("\n```", "")
        )

        return json.loads(cleaned_response)

    except Exception as e:
        print(f"Erro na API do Gemini (Modo 2): {e}")
        return {"error": str(e)}
