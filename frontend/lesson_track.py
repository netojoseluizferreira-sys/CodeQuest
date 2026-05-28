def ordenar_ids_exercicios(exercicios):
    """Ordena os IDs de exercicios em ordem natural.

    Recebe:
        exercicios: Dicionario de exercicios indexado por ID.

    Retorna:
        Lista de IDs ordenados numericamente quando possivel.
    """
    return sorted(exercicios.keys(), key=lambda item: int(item) if str(item).isdigit() else str(item))


def obter_trilha_aula(aula, exercicios):
    """Monta a sequencia de telas de aula e exercicios.

    Recebe:
        aula: Dicionario com dados da aula carregada.
        exercicios: Dicionario de exercicios disponiveis no mundo.

    Retorna:
        Lista de etapas da trilha, usando configuracao explicita ou fallback legado.
    """
    if aula and aula.get("trilha"):
        return aula["trilha"]

    return [
        {
            "tipo": "aula",
            "id": "texto_unico",
            "titulo": aula.get("titulo", "Aula") if aula else "Aula",
            "conteudo": aula.get("conteudo", []) if aula else [],
        },
        {
            "tipo": "exercicios",
            "id": "exercicios",
            "titulo": "Exercicios",
            "exercicios": ordenar_ids_exercicios(exercicios),
        },
    ]
