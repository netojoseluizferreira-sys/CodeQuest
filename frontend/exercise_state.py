import streamlit as st

from utils.database import (
    exercicio_foi_concluido,
    marcar_exercicio_concluido as salvar_exercicio_concluido,
    obter_erros_exercicio as carregar_erros_exercicio,
    registrar_erro_exercicio as salvar_erro_exercicio,
)


def chave_exercicio(mundo, exercicio_id, sufixo):
    """Monta uma chave unica para estado de exercicio no Streamlit.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        sufixo: Parte final que identifica o dado guardado.

    Retorna:
        String usada como chave em st.session_state.
    """
    return f"{mundo}_exercicio_{exercicio_id}_{sufixo}"


def obter_erros_exercicio(mundo, exercicio_id):
    """Carrega a quantidade de erros do exercicio para a sessao.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        Quantidade de erros ja registrados para o exercicio.
    """
    chave = chave_exercicio(mundo, exercicio_id, "erros")
    if chave not in st.session_state:
        st.session_state[chave] = carregar_erros_exercicio(
            mundo,
            exercicio_id,
            st.session_state.get("usuario"),
        )
    return st.session_state[chave]


def registrar_erro_exercicio(mundo, exercicio_id):
    """Registra um erro no exercicio atual.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        Nova quantidade total de erros do exercicio.
    """
    chave = chave_exercicio(mundo, exercicio_id, "erros")
    st.session_state[chave] = salvar_erro_exercicio(
        mundo,
        exercicio_id,
        st.session_state.get("usuario"),
    )
    return st.session_state[chave]


def exercicio_concluido(mundo, exercicio_id):
    """Verifica se o exercicio ja foi concluido pelo usuario.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        True quando o exercicio ja foi concluido; caso contrario, False.
    """
    chave = chave_exercicio(mundo, exercicio_id, "concluido")
    if chave not in st.session_state:
        st.session_state[chave] = exercicio_foi_concluido(
            mundo,
            exercicio_id,
            st.session_state.get("usuario"),
        )
    return st.session_state[chave]


def marcar_exercicio_concluido(mundo, exercicio_id, xp_ganho):
    """Marca o exercicio como concluido no banco e na sessao.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        xp_ganho: XP recebido pela conclusao do exercicio.

    Retorna:
        None.
    """
    salvar_exercicio_concluido(
        mundo,
        exercicio_id,
        xp_ganho,
        st.session_state.get("usuario"),
    )
    st.session_state[chave_exercicio(mundo, exercicio_id, "concluido")] = True
