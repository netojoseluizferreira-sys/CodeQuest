"""Regras de desbloqueio de conquistas do CodeQuest."""

import unicodedata

from backend.exercicio import carregar_exercicios
from backend.worlds import exercicios_obrigatorios, listar_mundos, mundo_implementado
from utils.achievement_repository import desbloquear_conquista, obter_conquista
from utils.database_connection import conectar, inicializar_banco
from utils.user_repository import obter_usuario_id


MELHOR_PROFESSOR_UFAL = "melhor_professor_ufal"
FENOMENO = "fenomeno"
QUASE_HEXA = "quase_hexa"
XP_BASE_EXERCICIO = 10
XP_MINIMO_EXERCICIO = 2

VARIACOES_ALEXANDRE_BARBOSA = {
    "barbosa",
    "alexandre",
    "alexandre barbosa",
    "prof barbosa",
    "professor barbosa",
    "prof alexandre",
    "professor alexandre",
}


def normalizar_texto(texto):
    """Normaliza texto livre para regras de conquista."""
    texto = unicodedata.normalize("NFD", str(texto).strip().lower())
    texto = "".join(char for char in texto if unicodedata.category(char) != "Mn")
    return " ".join(texto.split())


def nome_desbloqueia_melhor_professor(nome):
    """Retorna True para variacoes aceitas de Alexandre Barbosa."""
    return normalizar_texto(nome) in VARIACOES_ALEXANDRE_BARBOSA


def avaliar_nome_usuario(usuario):
    """Avalia conquistas baseadas no nome do usuario recem-criado."""
    if usuario is None or not nome_desbloqueia_melhor_professor(usuario.nome):
        return []
    return _desbloquear_e_descrever(usuario, MELHOR_PROFESSOR_UFAL)


def avaliar_progresso_usuario(usuario):
    """Avalia conquistas dependentes de XP e conclusao do conteudo disponivel."""
    if usuario is None:
        return []

    desbloqueadas = []
    maximo = xp_maximo_disponivel()
    if maximo > 0 and usuario.xp >= maximo:
        desbloqueadas.extend(_desbloquear_e_descrever(usuario, FENOMENO))

    if conteudo_disponivel_concluido_com_xp_minimo(usuario):
        desbloqueadas.extend(_desbloquear_e_descrever(usuario, QUASE_HEXA))

    return desbloqueadas


def avaliar_todas_conquistas(usuario):
    """Avalia todas as regras conhecidas para o usuario."""
    return avaliar_nome_usuario(usuario) + avaliar_progresso_usuario(usuario)


def xp_maximo_disponivel():
    """Calcula o XP maximo dos exercicios obrigatorios dos mundos implementados."""
    total = 0
    for mundo in _mundos_implementados():
        exercicios = carregar_exercicios(mundo["id"])
        for exercicio_id in exercicios_obrigatorios(mundo["id"]):
            exercicio = exercicios.get(str(exercicio_id), {})
            total += int(exercicio.get("xp", XP_BASE_EXERCICIO))
    return total


def xp_minimo_disponivel():
    """Calcula o XP minimo para concluir o conteudo disponivel."""
    return len(_exercicios_obrigatorios_disponiveis()) * XP_MINIMO_EXERCICIO


def conteudo_disponivel_concluido_com_xp_minimo(usuario):
    """Verifica se todos os exercicios disponiveis foram concluidos com XP minimo."""
    obrigatorios = _exercicios_obrigatorios_disponiveis()
    if not obrigatorios:
        return False

    usuario_id = obter_usuario_id(usuario)
    inicializar_banco()
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT mundo, exercicio_id, xp_ganho
            FROM exercicios_concluidos
            WHERE usuario_id = ?
            """,
            (usuario_id,),
        ).fetchall()

    concluidos = {
        (linha["mundo"], str(linha["exercicio_id"])): int(linha["xp_ganho"])
        for linha in linhas
    }

    return all(concluidos.get(chave) == XP_MINIMO_EXERCICIO for chave in obrigatorios)


def _desbloquear_e_descrever(usuario, conquista_id):
    if not desbloquear_conquista(usuario, conquista_id):
        return []

    conquista = obter_conquista(conquista_id)
    return [] if conquista is None else [conquista]


def _mundos_implementados():
    return [mundo for mundo in listar_mundos() if mundo_implementado(mundo["id"])]


def _exercicios_obrigatorios_disponiveis():
    chaves = []
    for mundo in _mundos_implementados():
        chaves.extend((mundo["id"], exercicio_id) for exercicio_id in exercicios_obrigatorios(mundo["id"]))
    return chaves
