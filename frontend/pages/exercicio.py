import re
import unicodedata

import streamlit as st

from utils.database import (
    exercicio_foi_concluido,
    marcar_exercicio_concluido as salvar_exercicio_concluido,
    obter_erros_exercicio as carregar_erros_exercicio,
    registrar_erro_exercicio as salvar_erro_exercicio,
)
from backend.xp_system import adicionar_xp


XP_BASE_PADRAO = 10
XP_MINIMO_POR_EXERCICIO = 2
PENALIDADE_XP_POR_ERRO = 2


def chave_exercicio(mundo, exercicio_id, sufixo):
    """Monta uma chave unica para estado de exercicio no Streamlit.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        sufixo: Parte final que identifica o dado guardado.

    Retorna:
        String usada como chave em st.session_state.
    """
    return f"{mundo}_exercicio_{exercicio_id}_{sufixo}"


def obter_erros_exercicio(mundo, exercicio_id):
    """Carrega a quantidade de erros do exercicio para a sessao.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        Quantidade de erros ja registrados para o exercicio.
    """
    chave = chave_exercicio(mundo, exercicio_id, "erros")
    if chave not in st.session_state:
        st.session_state[chave] = carregar_erros_exercicio(
            mundo,
            exercicio_id,
            st.session_state.get("usuario"),
        )
    return st.session_state[chave]


def registrar_erro_exercicio(mundo, exercicio_id):
    """Registra um erro no exercicio atual.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        Nova quantidade total de erros do exercicio.
    """
    chave = chave_exercicio(mundo, exercicio_id, "erros")
    st.session_state[chave] = salvar_erro_exercicio(
        mundo,
        exercicio_id,
        st.session_state.get("usuario"),
    )
    return st.session_state[chave]


def exercicio_concluido(mundo, exercicio_id):
    """Verifica se o exercicio ja foi concluido pelo usuario.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.

    Retorna:
        True quando o exercicio ja foi concluido; caso contrario, False.
    """
    chave = chave_exercicio(mundo, exercicio_id, "concluido")
    if chave not in st.session_state:
        st.session_state[chave] = exercicio_foi_concluido(
            mundo,
            exercicio_id,
            st.session_state.get("usuario"),
        )
    return st.session_state[chave]


def marcar_exercicio_concluido(mundo, exercicio_id, xp_ganho):
    """Marca o exercicio como concluido no banco e na sessao.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        xp_ganho: XP recebido pela conclusao do exercicio.

    Retorna:
        None.
    """
    salvar_exercicio_concluido(
        mundo,
        exercicio_id,
        xp_ganho,
        st.session_state.get("usuario"),
    )
    st.session_state[chave_exercicio(mundo, exercicio_id, "concluido")] = True


def calcular_xp_disponivel(exercicio, erros):
    """Calcula o XP disponivel apos penalidades por erro.

    Recebe:
        exercicio: Dicionario com dados e XP base do exercicio.
        erros: Quantidade de erros ja cometidos no exercicio.

    Retorna:
        XP que ainda pode ser recebido, respeitando o minimo configurado.
    """
    xp_base = exercicio.get("xp", XP_BASE_PADRAO)
    xp_com_penalidade = xp_base - (erros * PENALIDADE_XP_POR_ERRO)
    return max(XP_MINIMO_POR_EXERCICIO, xp_com_penalidade)


def frase_xp_disponivel(xp):
    """Seleciona a mensagem exibida para o XP disponivel.

    Recebe:
        xp: Quantidade de XP disponivel no exercicio.

    Retorna:
        Texto de feedback correspondente ao XP informado.
    """
    frases = {
        10: "🌟 Perfeito até aqui: este desafio ainda vale 10 XP!",
        8: "💪 Um tropeço só: ainda dá para garantir 8 XP.",
        6: "🧠 Ajustando a rota: agora este desafio vale 6 XP.",
        4: "🔥 Persistência conta: você ainda pode ganhar 4 XP.",
        2: "🛡️ Modo resgate: o mínimo garantido agora é 2 XP.",
    }
    return frases.get(xp, f"⭐ Este desafio vale {xp} XP agora.")


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


def normalizar_resposta_texto(texto):
    """Normaliza texto para comparacao tolerante de respostas abertas.

    Recebe:
        texto: Resposta digitada ou resposta aceita cadastrada.

    Retorna:
        Texto em minusculas, sem acentos e com separadores padronizados.
    """
    sem_acentos = unicodedata.normalize("NFD", texto.lower())
    sem_acentos = "".join(char for char in sem_acentos if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos).strip()


def resposta_correta(exercicio, resposta):
    """Valida a resposta enviada para um exercicio.

    Recebe:
        exercicio: Dicionario com tipo, opcoes e resposta esperada.
        resposta: Valor informado pelo usuario na interface.

    Retorna:
        True quando a resposta esta correta; caso contrario, False.
    """
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        resposta_normalizada = normalizar_resposta_texto(resposta or "")
        respostas_aceitas = [
            normalizar_resposta_texto(item)
            for item in exercicio.get("respostas_aceitas", [])
        ]
        return resposta_normalizada in respostas_aceitas

    return resposta == exercicio["opcoes"][exercicio["resposta"]]


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


def resposta_vazia(exercicio, resposta):
    """Verifica se a resposta atual ainda esta vazia.

    Recebe:
        exercicio: Dicionario com dados do exercicio.
        resposta: Valor atual do campo de resposta.

    Retorna:
        True quando nao ha resposta valida; caso contrario, False.
    """
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        return not resposta or not resposta.strip()

    return resposta is None


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
