import streamlit as st

from backend.exercicio import carregar_aula, carregar_exercicios
from backend.xp_system import xp_para_proximo_nivel, progresso_para_proximo_nivel
from frontend.pages.exercicio import mostrar_exercicio
from utils.database import carregar_usuario, criar_usuario, resetar_banco_de_dados


def inicializar_estado_global():
    """Prepara os dados globais da sessao do Streamlit.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    if "usuario" not in st.session_state:
        st.session_state.usuario = carregar_usuario()
    if "pagina" not in st.session_state:
        st.session_state.pagina = "menu"
    if st.session_state.pop("db_resetado", False):
        st.success("🧪 Banco de dados zerado para testes!")


def ir_para_pagina(pagina):
    """Altera a pagina ativa e recarrega a interface.

    Recebe:
        pagina: Nome interno da pagina que deve ser exibida.

    Retorna:
        None.
    """
    st.session_state.pagina = pagina
    st.rerun()


def resetar_estado_app():
    """Apaga dados persistidos e limpa a sessao para testes.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    resetar_banco_de_dados()
    st.session_state.clear()
    st.session_state.db_resetado = True
    st.rerun()


def chave_fluxo(mundo, aula_id, sufixo):
    """Monta uma chave unica para estado de fluxo no Streamlit.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        sufixo: Parte final que identifica o dado guardado.

    Retorna:
        String usada como chave em st.session_state.
    """
    return f"fluxo_{mundo}_{aula_id}_{sufixo}"


def inicializar_fluxo_aula_exercicios(mundo, aula_id):
    """Inicializa o estado de uma trilha de aula e exercicios.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        None.
    """
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "indice_etapa"), 0)
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "indice_exercicio"), 0)
    st.session_state.setdefault(chave_fluxo(mundo, aula_id, "concluido"), False)


def obter_indice_etapa_atual(mundo, aula_id):
    """Busca o indice da etapa atual da trilha.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        Indice inteiro da etapa atual.
    """
    return st.session_state[chave_fluxo(mundo, aula_id, "indice_etapa")]


def definir_indice_etapa_atual(mundo, aula_id, indice):
    """Atualiza o indice da etapa atual da trilha.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        indice: Novo indice da etapa.

    Retorna:
        None.
    """
    st.session_state[chave_fluxo(mundo, aula_id, "indice_etapa")] = indice


def obter_indice_exercicio_atual(mundo, aula_id):
    """Busca o indice do exercicio atual dentro da etapa.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        Indice inteiro do exercicio atual.
    """
    return st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")]


def definir_indice_exercicio_atual(mundo, aula_id, indice):
    """Atualiza o indice do exercicio atual dentro da etapa.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        indice: Novo indice do exercicio.

    Retorna:
        None.
    """
    st.session_state[chave_fluxo(mundo, aula_id, "indice_exercicio")] = indice


def fluxo_concluido(mundo, aula_id):
    """Verifica se a trilha de aula foi concluida.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        True quando a trilha foi concluida; caso contrario, False.
    """
    return st.session_state[chave_fluxo(mundo, aula_id, "concluido")]


def definir_fluxo_concluido(mundo, aula_id, concluido):
    """Atualiza o status de conclusao da trilha.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        concluido: Booleano com o novo status da trilha.

    Retorna:
        None.
    """
    st.session_state[chave_fluxo(mundo, aula_id, "concluido")] = concluido


def ordenar_ids_exercicios(exercicios):
    """Ordena os IDs de exercicios em ordem natural.

    Recebe:
        exercicios: Dicionario de exercicios indexado por ID.

    Retorna:
        Lista de IDs ordenados numericamente quando possivel.
    """
    return sorted(exercicios.keys(), key=lambda item: int(item) if str(item).isdigit() else str(item))


def obter_trilha_aula(aula, exercicios):
    """Monta a sequencia de telas de aula e exercicios.

    Recebe:
        aula: Dicionario com dados da aula carregada.
        exercicios: Dicionario de exercicios disponiveis no mundo.

    Retorna:
        Lista de etapas da trilha, usando configuracao explicita ou fallback legado.
    """
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
    """Reinicia a trilha na primeira etapa.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        None.
    """
    definir_indice_etapa_atual(mundo, aula_id, 0)
    definir_indice_exercicio_atual(mundo, aula_id, 0)
    definir_fluxo_concluido(mundo, aula_id, False)
    st.rerun()


def avancar_etapa_do_fluxo(mundo, aula_id, total_etapas):
    """Avanca a trilha para a proxima etapa ou marca conclusao.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        total_etapas: Quantidade total de etapas da trilha.

    Retorna:
        None.
    """
    proxima_etapa = obter_indice_etapa_atual(mundo, aula_id) + 1
    definir_indice_exercicio_atual(mundo, aula_id, 0)

    if proxima_etapa >= total_etapas:
        definir_fluxo_concluido(mundo, aula_id, True)
    else:
        definir_indice_etapa_atual(mundo, aula_id, proxima_etapa)

    st.rerun()


def avancar_exercicio_ou_etapa(mundo, aula_id, etapa, total_etapas):
    """Avanca para o proximo exercicio ou para a proxima etapa.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        etapa: Dicionario da etapa atual de exercicios.
        total_etapas: Quantidade total de etapas da trilha.

    Retorna:
        None.
    """
    indice_exercicio = obter_indice_exercicio_atual(mundo, aula_id)
    proximo_exercicio = indice_exercicio + 1

    if proximo_exercicio >= len(etapa["exercicios"]):
        avancar_etapa_do_fluxo(mundo, aula_id, total_etapas)
    else:
        definir_indice_exercicio_atual(mundo, aula_id, proximo_exercicio)
        st.rerun()


def mostrar_tela_aula(etapa, mundo, aula_id, total_etapas):
    """Renderiza uma tela de conteudo da aula.

    Recebe:
        etapa: Dicionario com titulo e linhas de conteudo.
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        total_etapas: Quantidade total de etapas da trilha.

    Retorna:
        None.
    """
    st.caption(f"📚 Aula • etapa {obter_indice_etapa_atual(mundo, aula_id) + 1} de {total_etapas}")
    st.markdown(f"## 📚 {etapa['titulo']}")
    st.divider()

    for linha in etapa.get("conteudo", []):
        st.markdown(f"➤ {linha}")

    if st.button("➡️ Continuar", use_container_width=True):
        avancar_etapa_do_fluxo(mundo, aula_id, total_etapas)


def mostrar_tela_exercicio_atual(mundo, aula_id, etapa, exercicios, total_etapas):
    """Renderiza o exercicio atual de uma etapa pratica.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        etapa: Dicionario da etapa atual de exercicios.
        exercicios: Dicionario com todos os exercicios do mundo.
        total_etapas: Quantidade total de etapas da trilha.

    Retorna:
        None.
    """
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
    """Renderiza a tela de conclusao da trilha.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        None.
    """
    st.success("✅ Aula e exercicios concluidos!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Rever aula", use_container_width=True):
            reiniciar_fluxo_aula_exercicios(mundo, aula_id)
    with col2:
        if st.button("🌍 Voltar aos mundos", use_container_width=True):
            ir_para_pagina("mundos")


def mostrar_fluxo_aula_exercicios(mundo, aula_id, titulo):
    """Controla a trilha reutilizavel de aula e exercicios.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.
        titulo: Titulo exibido no topo do fluxo.

    Retorna:
        None.
    """
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


def renderizar_pagina_atual():
    """Renderiza a tela correspondente ao estado de navegacao atual.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
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
