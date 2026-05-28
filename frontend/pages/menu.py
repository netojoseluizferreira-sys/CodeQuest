import streamlit as st

from frontend.navigation import ir_para_pagina, resetar_estado_app


def mostrar_menu_principal():
    """Renderiza o menu principal da aplicacao.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👤 MEU PERFIL", use_container_width=True):
            ir_para_pagina("perfil")

    with col2:
        if st.button("🌍 MUNDOS", use_container_width=True):
            ir_para_pagina("mundos")

    with col3:
        if st.button("🏆 RANKEAMENTO", use_container_width=True):
            st.info("🏆 Ranking em breve - Pos-MVP")

    st.divider()
    if st.button("🧪 Zerar banco de dados de teste", use_container_width=True):
        resetar_estado_app()
