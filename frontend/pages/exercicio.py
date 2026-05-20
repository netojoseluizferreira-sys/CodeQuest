# frontend/pages/exercicio.py
import streamlit as st
from backend.exercicio import carregar_exercicios
from backend.xp_system import adicionar_xp
from utils.json_utils import salvar_usuario

def mostrar_exercicio(mundo, exercicio_id, exercicio):
    st.subheader(f"📝 Exercício {exercicio_id}")
    st.write(exercicio['pergunta'])
    
    resposta = st.radio(
        "Escolha uma opção:",
        exercicio['opcoes'],
        index=None
    )
    
    if st.button("✅ Responder"):
        if resposta == exercicio['opcoes'][exercicio['resposta']]:
            st.success("🎉 Acertou! +{} XP".format(exercicio['xp']))
            
            # Adicionar XP ao usuário
            usuario = st.session_state.usuario
            subiu, novo_nivel = adicionar_xp(usuario, exercicio['xp'])
            
            if subiu:
                st.balloons()
                st.success(f"✨ PARABÉNS! Você subiu para o nível {novo_nivel}!")
            
            # Salvar progresso
            salvar_usuario(usuario)
            st.session_state.usuario = usuario
            
            # Marcar como concluído (opcional)
            st.session_state[f'exercicio_{exercicio_id}_concluido'] = True
        else:
            st.error("❌ Errou! Tente novamente.")