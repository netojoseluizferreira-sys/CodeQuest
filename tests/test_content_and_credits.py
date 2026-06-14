"""Testes de carregamento de conteudo pedagogico e creditos."""

from pygame_client.content import (
    carregar_aula_pygame,
    carregar_exercicios_pygame,
    corrigir_conteudo,
    obter_exercicio,
)
from pygame_client.credits import obter_linhas_creditos


def test_carregar_aula_pygame_retorna_aula_existente():
    aula = carregar_aula_pygame("mundo_1", "aula_1")

    assert aula is not None
    assert aula["titulo"]
    assert [bloco["tipo"] for bloco in aula["trilha"]] == [
        "aula",
        "exercicios",
        "aula",
        "exercicios",
        "aula",
        "exercicios",
    ]


def test_carregar_aula_pygame_inexistente_retorna_none():
    assert carregar_aula_pygame("mundo_inexistente", "aula_1") is None


def test_carregar_exercicios_pygame_e_obter_exercicio():
    exercicios = carregar_exercicios_pygame("mundo_1")

    assert len(exercicios) >= 15
    assert obter_exercicio(exercicios, 1)["id"] == 1
    assert obter_exercicio(exercicios, "nao-existe") is None


def test_corrigir_conteudo_preserva_tipos_e_corrige_recursivamente():
    valor = {"texto": "OlÃ¡", "itens": ["programaÃ§Ã£o", 3]}

    corrigido = corrigir_conteudo(valor)

    assert corrigido == {"texto": "Olá", "itens": ["programação", 3]}


def test_creditos_removem_referencias_antigas_e_mantem_tecnologias_atuais():
    texto = "\n".join(linha for _, linha in obter_linhas_creditos())

    assert "Streamlit" not in texto
    assert "FastAPI" not in texto
    assert "Pygame" in texto
    assert "SQLite" in texto
