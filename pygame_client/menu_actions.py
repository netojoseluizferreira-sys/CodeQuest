from dataclasses import dataclass


@dataclass(frozen=True)
class MenuAction:
    """Representa uma acao futura disparada pelo menu Pygame."""

    name: str
    description: str
    payload: dict
    success: bool = True


def solicitar_novo_jogo(api_client):
    """Solicita novo jogo para a API.

    Recebe:
        api_client: Cliente HTTP configurado para chamar a API.

    Retorna:
        MenuAction com resultado da chamada.
    """
    try:
        payload = api_client.novo_jogo()
        return MenuAction(
            name="novo_jogo",
            description=payload.get("message", "Novo jogo preparado."),
            payload=payload,
        )
    except Exception as exc:
        return MenuAction(
            name="novo_jogo",
            description=f"API indisponivel para novo jogo: {exc}",
            payload={},
            success=False,
        )


def solicitar_continuar_jogo(api_client):
    """Solicita continuar jogo para a API.

    Recebe:
        api_client: Cliente HTTP configurado para chamar a API.

    Retorna:
        MenuAction com resultado da chamada.
    """
    try:
        payload = api_client.continuar()
        return MenuAction(
            name="continuar",
            description=f"Save carregado para {payload.get('nome', 'usuario')}.",
            payload=payload,
        )
    except Exception as exc:
        return MenuAction(
            name="continuar",
            description=f"API indisponivel para continuar: {exc}",
            payload={},
            success=False,
        )
