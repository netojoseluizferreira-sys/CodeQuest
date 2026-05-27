import re
import unicodedata

import streamlit as st

from backend.xp_system import adicionar_xp
from utils.json_utils import salvar_usuario


MAX_TENTATIVAS_COM_XP = 3


def chave_exercicio(mundo, exercicio_id, sufixo):
    """Monta uma chave unica para controles de estado do exercicio."""
    return f"{mundo}_exercicio_{exercicio_id}_{sufixo}"


def obter_tentativas_exercicio(mundo, exercicio_id):
    """Retorna quantas respostas ja foram enviadas neste exercicio."""
    return st.session_state.get(chave_exercicio(mundo, exercicio_id, "tentativas"), 0)


def registrar_tentativa_exercicio(mundo, exercicio_id):
    """Incrementa e retorna o total de tentativas do exercicio."""
    chave = chave_exercicio(mundo, exercicio_id, "tentativas")
    st.session_state[chave] = st.session_state.get(chave, 0) + 1
    return st.session_state[chave]


def exercicio_concluido(mundo, exercicio_id):
    """Verifica se o exercicio ja foi acertado."""
    return st.session_state.get(chave_exercicio(mundo, exercicio_id, "concluido"), False)


def marcar_exercicio_concluido(mundo, exercicio_id):
    """Marca um exercicio como concluido no estado da sessao."""
    st.session_state[chave_exercicio(mundo, exercicio_id, "concluido")] = True


def tentativa_vale_xp(tentativa, limite_tentativas=MAX_TENTATIVAS_COM_XP):
    """Define se a tentativa ainda permite ganhar XP."""
    return tentativa <= limite_tentativas


def premiar_usuario_com_xp(exercicio):
    """Adiciona o XP do exercicio ao usuario e persiste os dados."""
    usuario = st.session_state.usuario
    subiu, novo_nivel = adicionar_xp(usuario, exercicio["xp"])

    salvar_usuario(usuario)
    st.session_state.usuario = usuario

    return subiu, novo_nivel


def normalizar_resposta_texto(texto):
    """Normaliza texto para comparar respostas abertas com mais tolerancia."""
    sem_acentos = unicodedata.normalize("NFD", texto.lower())
    sem_acentos = "".join(char for char in sem_acentos if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos).strip()


def resposta_correta(exercicio, resposta):
    """Valida respostas de multipla escolha e de completar."""
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        resposta_normalizada = normalizar_resposta_texto(resposta or "")
        respostas_aceitas = [
            normalizar_resposta_texto(item)
            for item in exercicio.get("respostas_aceitas", [])
        ]
        return resposta_normalizada in respostas_aceitas

    return resposta == exercicio["opcoes"][exercicio["resposta"]]


def mostrar_status_tentativas(mundo, exercicio_id, limite_tentativas=MAX_TENTATIVAS_COM_XP):
    """Mostra o status de tentativas e se o XP ainda esta disponivel."""
    tentativas = obter_tentativas_exercicio(mundo, exercicio_id)
    restantes = max(limite_tentativas - tentativas, 0)

    if restantes > 0:
        st.caption(f"⭐ Tentativas com XP restantes: {restantes}/{limite_tentativas}")
    else:
        st.warning("⚠️ Voce ainda pode continuar tentando, mas este exercicio nao dara mais XP.")


def mostrar_campo_resposta(mundo, exercicio_id, exercicio):
    """Renderiza o controle correto para o tipo de exercicio."""
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


def resposta_vazia(exercicio, resposta):
    """Verifica se o usuario ainda nao respondeu."""
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        return not resposta or not resposta.strip()

    return resposta is None


def mostrar_exercicio(mundo, exercicio_id, exercicio, limite_tentativas=MAX_TENTATIVAS_COM_XP):
    """Renderiza um exercicio e retorna 'acertou', 'errou', 'concluido' ou None."""
    if exercicio_concluido(mundo, exercicio_id):
        st.info("✅ Voce ja completou este exercicio!")
        return "concluido"

    mostrar_status_tentativas(mundo, exercicio_id, limite_tentativas)

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

        tentativa_atual = registrar_tentativa_exercicio(mundo, exercicio_id)
        pode_ganhar_xp = tentativa_vale_xp(tentativa_atual, limite_tentativas)

        if resposta_correta(exercicio, resposta):
            if pode_ganhar_xp:
                st.success(f"🎉 Acertou! +{exercicio['xp']} XP")

                subiu, novo_nivel = premiar_usuario_com_xp(exercicio)

                if subiu:
                    st.balloons()
                    st.success(f"✨ Parabens! Voce subiu para o nivel {novo_nivel}!")
            else:
                st.success("🎉 Acertou! Como o limite de tentativas com XP acabou, nenhum XP foi adicionado.")

            marcar_exercicio_concluido(mundo, exercicio_id)
            return "acertou"

        st.error("❌ Errou! Tente novamente.")
        return "errou"

    return None
