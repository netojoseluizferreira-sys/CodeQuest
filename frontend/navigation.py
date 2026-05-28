import streamlit as st

from utils.database import carregar_usuario, resetar_banco_de_dados


def inicializar_estado_global():
    """Prepara os dados globais da sessao do Streamlit.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    if "usuario" not in st.session_state:
        st.session_state.usuario = carregar_usuario()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "menu"
    if st.session_state.pop("db_resetado", False):
        st.success("🧪 Banco de dados zerado para testes!")


def ir_para_pagina(pagina):
    """Altera a pagina ativa e recarrega a interface.

    Recebe:
        pagina: Nome interno da pagina que deve ser exibida.

    Retorna:
        None.
    """
    st.session_state.pagina = pagina
    st.rerun()


def resetar_estado_app():
    """Apaga dados persistidos e limpa a sessao para testes.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    resetar_banco_de_dados()
    st.session_state.clear()
    st.session_state.db_resetado = True
    st.rerun()
