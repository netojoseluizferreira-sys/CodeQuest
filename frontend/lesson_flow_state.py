import streamlit as st


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
