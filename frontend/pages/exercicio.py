import streamlit as st
from backend.xp_system import adicionar_xp
from utils.json_utils import salvar_usuario

def mostrar_exercicio(mundo, exercicio_id, exercicio):
    if st.session_state.get(f'exercicio_{exercicio_id}_concluido', False):
        st.info("✅ Você já completou este exercício!")
        return
    
    st.subheader(f"📝 {exercicio.get('titulo', f'Exercício {exercicio_id}')}")
    st.write(exercicio['pergunta'])
    
    resposta = st.radio(
        "Escolha uma opção:",
        exercicio['opcoes'],
        index=None,
        key=f"resp_{exercicio_id}"
    )
    
    if st.button("✅ Responder", key=f"btn_{exercicio_id}"):
        if st.session_state.usuario is None:
            st.error("❌ Crie um perfil primeiro!")
            return
        
        if resposta == exercicio['opcoes'][exercicio['resposta']]:
            st.success(f"🎉 Acertou! +{exercicio['xp']} XP")
            
            # Adicionar XP ao usuário
            usuario = st.session_state.usuario
            subiu, novo_nivel = adicionar_xp(usuario, exercicio['xp'])
            
            if subiu:
                st.balloons()
                st.success(f"✨ PARABÉNS! Você subiu para o nível {novo_nivel}!")
            
            # Salvar progresso
            salvar_usuario(usuario)
            st.session_state.usuario = usuario
            
            # Marcar como concluído
            st.session_state[f'exercicio_{exercicio_id}_concluido'] = True
            st.rerun()
        else:
            st.error("❌ Errou! Tente novamente.")