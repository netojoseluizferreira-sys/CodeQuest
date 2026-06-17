"""Testes de carregamento de conteúdo pedagógico e créditos."""

import json
from pathlib import Path

from pygame_client.content import (
    carregar_aula_pygame,
    carregar_exercicios_pygame,
    corrigir_conteudo,
    obter_exercicio,
)
from pygame_client.credits import obter_linhas_creditos


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


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


def test_carregar_aula_mundo_2_tem_textos_divididos_e_tres_exercicios():
    aula = carregar_aula_pygame("mundo_2", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 2: Primeiros passos em Python"
    assert len(aula["trilha"]) == 10

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert len(textos) == 5
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert len(blocos_exercicios) == 5
    assert all(len(bloco["exercicios"]) == 3 for bloco in blocos_exercicios)


def test_carregar_exercicios_pygame_e_obter_exercicio():
    exercicios = carregar_exercicios_pygame("mundo_1")

    assert len(exercicios) >= 15
    assert obter_exercicio(exercicios, 1)["id"] == 1
    assert obter_exercicio(exercicios, "nao-existe") is None


def test_carregar_exercicios_mundo_2():
    exercicios = carregar_exercicios_pygame("mundo_2")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 1)["pergunta"].startswith("Qual função")
    assert obter_exercicio(exercicios, 15)["resposta"] == 1


def test_carregar_aula_mundo_3_organiza_operadores_por_blocos():
    aula = carregar_aula_pygame("mundo_3", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 3: Operadores"
    assert len(aula["trilha"]) == 8

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "Operadores aritméticos",
        "Operadores relacionais",
        "Operadores lógicos",
        "Precedência de operadores",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "2", "10", "14"],
        ["3", "4", "8", "9"],
        ["5", "6", "11", "13", "15"],
        ["7", "12"],
    ]


def test_carregar_exercicios_mundo_3():
    exercicios = carregar_exercicios_pygame("mundo_3")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 1)["resposta"] == 2
    assert obter_exercicio(exercicios, 7)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 15)["resposta"] == 2


def test_carregar_aula_mundo_4_organiza_estruturas_de_decisao_por_blocos():
    aula = carregar_aula_pygame("mundo_4", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 4: Estruturas de Decisão"
    assert len(aula["trilha"]) == 6

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "if / else",
        "elif",
        "Condições aninhadas",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "2", "6", "7", "10", "11"],
        ["3", "4", "8", "9", "13", "14"],
        ["5", "12", "15"],
    ]


def test_carregar_exercicios_mundo_4():
    exercicios = carregar_exercicios_pygame("mundo_4")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 3)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 11)["resposta"] == 1
    assert obter_exercicio(exercicios, 15)["resposta"] == 3


def test_carregar_aula_mundo_5_organiza_repeticao_por_blocos():
    aula = carregar_aula_pygame("mundo_5", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 5: Estruturas de Repetição"
    assert len(aula["trilha"]) == 10

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "O que são loops",
        "Loop while",
        "Loop for",
        "break, pass e continue",
        "Loops aninhados",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "9"],
        ["2", "3", "12"],
        ["4", "11"],
        ["5", "6", "7", "10", "14", "15"],
        ["8", "13"],
    ]


def test_carregar_exercicios_mundo_5():
    exercicios = carregar_exercicios_pygame("mundo_5")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 4)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 14)["resposta"] == 2
    assert obter_exercicio(exercicios, 15)["resposta"] == 1


def test_carregar_aula_mundo_6_organiza_funcoes_por_blocos():
    aula = carregar_aula_pygame("mundo_6", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 6: Funções"
    assert len(aula["trilha"]) == 10

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "O que é uma função",
        "Criando e chamando funções",
        "Parâmetros e argumentos",
        "Retorno de valores",
        "Escopo de variáveis",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "9"],
        ["2", "3", "10", "11"],
        ["4", "5"],
        ["6", "12", "13", "15"],
        ["7", "8", "14"],
    ]


def test_carregar_exercicios_mundo_6():
    exercicios = carregar_exercicios_pygame("mundo_6")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 3)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 12)["resposta"] == 3
    assert obter_exercicio(exercicios, 15)["resposta"] == 3


def test_carregar_aula_mundo_7_organiza_listas_por_blocos():
    aula = carregar_aula_pygame("mundo_7", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 7: Vetores / Listas"
    assert len(aula["trilha"]) == 8

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "O que são listas",
        "Criando e acessando elementos",
        "Percorrendo listas com loops",
        "Adicionando, removendo e alterando",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "2"],
        ["3", "4", "5", "10", "11"],
        ["9", "12", "15"],
        ["6", "7", "8", "13", "14"],
    ]


def test_carregar_exercicios_mundo_7():
    exercicios = carregar_exercicios_pygame("mundo_7")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 4)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 14)["resposta"] == 1
    assert obter_exercicio(exercicios, 15)["resposta"] == 2


def test_carregar_aula_mundo_8_organiza_matrizes_por_blocos():
    aula = carregar_aula_pygame("mundo_8", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 8: Matrizes"
    assert len(aula["trilha"]) == 8

    textos = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "aula"]
    blocos_exercicios = [bloco for bloco in aula["trilha"] if bloco["tipo"] == "exercicios"]

    assert [bloco["titulo"] for bloco in textos] == [
        "O que são matrizes",
        "Criando e acessando matrizes",
        "Percorrendo matrizes",
        "Aplicações práticas",
    ]
    assert all(len(bloco["conteudo"]) == 3 for bloco in textos)
    assert all(bloco.get("video_url", "").startswith("https://www.youtube.com/") for bloco in textos)
    assert [bloco["exercicios"] for bloco in blocos_exercicios] == [
        ["1", "3", "6"],
        ["2", "5", "9", "10", "11", "14"],
        ["4", "7", "12", "15"],
        ["8", "13"],
    ]


def test_carregar_exercicios_mundo_8():
    exercicios = carregar_exercicios_pygame("mundo_8")

    assert len(exercicios) == 15
    assert obter_exercicio(exercicios, 3)["tipo"] == "completar"
    assert obter_exercicio(exercicios, 11)["resposta"] == 3
    assert obter_exercicio(exercicios, 15)["resposta"] == 2


def test_carregar_aula_mundo_9_tem_aula_cutscene_e_textos_finais():
    aula = carregar_aula_pygame("mundo_9", "aula_1")

    assert aula is not None
    assert aula["titulo"] == "Aula 9: Recursividade"
    assert [bloco["tipo"] for bloco in aula["trilha"]] == [
        "aula",
        "cutscene_video",
        "final_text",
        "final_text",
    ]
    assert aula["trilha"][0]["titulo"] == "Recursividade"
    assert len(aula["trilha"][0]["conteudo"]) == 3
    assert aula["trilha"][1]["frames_dir"] == "mundo_9_cutscene_frames"
    assert aula["trilha"][1]["audio"] == "mundo_9_cutscene.mp3"
    assert "Faísca" in aula["trilha"][2]["conteudo"][1]
    assert len(aula["trilha"][2]["conteudo"]) == 6
    assert aula["trilha"][3]["titulo"] == "Agradecimentos"
    assert (DATA_DIR / "music" / "mundo_9_cutscene.mp3").is_file()
    assert len(list((DATA_DIR / "mundo_9_cutscene_frames").glob("*.jpg"))) == 240


def test_mundos_3_a_9_usam_fundos_tematicos_com_overlay_leve():
    mundos = json.loads((DATA_DIR / "mundos.json").read_text(encoding="utf-8"))

    fundos_esperados = {
        "mundo_3": ("mundo_3_background.jpeg", 120),
        "mundo_4": ("mundo_4_background.jpeg", 105),
        "mundo_5": ("mundo_5_background.jpeg", 100),
        "mundo_6": ("mundo_6_background.jpeg", 115),
        "mundo_7": ("mundo_7_background.jpeg", 105),
        "mundo_8": ("mundo_8_background.jpeg", 125),
        "mundo_9": ("mundo_9_background.jpeg", 115),
    }

    for mundo_id, (background, overlay_alpha) in fundos_esperados.items():
        assert mundos[mundo_id]["background"] == background
        assert mundos[mundo_id]["overlay_alpha"] == overlay_alpha
        assert 90 <= overlay_alpha <= 130
        assert (DATA_DIR / background).is_file()


def test_corrigir_conteudo_preserva_tipos_e_corrige_recursivamente():
    valor = {"texto": "OlÃ¡", "itens": ["programaÃ§Ã£o", 3]}

    corrigido = corrigir_conteudo(valor)

    assert corrigido == {"texto": "Olá", "itens": ["programação", 3]}


def test_creditos_removem_referencias_antigas_e_mantem_tecnologias_atuais():
    texto = "\n".join(linha for _, linha in obter_linhas_creditos())

    assert "Streamlit" not in texto
    assert "FastAPI" not in texto
    assert "Agradecimentos" not in texto
    assert "Obrigado por embarcar nessa jornada" not in texto
    assert "Pygame" in texto
    assert "SQLite" in texto
