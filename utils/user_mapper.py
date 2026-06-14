"""Conversores entre dados SQLite, dicionarios legados e Usuario."""

import json

from backend.usuario import Usuario


def garantir_usuario(usuario):
    """Normaliza entradas heterogêneas para a dataclass Usuario.

    Aceita instâncias já convertidas, dicionários legados (salvos em JSON antes
    da migração para SQLite) ou None, retornando sempre um tipo consistente.

    Recebe:
        usuario (Usuario | dict | None): Valor a normalizar.

    Retorna:
        Usuario | None: Instância de Usuario correspondente, ou None quando a
        entrada for None.
    """
    if usuario is None:
        return None
    if isinstance(usuario, Usuario):
        return usuario
    return Usuario.from_dict(usuario)


def usuario_from_linha(linha):
    """Converte uma linha da tabela usuarios (sqlite3.Row) em objeto de domínio.

    Recebe:
        linha (sqlite3.Row): Linha com colunas id, nome, idade, xp, nivel e
        conquistas (JSON serializado como texto).

    Retorna:
        Usuario: Instância preenchida com os dados da linha; conquistas é
        desserializada de JSON, usando lista vazia quando o campo for nulo.
    """
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        idade=linha["idade"],
        xp=linha["xp"],
        nivel=linha["nivel"],
        conquistas=json.loads(linha["conquistas"] or "[]"),
    )
