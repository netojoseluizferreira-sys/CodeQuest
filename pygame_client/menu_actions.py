from dataclasses import dataclass


@dataclass(frozen=True)
class MenuAction:
    """Representa uma acao futura disparada pelo menu Pygame."""

    name: str
    description: str
    payload: dict


def solicitar_novo_jogo(nome_padrao="Aventureiro"):
    """Cria o payload futuro para iniciar um novo jogo.

    Recebe:
        nome_padrao: Nome temporario usado ate existir tela de cadastro no Pygame.

    Retorna:
        MenuAction sem efeito colateral local, pronta para futura chamada FastAPI.
    """
    return MenuAction(
        name="novo_jogo",
        description="Futuramente apagara o banco e criara um usuario via API.",
        payload={"resetar_banco": True, "nome": nome_padrao},
    )


def solicitar_continuar_jogo():
    """Cria o payload futuro para continuar um save.

    Recebe:
        Nenhum parametro.

    Retorna:
        MenuAction sem efeito colateral local, pronta para futura chamada FastAPI.
    """
    return MenuAction(
        name="continuar",
        description="Futuramente carregara o save existente ou criara um novo via API.",
        payload={"criar_se_nao_existir": True},
    )
