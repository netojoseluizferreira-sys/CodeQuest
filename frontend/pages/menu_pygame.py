import streamlit as st

from frontend.runtime_services import (
    api_esta_disponivel,
    iniciar_api_local,
    iniciar_menu_pygame,
    obter_status_api,
)


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
        status_api = obter_status_api()
        with st.expander("Diagnostico da API local"):
            st.write(f"URL: `{status_api['url']}`")
            st.write(f"Python: `{status_api['python_runtime']}`")
            st.write(f"Runtimes candidatos: `{status_api['runtimes']}`")
            st.write(f"Processo ativo: `{status_api['processo_ativo']}`")
            st.write(f"Thread interna ativa: `{status_api['thread_ativa']}`")
            st.write(f"Codigo de saida: `{status_api['codigo_saida']}`")
            if status_api["log"]:
                st.code(status_api["log"], language="text")
            else:
                st.caption("Nenhum log de inicializacao foi registrado ainda.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎮 Abrir menu Pygame", use_container_width=True):
            iniciar_menu_pygame()
            st.rerun()
    with col2:
        if st.button("Tentar API", use_container_width=True):
            iniciar_api_local()
            st.rerun()
    with col3:
        if st.button("🔄 Verificar escolha", use_container_width=True):
            st.rerun()
