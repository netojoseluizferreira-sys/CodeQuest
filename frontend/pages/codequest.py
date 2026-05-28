import streamlit as st

from backend.exercicio import carregar_aula, carregar_exercicios
from backend.usuario import criar_usuario
from backend.xp_system import xp_para_proximo_nivel, progresso_para_proximo_nivel
from frontend.pages.exercicio import mostrar_exercicio
from utils.database import carregar_usuario, resetar_banco_de_dados, salvar_usuario


def inicializar_estado_global():
    """Inicializa dados usados em todas as telas."""
    if "usuario" not in st.session_state:
        st.session_state.usuario = carregar_usuario()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "menu"
    if st.session_state.pop("db_resetado", False):
        st.success("🧪 Banco de dados zerado para testes!")


def ir_para_pagina(pagina):
    """Troca a tela atual e recarrega o app."""
    st.session_state.pagina = pagina
    st.rerun()


def resetar_estado_app():
    """Limpa dados persistidos e estado em memoria para testes."""
    resetar_banco_de_dados()
    st.session_state.clear()
    st.session_state.db_resetado = True
    st.rerun()


def chave_fluxo(mundo, aula_id, sufixo):
    """Monta chaves reaproveitaveis para fluxos de aula e exercicios."""
    return f"fluxo_{mundo}_{aula_id}_{sufixo}"


def inicializar_fluxo_aula_exercicios(mundo, aula_id):
    """Cria o estado inicial de uma trilha de aula e exercicios intercalados."""
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "indice_etapa"), 0)
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "indice_exercicio"), 0)
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "concluido"), False)


def obter_indice_etapa_atual(mundo, aula_id):
    """Retorna o indice da etapa atual da trilha."""
    return st.session_state[chave_fluxo(mundo, aula_id, "indice_etapa")]


def definir_indice_etapa_atual(mundo, aula_id, indice):
    """Atualiza o indice da etapa atual da trilha."""
    st.session_state[chave_fluxo(mundo, aula_id, "indice_etapa")] = indice


def obter_indice_exercicio_atual(mundo, aula_id):
    """Retorna o indice do exercicio atual dentro de um bloco."""
    return st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")]


def definir_indice_exercicio_atual(mundo, aula_id, indice):
    """Atualiza o indice do exercicio atual dentro de um bloco."""
    st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")] = indice


def fluxo_concluido(mundo, aula_id):
    """Verifica se a trilha foi concluida."""
    return st.session_state[chave_fluxo(mundo, aula_id, "concluido")]


def definir_fluxo_concluido(mundo, aula_id, concluido):
    """Atualiza o status de conclusao da trilha."""
    st.session_state[chave_fluxo(mundo, aula_id, "concluido")] = concluido


def ordenar_ids_exercicios(exercicios):
    """Ordena os IDs de exercicios, preservando IDs numericos em ordem natural."""
    return sorted(exercicios.keys(), key=lambda item: int(item) if str(item).isdigit() else str(item))


def obter_trilha_aula(aula, exercicios):
    """Retorna a trilha configurada ou monta uma trilha legada para aulas antigas."""
    if aula and aula.get("trilha"):
        return aula["trilha"]

    return [
        {
            "tipo": "aula",
            "id": "texto_unico",
            "titulo": aula.get("titulo", "Aula") if aula else "Aula",
            "conteudo": aula.get("conteudo", []) if aula else [],
        },
        {
            "tipo": "exercicios",
            "id": "exercicios",
            "titulo": "Exercicios",
            "exercicios": ordenar_ids_exercicios(exercicios),
        },
    ]


def reiniciar_fluxo_aula_exercicios(mundo, aula_id):
    """Volta a trilha para a primeira etapa."""
    definir_indice_etapa_atual(mundo, aula_id, 0)
    definir_indice_exercicio_atual(mundo, aula_id, 0)
    definir_fluxo_concluido(mundo, aula_id, False)
    st.rerun()


def avancar_etapa_do_fluxo(mundo, aula_id, total_etapas):
    """Avanca para a proxima etapa ou conclui a trilha."""
    proxima_etapa = obter_indice_etapa_atual(mundo, aula_id) + 1
    definir_indice_exercicio_atual(mundo, aula_id, 0)

    if proxima_etapa >= total_etapas:
        definir_fluxo_concluido(mundo, aula_id, True)
    else:
        definir_indice_etapa_atual(mundo, aula_id, proxima_etapa)

    st.rerun()


def avancar_exercicio_ou_etapa(mundo, aula_id, etapa, total_etapas):
    """Avanca dentro do bloco de exercicios ou passa para a proxima etapa."""
    indice_exercicio = obter_indice_exercicio_atual(mundo, aula_id)
    proximo_exercicio = indice_exercicio + 1

    if proximo_exercicio >= len(etapa["exercicios"]):
        avancar_etapa_do_fluxo(mundo, aula_id, total_etapas)
    else:
        definir_indice_exercicio_atual(mundo, aula_id, proximo_exercicio)
        st.rerun()


def mostrar_tela_aula(etapa, mundo, aula_id, total_etapas):
    """Renderiza uma pagina de texto da aula."""
    st.caption(f"📚 Aula • etapa {obter_indice_etapa_atual(mundo, aula_id) + 1} de {total_etapas}")
    st.markdown(f"## 📚 {etapa['titulo']}")
    st.divider()

    for linha in etapa.get("conteudo", []):
        st.markdown(f"➤ {linha}")

    if st.button("➡️ Continuar", use_container_width=True):
        avancar_etapa_do_fluxo(mundo, aula_id, total_etapas)


def mostrar_tela_exercicio_atual(mundo, aula_id, etapa, exercicios, total_etapas):
    """Renderiza um exercicio por tela dentro do bloco atual."""
    ids_exercicios = etapa.get("exercicios", [])

    if not ids_exercicios:
        st.info("📝 Exercicios em breve!")
        return

    indice_atual = min(obter_indice_exercicio_atual(mundo, aula_id), len(ids_exercicios) - 1)
    definir_indice_exercicio_atual(mundo, aula_id, indice_atual)

    exercicio_id = ids_exercicios[indice_atual]
    exercicio = exercicios.get(exercicio_id)

    if exercicio is None:
        st.error(f"❌ Exercicio {exercicio_id} nao encontrado.")
        return

    st.caption(
        f"🎯 {etapa.get('titulo', 'Pratica')} • exercicio {indice_atual + 1} de {len(ids_exercicios)}"
    )
    resultado = mostrar_exercicio(mundo, exercicio_id, exercicio)

    if resultado in {"acertou", "concluido"}:
        ultimo_exercicio = indice_atual == len(ids_exercicios) - 1
        texto_botao = "➡️ Continuar aula" if ultimo_exercicio else "➡️ Proximo exercicio"
        if st.button(texto_botao, use_container_width=True):
            avancar_exercicio_ou_etapa(mundo, aula_id, etapa, total_etapas)


def mostrar_tela_fluxo_concluido(mundo, aula_id):
    """Renderiza a tela final da trilha."""
    st.success("✅ Aula e exercicios concluidos!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Rever aula", use_container_width=True):
            reiniciar_fluxo_aula_exercicios(mundo, aula_id)
    with col2:
        if st.button("🌍 Voltar aos mundos", use_container_width=True):
            ir_para_pagina("mundos")


def mostrar_fluxo_aula_exercicios(mundo, aula_id, titulo):
    """Controla uma trilha reutilizavel de textos e exercicios intercalados."""
    inicializar_fluxo_aula_exercicios(mundo, aula_id)

    st.subheader(titulo)

    aula = carregar_aula(mundo, aula_id)
    exercicios = carregar_exercicios(mundo)
    trilha = obter_trilha_aula(aula, exercicios)

    if not aula:
        st.info("📚 Aula nao encontrada.")
    elif fluxo_concluido(mundo, aula_id):
        mostrar_tela_fluxo_concluido(mundo, aula_id)
    else:
        indice_etapa = min(obter_indice_etapa_atual(mundo, aula_id), len(trilha) - 1)
        definir_indice_etapa_atual(mundo, aula_id, indice_etapa)
        etapa = trilha[indice_etapa]

        if etapa["tipo"] == "aula":
            mostrar_tela_aula(etapa, mundo, aula_id, len(trilha))
        elif etapa["tipo"] == "exercicios":
            mostrar_tela_exercicio_atual(mundo, aula_id, etapa, exercicios, len(trilha))
        else:
            st.error(f"❌ Tipo de etapa desconhecido: {etapa['tipo']}")

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

    st.divider()
    if st.button("🧪 Zerar banco de dados de teste", use_container_width=True):
        resetar_estado_app()


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
