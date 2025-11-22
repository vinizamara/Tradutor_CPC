import streamlit as st
import logic_processor as lp
from streamlit_option_menu import option_menu
import re

# Configuração inicial da página
st.set_page_config(
  page_title="Agente de IA Lógico",
  page_icon="🤖",
  layout="centered"
)

# Força o navegador a não traduzir o conteúdo da interface
st.markdown("""
<meta name="google" content="notranslate">
<style>
  .notranslate { translate: no !important; }
  body { translate: no !important; }
</style>
""", unsafe_allow_html=True)

# Carrega e aplica estilos visuais personalizados
def load_css():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        body { font-family: "Inter", sans-serif; }

        .stButton > button {
          font-family: "Inter", sans-serif; 
          border: none;
          background-color: #007bff;
          color: white;
          padding: 0.75em 1.5em;
          border-radius: 50px;
          font-weight: 600;
          width: 100%;
          transition: all 0.3s ease;
        }
        .stButton > button:hover { background-color: #0056b3; }

        .stTextInput > div > div > input,
        .stTextArea > div > textarea {
            background-color: #1a1c24 !important;
            color: #FAFAFA !important;
            border-radius: 10px;
            border: 1px solid #31333f;
            font-size: 1.1rem;
        }

        /* Remove bordas decorativas dos containers */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

st.title("Tradutor - Agente de IA", anchor=False)
st.caption("Projeto acadêmico de IA - Uni-FACEF")

# Carrega chave da API (se disponível no secrets)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("Chave de API do Google Gemini não encontrada!")
    api_key = None

# Menu para alternar entre os modos de tradução
selected_mode = option_menu(
  menu_title=None, 
  options=["Português ⭢ Lógica", "Lógica ⭢ Português"],
  icons=["translate", "code-slash"], 
  orientation="horizontal",
  styles={
    "container": {"padding": "0!important", "background-color": "#0E1117"},
    "nav-link": {"font-size": "1.1rem", "--hover-color": "#262730"},
    "nav-link-selected": {"background-color": "#007bff"},
  }
)

st.write("---")

# ============================================================
# MODO 1 — Tradução de Português → Lógica (CPC)
# ============================================================

if selected_mode == "Português ⭢ Lógica":
  
    st.markdown("Esse modo converte frases em Português para fórmulas do Cálculo Proposicional Clássico.")
    st.subheader("Insira a sentença")

    nl_input = st.text_area(
        "Label escondido",
        placeholder="Exemplo: Se não estiver chovendo, eu vou à praia.",
        label_visibility="collapsed",
        height=80
    )

    # Aciona a função de tradução e grava o resultado no estado
    if st.button("Traduzir para CPC", key="btn_nl_translate", disabled=(api_key is None), use_container_width=True):
        if not nl_input:
            st.warning("Por favor, insira uma sentença.")
        else:
            with st.spinner("A IA está pensando..."):
                try:
                    result = lp.translate_nl_to_cpc(nl_input, api_key)
                    st.session_state["nl_result"] = result
                except Exception as e:
                    st.error(f"Erro inesperado: {e}")

    # Exibe o resultado da tradução caso exista
    if "nl_result" in st.session_state:

        result = st.session_state["nl_result"]

        st.subheader("Resultado (Lógica CPC):")

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown("**Fórmula Lógica:**")
            st.code(result.get("formula"), language="plaintext")

            st.markdown("**Significados das proposições:**")
            propositions = result.get("propositions", {}) or {}
            for key, value in propositions.items():
                st.markdown(f"- **{key}** = {value}")

# ============================================================
# MODO 2 — Tradução de Lógica → Português
# ============================================================

if selected_mode == "Lógica ⭢ Português":
  
    st.markdown("Esse modo converte fórmulas de lógica proposicional para frases em Português.")
    st.subheader("Insira a fórmula lógica")

    cpc_input = st.text_area(
        "Label escondido",
        placeholder="Exemplo: (P ∧ Q) -> R",
        label_visibility="collapsed",
        height=80
    )

    # Extrai variáveis presentes na fórmula e salva no estado
    if st.button("Traduzir para Português", key="btn_cpc", disabled=(api_key is None), use_container_width=True):
        if not cpc_input:
            st.error("Por favor, insira uma fórmula.")
        else:
            variables = lp.get_variables_from_formula(cpc_input)
            if not variables:
                st.error("Fórmula inválida!")
            else:
                st.session_state["cpc_vars"] = variables
                st.session_state["cpc_formula"] = cpc_input

    # Formulário de definição dos significados das proposições
    if "cpc_vars" in st.session_state:

        vars = st.session_state["cpc_vars"]
        formula = st.session_state["cpc_formula"]

        st.markdown("**Defina os significados das proposições:**")

        saved_map = st.session_state.get("mapping", {})
        user_map = {}

        for var in sorted(list(vars)):
            default = saved_map.get(var, "")
            val = st.text_input(f"{var} =", value=default, key=f"map_{var}")
            if val.strip():
                user_map[var] = val.strip()

        st.caption("Se algum campo estiver vazio, a IA poderá sugerir automaticamente.")

        # Gera a frase em português com base na fórmula e no mapa fornecido
        if st.button("Gerar frase", key="btn_generate_pt"):
            with st.spinner("Gerando sentença..."):
                try:
                    result = lp.translate_cpc_to_nl_AI(
                        formula,
                        api_key,
                        user_propositions=user_map or None
                    )

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.subheader("Resultado em Português:")
                        st.markdown(f"### 💬 *{result['sentence']}*")

                        st.markdown("**Proposições usadas:**")
                        propositions = result.get("propositions", {})
                        final_map = {k: user_map.get(k, v) for k, v in propositions.items()}

                        for k, v in final_map.items():
                            st.markdown(f"- **{k}** = {v}")

                        # Salva significados para reutilização futura
                        st.session_state["mapping"] = {**saved_map, **final_map}

                except Exception as e:
                    st.error(f"Erro inesperado: {e}")

    # ---------------------------------------------------------
    # Tabela de operadores aceitos pelo tradutor
    # ---------------------------------------------------------

    st.subheader("Sintaxe Aceita:")
    syntax_data = [
        ("E (AND)", "&", "∧"),
        ("OU (OR)", "|", "∨"),
        ("NÃO (NOT)", "~", "¬"),
        ("IMPLICA", "->", "→"),
        ("SE E SOMENTE SE", "<->", "↔")
    ]

    for name, ascii_sym, unicode_sym in syntax_data:
        st.markdown(f"### {name}")
        cols = st.columns(2)
        with cols[0]:
            st.code(ascii_sym)
        with cols[1]:
            st.code(unicode_sym)
        st.divider()

    st.markdown("- Proposições devem ser letras **MAIÚSCULAS** (P, Q, A, B)")
