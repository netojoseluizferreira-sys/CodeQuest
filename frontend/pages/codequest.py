from frontend.lesson_flow import mostrar_fluxo_aula_exercicios
from frontend.navigation import inicializar_estado_global
from frontend.pages.menu import mostrar_menu_principal
from frontend.pages.menu_pygame import mostrar_espera_menu_pygame
from frontend.pages.mundos import mostrar_mundos
from frontend.pages.perfil import mostrar_perfil


def renderizar_pagina_atual():
    """Renderiza a tela correspondente ao estado de navegacao atual.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    import streamlit as st

    if st.session_state.pagina == "menu_pygame":
        mostrar_espera_menu_pygame()
    elif st.session_state.pagina == "menu":
        mostrar_menu_principal()
    elif st.session_state.pagina == "perfil":
        mostrar_perfil()
    elif st.session_state.pagina == "mundos":
        mostrar_mundos()
    elif st.session_state.pagina == "mundo1":
        mostrar_fluxo_aula_exercicios(
            mundo="mundo_1",
            aula_id="aula_1",
            titulo="🏰 Cabana do Oraculo - Mundo 1",
        )
