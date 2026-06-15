"""Repositório SQLite para conclusões e erros por exercício."""

from contextlib import closing

from utils.database_connection import conectar, inicializar_banco
from utils.user_repository import obter_usuario_id


def exercicio_foi_concluido(mundo, exercicio_id, usuario=None):
    """Verifica se um exercício já foi concluído por um usuário no banco.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".
        exercicio_id (str | int): Identificador do exercício; convertido para str.
        usuario (Usuario | dict | None): Usuário alvo. None usa o ID padrão
        (USUARIO_ATIVO_ID = 1).

    Retorna:
        bool: True quando existe uma linha em exercicios_concluidos para a
        combinação (usuario_id, mundo, exercicio_id); False caso contrário.
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
    """Insere um registro de conclusão de exercício, ignorando duplicatas.

    Usa INSERT OR IGNORE, portanto re-concluir o mesmo exercício não sobrescreve
    o registro original nem lança exceção.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".
        exercicio_id (str | int): Identificador do exercício; convertido para str.
        xp_ganho (int): XP recebido na primeira conclusão (padrão 0).
        usuario (Usuario | dict | None): Usuário alvo. None usa o ID padrão.
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
    """Retorna a quantidade de erros registrados para um exercício específico.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".
        exercicio_id (str | int): Identificador do exercício; convertido para str.
        usuario (Usuario | dict | None): Usuário alvo. None usa o ID padrão.

    Retorna:
        int: Número de erros acumulados; 0 quando nenhum erro foi registrado ainda.
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
    """Incrementa em 1 o contador de erros do exercício, criando o registro se necessário.

    Usa INSERT … ON CONFLICT … DO UPDATE para upsert atômico, evitando condição
    de corrida em atualizações concorrentes.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".
        exercicio_id (str | int): Identificador do exercício; convertido para str.
        usuario (Usuario | dict | None): Usuário alvo. None usa o ID padrão.

    Retorna:
        int: Novo total de erros após o incremento.
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
