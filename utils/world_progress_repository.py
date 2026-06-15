"""Repositório SQLite para progresso e conclusão por mundo."""

from contextlib import closing

from backend.worlds import exercicios_obrigatorios, mundo_implementado, mundo_requisito, nome_mundo
from utils.database_connection import conectar, inicializar_banco
from utils.user_repository import obter_usuario_id

STATUS_DISPONIVEL = "disponivel"
STATUS_BLOQUEADO = "bloqueado"
STATUS_EM_BREVE = "em_breve"


def garantir_progresso_mundo(mundo_id, usuario=None):
    """Cria o registro de progresso do mundo quando ele ainda não existe."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        _garantir_progresso_mundo(conexao, usuario_id, mundo_id)


def mundo_concluido(mundo_id, usuario=None):
    """Retorna True quando o mundo está concluído para o usuário informado.

    Para compatibilidade com saves anteriores à tabela de mundos, tenta atualizar
    o status a partir dos exercícios já concluídos antes de retornar False.
    """
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        if _mundo_concluido_registrado(conexao, usuario_id, mundo_id):
            return True

    return verificar_e_marcar_conclusao_mundo(mundo_id, usuario)


def marcar_mundo_concluido(mundo_id, usuario=None):
    """Marca um mundo como concluído, sem duplicar registro por usuário e mundo."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        _marcar_mundo_concluido(conexao, usuario_id, mundo_id)


def listar_mundos_concluidos(usuario=None):
    """Lista IDs de mundos concluídos por um usuário."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        linhas = conexao.execute(
            """
            SELECT mundo_id
            FROM mundos_concluidos
            WHERE usuario_id = ? AND concluido = 1
            ORDER BY data_conclusao, mundo_id
            """,
            (usuario_id,),
        ).fetchall()

    return [linha["mundo_id"] for linha in linhas]


def obter_status_mundo(mundo_id, usuario=None):
    """Retorna o estado de acesso de um mundo para o usuário."""
    if not mundo_implementado(mundo_id):
        return {
            "estado": STATUS_EM_BREVE,
            "mundo_id": mundo_id,
            "mensagem": (
                "EM BREVE!\nOs segredos deste mundo ainda não estão prontos para serem revelados. "
                "Continue sua jornada pelos mundos disponíveis enquanto isso."
            ),
        }

    requisito = mundo_requisito(mundo_id)
    if requisito and not mundo_concluido(requisito, usuario):
        return {
            "estado": STATUS_BLOQUEADO,
            "mundo_id": mundo_id,
            "requer": requisito,
            "mensagem": f"Conclua {nome_mundo(requisito)} antes de abrir {nome_mundo(mundo_id)}.",
        }

    return {
        "estado": STATUS_DISPONIVEL,
        "mundo_id": mundo_id,
        "mensagem": "",
    }


def verificar_e_marcar_conclusao_mundo(mundo_id, usuario=None):
    """Marca o mundo como concluído quando todos os seus exercícios foram feitos."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)
    obrigatorios = set(exercicios_obrigatorios(mundo_id))

    with closing(conectar()) as conexao, conexao:
        if not obrigatorios:
            _garantir_progresso_mundo(conexao, usuario_id, mundo_id)
            return False

        linhas = conexao.execute(
            """
            SELECT exercicio_id
            FROM exercicios_concluidos
            WHERE usuario_id = ? AND mundo = ?
            """,
            (usuario_id, mundo_id),
        ).fetchall()
        exercicios_concluidos = {str(linha["exercicio_id"]) for linha in linhas}

        if obrigatorios.issubset(exercicios_concluidos):
            _marcar_mundo_concluido(conexao, usuario_id, mundo_id)
            return True

        _garantir_progresso_mundo(conexao, usuario_id, mundo_id)
        return False


def _garantir_progresso_mundo(conexao, usuario_id, mundo_id):
    conexao.execute(
        """
        INSERT OR IGNORE INTO mundos_concluidos (usuario_id, mundo_id, concluido)
        VALUES (?, ?, 0)
        """,
        (usuario_id, mundo_id),
    )


def _mundo_concluido_registrado(conexao, usuario_id, mundo_id):
    linha = conexao.execute(
        """
        SELECT concluido
        FROM mundos_concluidos
        WHERE usuario_id = ? AND mundo_id = ?
        """,
        (usuario_id, mundo_id),
    ).fetchone()
    return linha is not None and bool(linha["concluido"])


def _marcar_mundo_concluido(conexao, usuario_id, mundo_id):
    conexao.execute(
        """
        INSERT INTO mundos_concluidos (usuario_id, mundo_id, concluido, data_conclusao)
        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(usuario_id, mundo_id) DO UPDATE SET
            concluido = 1,
            data_conclusao = COALESCE(mundos_concluidos.data_conclusao, CURRENT_TIMESTAMP)
        """,
        (usuario_id, mundo_id),
    )
