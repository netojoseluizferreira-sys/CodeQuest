from contextlib import closing

from utils.database_connection import conectar, inicializar_banco
from utils.user_repository import obter_usuario_id


def exercicio_foi_concluido(mundo, exercicio_id, usuario=None):
    """Verifica se um exercicio ja foi concluido por um usuario.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        True quando o exercicio ja foi concluido; caso contrario, False.
    """
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT 1
            FROM exercicios_concluidos
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        ).fetchone()

    return linha is not None


def marcar_exercicio_concluido(mundo, exercicio_id, xp_ganho=0, usuario=None):
    """Marca um exercicio como concluido para bloquear nova recompensa.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        xp_ganho: XP recebido na primeira conclusao.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        None.
    """
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO exercicios_concluidos
                (usuario_id, mundo, exercicio_id, xp_ganho)
            VALUES (?, ?, ?, ?)
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id), xp_ganho),
        )


def obter_erros_exercicio(mundo, exercicio_id, usuario=None):
    """Busca a quantidade de erros persistida para um exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        Quantidade de erros registrados para o exercicio.
    """
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT erros
            FROM exercicio_erros
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        ).fetchone()

    return 0 if linha is None else linha["erros"]


def registrar_erro_exercicio(mundo, exercicio_id, usuario=None):
    """Incrementa a quantidade de erros de um exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        Nova quantidade total de erros do exercicio.
    """
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            INSERT INTO exercicio_erros (usuario_id, mundo, exercicio_id, erros)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(usuario_id, mundo, exercicio_id) DO UPDATE SET
                erros = erros + 1,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (usuario_id, mundo, str(exercicio_id)),
        )
        linha = conexao.execute(
            """
            SELECT erros
            FROM exercicio_erros
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (usuario_id, mundo, str(exercicio_id)),
        ).fetchone()

    return linha["erros"]
