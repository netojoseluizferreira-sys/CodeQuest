import streamlit as st

from backend.xp_system import progresso_para_proximo_nivel, xp_para_proximo_nivel
from frontend.navigation import ir_para_pagina
from utils.database import criar_usuario


def mostrar_perfil():
    """Renderiza a tela de criacao e visualizacao do perfil.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    st.subheader("👤 Meu Perfil")

    if st.session_state.usuario is None:
        nome = st.text_input("Digite seu nome")
        idade = st.number_input("Digite sua idade", min_value=1, max_value=120, step=1)

        if st.button("✨ Criar Perfil"):
            if nome:
                usuario = criar_usuario(nome, idade)
                st.session_state.usuario = usuario
                st.success("✅ Perfil criado com sucesso!")
                st.rerun()
    else:
        usuario = st.session_state.usuario

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏅 Nivel", usuario.nivel)
        with col2:
            st.metric("⭐ XP Total", usuario.xp)

        falta_xp = xp_para_proximo_nivel(usuario.xp)
        progresso = progresso_para_proximo_nivel(usuario.xp)

        st.progress(progresso)
        st.caption(f"📈 Faltam {falta_xp} XP para o proximo nivel!")

        st.write(f"**Nome:** {usuario.nome}")
        st.write(f"**Idade:** {usuario.idade}")

        if st.button("🔙 Voltar ao Menu"):
            ir_para_pagina("menu")
