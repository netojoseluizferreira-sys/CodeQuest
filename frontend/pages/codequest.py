import streamlit as st

from backend.exercicio import carregar_aula, carregar_exercicios
from backend.usuario import criar_usuario
from backend.xp_system import xp_para_proximo_nivel, progresso_para_proximo_nivel
from frontend.pages.exercicio import mostrar_exercicio
from utils.json_utils import carregar_usuario, salvar_usuario


def inicializar_estado_global():
    """Inicializa dados usados em todas as telas."""
    if "usuario" not in st.session_state:
        st.session_state.usuario = carregar_usuario()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "menu"


def ir_para_pagina(pagina):
    """Troca a tela atual e recarrega o app."""
    st.session_state.pagina = pagina
    st.rerun()


def chave_fluxo(mundo, aula_id, sufixo):
    """Monta chaves reaproveitaveis para fluxos de aula e exercicios."""
    return f"fluxo_{mundo}_{aula_id}_{sufixo}"


def inicializar_fluxo_aula_exercicios(mundo, aula_id):
    """Cria o estado inicial de um fluxo aula -> exercicios em sequencia."""
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "etapa"), "aula")
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "indice_exercicio"), 0)


def obter_etapa_fluxo(mundo, aula_id):
    """Retorna a etapa atual do fluxo."""
    return st.session_state[chave_fluxo(mundo, aula_id, "etapa")]


def definir_etapa_fluxo(mundo, aula_id, etapa):
    """Atualiza a etapa atual do fluxo."""
    st.session_state[chave_fluxo(mundo, aula_id, "etapa")] = etapa


def obter_indice_exercicio_atual(mundo, aula_id):
    """Retorna o indice do exercicio atual dentro do fluxo."""
    return st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")]


def definir_indice_exercicio_atual(mundo, aula_id, indice):
    """Atualiza o indice do exercicio atual dentro do fluxo."""
    st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")] = indice


def ordenar_ids_exercicios(exercicios):
    """Ordena os IDs de exercicios, preservando IDs numericos em ordem natural."""
    return sorted(exercicios.keys(), key=lambda item: int(item) if str(item).isdigit() else str(item))


def reiniciar_fluxo_aula_exercicios(mundo, aula_id):
    """Volta o fluxo para a aula inicial."""
    definir_etapa_fluxo(mundo, aula_id, "aula")
    definir_indice_exercicio_atual(mundo, aula_id, 0)
    st.rerun()


def iniciar_exercicios_do_fluxo(mundo, aula_id):
    """Move o fluxo da aula para o primeiro exercicio."""
    definir_etapa_fluxo(mundo, aula_id, "exercicios")
    definir_indice_exercicio_atual(mundo, aula_id, 0)
    st.rerun()


def avancar_exercicio_do_fluxo(mundo, aula_id, total_exercicios):
    """Avanca para o proximo exercicio ou encerra o fluxo."""
    proximo_indice = obter_indice_exercicio_atual(mundo, aula_id) + 1

    if proximo_indice >= total_exercicios:
        definir_etapa_fluxo(mundo, aula_id, "concluido")
    else:
        definir_indice_exercicio_atual(mundo, aula_id, proximo_indice)

    st.rerun()


def mostrar_tela_aula(aula, mundo, aula_id):
    """Renderiza a tela de aula do fluxo."""
    if not aula:
        st.info("📚 Aula nao encontrada.")
        return

    st.markdown(f"## 📚 {aula['titulo']}")
    st.divider()

    for linha in aula["conteudo"]:
        st.markdown(f"➤ {linha}")

    if st.button("📝 Ir para os exercicios", use_container_width=True):
        iniciar_exercicios_do_fluxo(mundo, aula_id)


def mostrar_tela_exercicio_atual(mundo, aula_id, exercicios):
    """Renderiza somente um exercicio por tela, seguindo a ordem configurada."""
    if not exercicios:
        st.info("📝 Exercicios em breve!")
        return

    ids_exercicios = ordenar_ids_exercicios(exercicios)
    indice_atual = min(obter_indice_exercicio_atual(mundo, aula_id), len(ids_exercicios) - 1)
    definir_indice_exercicio_atual(mundo, aula_id, indice_atual)
    exercicio_id = ids_exercicios[indice_atual]
    exercicio = exercicios[exercicio_id]

    st.caption(f"🎯 Exercicio {indice_atual + 1} de {len(ids_exercicios)}")
    resultado = mostrar_exercicio(mundo, exercicio_id, exercicio)

    if resultado in {"acertou", "concluido"}:
        texto_botao = "🏁 Finalizar aula" if indice_atual == len(ids_exercicios) - 1 else "➡️ Proximo exercicio"
        if st.button(texto_botao, use_container_width=True):
            avancar_exercicio_do_fluxo(mundo, aula_id, len(ids_exercicios))


def mostrar_tela_fluxo_concluido(mundo, aula_id):
    """Renderiza a tela final do fluxo."""
    st.success("✅ Aula e exercicios concluidos!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Rever aula", use_container_width=True):
            reiniciar_fluxo_aula_exercicios(mundo, aula_id)
    with col2:
        if st.button("🌍 Voltar aos mundos", use_container_width=True):
            ir_para_pagina("mundos")


def mostrar_fluxo_aula_exercicios(mundo, aula_id, titulo):
    """Controla um fluxo reutilizavel de aula seguida por exercicios sequenciais."""
    inicializar_fluxo_aula_exercicios(mundo, aula_id)

    st.subheader(titulo)

    etapa = obter_etapa_fluxo(mundo, aula_id)
    aula = carregar_aula(mundo, aula_id)
    exercicios = carregar_exercicios(mundo)

    if etapa == "aula":
        mostrar_tela_aula(aula, mundo, aula_id)
    elif etapa == "exercicios":
        mostrar_tela_exercicio_atual(mundo, aula_id, exercicios)
    else:
        mostrar_tela_fluxo_concluido(mundo, aula_id)

    if st.button("🔙 Voltar aos Mundos"):
        ir_para_pagina("mundos")


def mostrar_menu_principal():
    """Renderiza o menu principal."""
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


def mostrar_perfil():
    """Renderiza criacao e dados do perfil."""
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

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏅 Nivel", usuario["nivel"])
        with col2:
            st.metric("⭐ XP Total", usuario["xp"])

        falta_xp = xp_para_proximo_nivel(usuario["xp"])
        progresso = progresso_para_proximo_nivel(usuario["xp"])

        st.progress(progresso)
        st.caption(f"📈 Faltam {falta_xp} XP para o proximo nivel!")

        st.write(f"**Nome:** {usuario['nome']}")
        st.write(f"**Idade:** {usuario['idade']}")

        if st.button("🔙 Voltar ao Menu"):
            ir_para_pagina("menu")


def mostrar_mundos():
    """Renderiza a lista de mundos disponiveis."""
    st.subheader("🌍 Mundos do CodeQuest")
    st.info("📖 Por enquanto, apenas o Mundo 1 esta disponivel!")

    if st.button("🏰 Entrar no Mundo 1"):
        ir_para_pagina("mundo1")

    if st.button("🔙 Voltar"):
        ir_para_pagina("menu")


def renderizar_pagina_atual():
    """Roteia a pagina ativa para sua tela."""
    if st.session_state.pagina == "menu":
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
