import re
import unicodedata

import streamlit as st

from backend.xp_system import adicionar_xp
from utils.json_utils import salvar_usuario


XP_BASE_PADRAO = 10
XP_MINIMO_POR_EXERCICIO = 2
PENALIDADE_XP_POR_ERRO = 2


def chave_exercicio(mundo, exercicio_id, sufixo):
    """Monta uma chave unica para controles de estado do exercicio."""
    return f"{mundo}_exercicio_{exercicio_id}_{sufixo}"


def obter_erros_exercicio(mundo, exercicio_id):
    """Retorna quantas respostas erradas ja foram enviadas neste exercicio."""
    return st.session_state.get(chave_exercicio(mundo, exercicio_id, "erros"), 0)


def registrar_erro_exercicio(mundo, exercicio_id):
    """Incrementa e retorna o total de erros do exercicio."""
    chave = chave_exercicio(mundo, exercicio_id, "erros")
    st.session_state[chave] = st.session_state.get(chave, 0) + 1
    return st.session_state[chave]


def exercicio_concluido(mundo, exercicio_id):
    """Verifica se o exercicio ja foi acertado."""
    return st.session_state.get(chave_exercicio(mundo, exercicio_id, "concluido"), False)


def marcar_exercicio_concluido(mundo, exercicio_id):
    """Marca um exercicio como concluido no estado da sessao."""
    st.session_state[chave_exercicio(mundo, exercicio_id, "concluido")] = True


def calcular_xp_disponivel(exercicio, erros):
    """Calcula o XP atual do exercicio com penalidade por erro e piso minimo."""
    xp_base = exercicio.get("xp", XP_BASE_PADRAO)
    xp_com_penalidade = xp_base - (erros * PENALIDADE_XP_POR_ERRO)
    return max(XP_MINIMO_POR_EXERCICIO, xp_com_penalidade)


def frase_xp_disponivel(xp):
    """Retorna uma frase diferente para cada faixa de XP disponivel."""
    frases = {
        10: "🌟 Perfeito até aqui: este desafio ainda vale 10 XP!",
        8: "💪 Um tropeço só: ainda dá para garantir 8 XP.",
        6: "🧠 Ajustando a rota: agora este desafio vale 6 XP.",
        4: "🔥 Persistência conta: você ainda pode ganhar 4 XP.",
        2: "🛡️ Modo resgate: o mínimo garantido agora é 2 XP.",
    }
    return frases.get(xp, f"⭐ Este desafio vale {xp} XP agora.")


def premiar_usuario_com_xp(quantidade_xp):
    """Adiciona o XP do exercicio ao usuario e persiste os dados."""
    usuario = st.session_state.usuario
    subiu, novo_nivel = adicionar_xp(usuario, quantidade_xp)

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


def mostrar_status_xp(mundo, exercicio_id, exercicio):
    """Mostra o XP atual do exercicio conforme os erros acumulados."""
    erros = obter_erros_exercicio(mundo, exercicio_id)
    xp_disponivel = calcular_xp_disponivel(exercicio, erros)

    st.caption(frase_xp_disponivel(xp_disponivel))
    if erros > 0:
        st.caption(f"Erros neste exercicio: {erros}")


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


def mostrar_exercicio(mundo, exercicio_id, exercicio):
    """Renderiza um exercicio e retorna 'acertou', 'errou', 'concluido' ou None."""
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

            marcar_exercicio_concluido(mundo, exercicio_id)
            return "acertou"

        erros = registrar_erro_exercicio(mundo, exercicio_id)
        proximo_xp = calcular_xp_disponivel(exercicio, erros)
        st.error(f"❌ Errou! Tente novamente. {frase_xp_disponivel(proximo_xp)}")
        return "errou"

    return None
