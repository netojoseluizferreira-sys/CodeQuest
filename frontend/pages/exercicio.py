import streamlit as st

from backend.xp_system import adicionar_xp
from frontend.exercise_state import (
    exercicio_concluido,
    marcar_exercicio_concluido,
    obter_erros_exercicio,
    registrar_erro_exercicio,
)
from frontend.exercise_validation import resposta_correta, resposta_vazia
from frontend.exercise_xp import calcular_xp_disponivel, frase_xp_disponivel


def premiar_usuario_com_xp(quantidade_xp):
    """Concede XP ao usuario atual da sessao.

    Recebe:
        quantidade_xp: Quantidade de XP a ser adicionada ao usuario.

    Retorna:
        Uma tupla com um booleano indicando subida de nivel e o novo nivel.
    """
    usuario = st.session_state.usuario
    subiu, novo_nivel = adicionar_xp(usuario, quantidade_xp)

    st.session_state.usuario = usuario

    return subiu, novo_nivel


def mostrar_status_xp(mundo, exercicio_id, exercicio):
    """Exibe o XP disponivel e o total de erros do exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        exercicio: Dicionario com dados do exercicio.

    Retorna:
        None.
    """
    erros = obter_erros_exercicio(mundo, exercicio_id)
    xp_disponivel = calcular_xp_disponivel(exercicio, erros)

    st.caption(frase_xp_disponivel(xp_disponivel))
    if erros > 0:
        st.caption(f"Erros neste exercicio: {erros}")


def mostrar_campo_resposta(mundo, exercicio_id, exercicio):
    """Renderiza o campo de resposta adequado ao tipo do exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        exercicio: Dicionario com dados do exercicio.

    Retorna:
        Valor informado pelo usuario no campo renderizado.
    """
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        return st.text_input(
            "Complete a resposta:",
            placeholder=exercicio.get("placeholder", "Digite sua resposta"),
            key=f"resp_{mundo}_{exercicio_id}",
        )

    return st.radio(
        "Escolha uma opcao:",
        exercicio["opcoes"],
        index=None,
        key=f"resp_{mundo}_{exercicio_id}",
    )


def mostrar_exercicio(mundo, exercicio_id, exercicio):
    """Renderiza um exercicio completo e processa sua resposta.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        exercicio: Dicionario com pergunta, opcoes e resposta esperada.

    Retorna:
        'acertou', 'errou', 'concluido' ou None conforme a interacao atual.
    """
    if exercicio_concluido(mundo, exercicio_id):
        st.info("✅ Voce ja completou este exercicio!")
        return "concluido"

    mostrar_status_xp(mundo, exercicio_id, exercicio)

    st.subheader(f"📝 {exercicio.get('titulo', f'Exercicio {exercicio_id}')}")
    st.write(exercicio["pergunta"])

    resposta = mostrar_campo_resposta(mundo, exercicio_id, exercicio)

    if st.button("✅ Responder", key=f"btn_{mundo}_{exercicio_id}"):
        if st.session_state.usuario is None:
            st.error("❌ Crie um perfil primeiro!")
            return None

        if resposta_vazia(exercicio, resposta):
            st.warning("⚠️ Responda antes de continuar.")
            return None

        erros_atuais = obter_erros_exercicio(mundo, exercicio_id)
        xp_disponivel = calcular_xp_disponivel(exercicio, erros_atuais)

        if resposta_correta(exercicio, resposta):
            st.success(f"🎉 Acertou! {frase_xp_disponivel(xp_disponivel)} +{xp_disponivel} XP")

            subiu, novo_nivel = premiar_usuario_com_xp(xp_disponivel)

            if subiu:
                st.balloons()
                st.success(f"✨ Parabens! Voce subiu para o nivel {novo_nivel}!")

            marcar_exercicio_concluido(mundo, exercicio_id, xp_disponivel)
            return "acertou"

        erros = registrar_erro_exercicio(mundo, exercicio_id)
        proximo_xp = calcular_xp_disponivel(exercicio, erros)
        st.error(f"❌ Errou! Tente novamente. {frase_xp_disponivel(proximo_xp)}")
        return "errou"

    return None
