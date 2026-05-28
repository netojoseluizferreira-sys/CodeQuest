import streamlit as st

from backend.exercicio import carregar_aula, carregar_exercicios
from frontend.lesson_flow_state import (
    definir_fluxo_concluido,
    definir_indice_etapa_atual,
    definir_indice_exercicio_atual,
    fluxo_concluido,
    inicializar_fluxo_aula_exercicios,
    obter_indice_etapa_atual,
    obter_indice_exercicio_atual,
)
from frontend.lesson_track import obter_trilha_aula
from frontend.navigation import ir_para_pagina
from frontend.pages.exercicio import mostrar_exercicio


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
    st.caption(f"📚 Aula - etapa {obter_indice_etapa_atual(mundo, aula_id) + 1} de {total_etapas}")
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
        f"🎯 {etapa.get('titulo', 'Pratica')} - exercicio {indice_atual + 1} de {len(ids_exercicios)}"
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
