"""Testes de validação de respostas e progresso dos exercícios."""

from backend.usuario import Usuario
from backend.exercicio import carregar_exercicios
from backend.worlds import exercicios_obrigatorios
from pygame_client.learning_progress import (
    calcular_xp_potencial,
    frase_xp,
    normalizar_resposta,
    registrar_resposta,
    resposta_esta_correta,
)
from utils import database


def test_calcular_xp_potencial_tem_piso_minimo():
    assert calcular_xp_potencial(0) == 10
    assert calcular_xp_potencial(1) == 8
    assert calcular_xp_potencial(2) == 6
    assert calcular_xp_potencial(4) == 2
    assert calcular_xp_potencial(50) == 2


def test_frase_xp_tem_mensagem_para_valores_esperados():
    for xp in (2, 4, 6, 8, 10):
        assert str(xp) in frase_xp(xp)
    assert "Sem XP extra" in frase_xp(0)


def test_normalizar_resposta_remove_acentos_pontuacao_e_espacos():
    assert normalizar_resposta("  Raciocínio-Lógico / Python,  ") == "raciocinio logico python"


def test_resposta_esta_correta_para_multipla_escolha_e_texto():
    multipla = {"tipo": "multipla_escolha", "resposta": 2}
    texto = {"tipo": "completar", "respostas_aceitas": ["raciocinio humano"]}

    assert resposta_esta_correta(multipla, "2") is True
    assert resposta_esta_correta(multipla, 1) is False
    assert resposta_esta_correta(texto, "Raciocínio Humano") is True
    assert resposta_esta_correta(texto, "maquina") is False


def test_registrar_resposta_correta_concede_xp_e_bloqueia_recompensa_duplicada(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)
    exercicio = {"id": "1", "tipo": "multipla_escolha", "resposta": 0}

    primeiro = registrar_resposta("mundo_1", exercicio, 0, usuario)
    segundo = registrar_resposta("mundo_1", exercicio, 0, usuario)

    assert primeiro["acertou"] is True
    assert primeiro["xp"] == 10
    assert segundo["acertou"] is True
    assert segundo["xp"] == 0
    assert database.carregar_usuario().xp == 10


def test_registrar_resposta_errada_reduz_xp_potencial(banco_temporario):
    usuario = database.salvar_usuario(Usuario(nome="Ada", idade=12))
    exercicio = {"id": "2", "tipo": "multipla_escolha", "resposta": 1}

    erro = registrar_resposta("mundo_1", exercicio, 0, usuario)
    acerto = registrar_resposta("mundo_1", exercicio, 1, usuario)

    assert erro["acertou"] is False
    assert erro["erros"] == 1
    assert "8 XP" in erro["mensagem"]
    assert acerto["xp"] == 8


def test_registrar_ultimo_exercicio_marca_mundo_como_concluido(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)
    exercicios = carregar_exercicios("mundo_1")
    exercicio_ids = exercicios_obrigatorios("mundo_1")
    ultimo_id = exercicio_ids[-1]

    for exercicio_id in exercicio_ids[:-1]:
        database.marcar_exercicio_concluido("mundo_1", exercicio_id, 10, usuario)

    assert database.mundo_concluido("mundo_1", usuario) is False

    ultimo_exercicio = exercicios[ultimo_id]
    resultado = registrar_resposta("mundo_1", ultimo_exercicio, ultimo_exercicio["resposta"], usuario)

    assert resultado["acertou"] is True
    assert database.mundo_concluido("mundo_1", usuario) is True
