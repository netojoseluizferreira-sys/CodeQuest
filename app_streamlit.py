import streamlit as st
from backend.usuario import criar_usuario, padronizar_idade
from backend.exercicio import carregar_aula
from utils.json_utils import salvar_usuario, carregar_usuario
from backend.xp_system import xp_para_proximo_nivel, progresso_para_proximo_nivel

st.set_page_config(page_title="CodeQuest", page_icon="🎮", layout="centered")

# Inicializar estado da sessão
if 'usuario' not in st.session_state:
    st.session_state.usuario = carregar_usuario()
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'menu'

st.title("🚀 CodeQuest")
st.caption("O Arquipélago de Bythos te aguarda!")

# ==================== MENU PRINCIPAL ====================
if st.session_state.pagina == 'menu':
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 MEU PERFIL", use_container_width=True):
            st.session_state.pagina = 'perfil'
            st.rerun()
    
    with col2:
        if st.button("🌍 MUNDOS", use_container_width=True):
            st.session_state.pagina = 'mundos'
            st.rerun()
    
    with col3:
        if st.button("🏆 RANKEAMENTO", use_container_width=True):
            st.info("🏆 Ranking em breve - Pós-MVP")

# ==================== PERFIL ====================
elif st.session_state.pagina == 'perfil':
    st.subheader("👤 Meu Perfil")
    
    if st.session_state.usuario is None:
        nome = st.text_input("Digite seu nome")
        idade = st.number_input("Digite sua idade", min_value=1, max_value=120, step=1)
        
        if st.button("✨ Criar Perfil"):
            if nome:
                usuario = criar_usuario(nome, idade)
                salvar_usuario(usuario)
                st.session_state.usuario = usuario
                st.success("✅ Perfil criado com sucesso!")
                st.rerun()
    else:
        usuario = st.session_state.usuario
        
        # Dados do perfil
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏅 Nível", usuario['nivel'])
        with col2:
            st.metric("⭐ XP Total", usuario['xp'])
        
        # Barra de progresso para o próximo nível
        falta_xp = xp_para_proximo_nivel(usuario['xp'])
        progresso = (usuario['xp'] % 100) / 100.0 if usuario['xp'] < 100 else 1.0
        # Versão melhorada usando a função que você pode criar:
        # progresso = progresso_para_proximo_nivel(usuario['xp'])
        
        st.progress(progresso)
        st.caption(f"📈 Faltam {falta_xp} XP para o próximo nível!")
        
        # Nome e idade
        st.write(f"**Nome:** {usuario['nome']}")
        st.write(f"**Idade:** {usuario['idade']}")
        
        if st.button("🔙 Voltar ao Menu"):
            st.session_state.pagina = 'menu'
            st.rerun()

# ==================== MUNDOS ====================
elif st.session_state.pagina == 'mundos':
    st.subheader("🌍 Mundos do CodeQuest")
    st.info("📖 Por enquanto, apenas o Mundo 1 está disponível!")
    
    if st.button("🏰 Entrar no Mundo 1"):
        st.session_state.pagina = 'mundo1'
        st.rerun()
    
    if st.button("🔙 Voltar"):
        st.session_state.pagina = 'menu'
        st.rerun()

# ==================== MUNDO 1 - AULA ====================
elif st.session_state.pagina == 'mundo1':
    st.subheader("🏰 Cabana do Oráculo - Mundo 1")
    
    aula = carregar_aula('mundo_1', 'aula_1')
    
    if aula:
        st.markdown(f"## 📚 {aula['titulo']}")
        st.divider()
        
        for linha in aula['conteudo']:
            st.markdown(f"➤ {linha}")
    
    if st.button("🔙 Voltar aos Mundos"):
        st.session_state.pagina = 'mundos'
        st.rerun()