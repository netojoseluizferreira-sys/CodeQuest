import streamlit as st

from frontend.navigation import ir_para_pagina


def mostrar_mundos():
    """Renderiza a lista de mundos disponiveis.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    st.subheader("🌍 Mundos do CodeQuest")
    st.info("📖 Por enquanto, apenas o Mundo 1 esta disponivel!")

    if st.button("🏰 Entrar no Mundo 1"):
        ir_para_pagina("mundo1")

    if st.button("🔙 Voltar"):
        ir_para_pagina("menu")
