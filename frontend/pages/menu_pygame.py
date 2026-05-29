import streamlit as st

from frontend.runtime_services import api_esta_disponivel, iniciar_menu_pygame


def mostrar_espera_menu_pygame():
    """Renderiza a tela de espera enquanto o menu Pygame controla o fluxo.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    st.subheader("🎮 Menu do CodeQuest")

    if api_esta_disponivel():
        st.success("API local conectada.")
        st.info("Use a janela do Pygame para escolher Novo jogo, Continuar ou Creditos.")
    else:
        st.error("API local ainda nao esta disponivel. Recarregue a pagina em alguns segundos.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎮 Abrir menu Pygame", use_container_width=True):
            iniciar_menu_pygame()
            st.rerun()
    with col2:
        if st.button("🔄 Verificar escolha", use_container_width=True):
            st.rerun()
