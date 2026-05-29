import streamlit as st

from utils.database import carregar_usuario, resetar_banco_de_dados
from frontend.runtime_services import (
    iniciar_api_local,
    iniciar_menu_pygame,
    limpar_estado_menu,
    obter_estado_menu,
)


def inicializar_estado_global():
    """Prepara os dados globais da sessao do Streamlit.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    api_online = iniciar_api_local()

    if "usuario" not in st.session_state:
        st.session_state.usuario = carregar_usuario()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "menu_pygame"
    if "pygame_menu_iniciado" not in st.session_state and api_online:
        st.session_state.pygame_menu_iniciado = iniciar_menu_pygame()

    aplicar_acao_pendente_do_menu()

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


def voltar_para_menu_pygame():
    """Retorna o fluxo do Streamlit para a tela de espera do menu Pygame.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    limpar_estado_menu()
    iniciar_menu_pygame()
    st.session_state.pagina = "menu_pygame"
    st.rerun()


def aplicar_acao_pendente_do_menu():
    """Aplica no Streamlit a proxima pagina solicitada pelo menu Pygame.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    estado = obter_estado_menu()
    if not estado or not estado.get("next_page"):
        return

    proxima_pagina = estado["next_page"]
    if proxima_pagina == "mundos":
        st.session_state.usuario = carregar_usuario()
    elif proxima_pagina == "perfil":
        st.session_state.usuario = carregar_usuario()

    limpar_estado_menu()
    st.session_state.pagina = proxima_pagina
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
