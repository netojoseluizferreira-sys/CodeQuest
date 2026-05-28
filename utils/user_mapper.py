import json

from backend.usuario import Usuario


def garantir_usuario(usuario):
    """Normaliza entradas de usuario para a dataclass Usuario.

    Recebe:
        usuario: Instancia de Usuario, dicionario legado ou None.

    Retorna:
        Instancia de Usuario equivalente ou None quando a entrada for None.
    """
    if usuario is None:
        return None
    if isinstance(usuario, Usuario):
        return usuario
    return Usuario.from_dict(usuario)


def usuario_from_linha(linha):
    """Converte uma linha da tabela usuarios em objeto de dominio.

    Recebe:
        linha: sqlite3.Row com colunas de usuario.

    Retorna:
        Instancia de Usuario preenchida com os dados da linha.
    """
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        idade=linha["idade"],
        xp=linha["xp"],
        nivel=linha["nivel"],
        conquistas=json.loads(linha["conquistas"] or "[]"),
    )
