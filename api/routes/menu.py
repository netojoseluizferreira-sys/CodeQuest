from fastapi import APIRouter, status

from api.menu_state import menu_state_store
from api.schemas import MenuStateResponse, NovoJogoRequest, UsuarioResponse
from api.mappers import usuario_para_response
from utils.database import carregar_usuario, criar_usuario, resetar_banco_de_dados


router = APIRouter(prefix="/menu", tags=["menu"])


def _state_response(state):
    """Converte o estado interno do menu para resposta HTTP.

    Recebe:
        state: Instancia de MenuState.

    Retorna:
        MenuStateResponse serializavel pela API.
    """
    return MenuStateResponse(next_page=state.next_page, message=state.message)


@router.get("/estado", response_model=MenuStateResponse)
def obter_estado_menu_api():
    """Retorna a ultima acao solicitada pelo menu Pygame.

    Recebe:
        Nenhum parametro.

    Retorna:
        Estado atual do menu para o Streamlit consumir.
    """
    return _state_response(menu_state_store.obter())


@router.post("/limpar", response_model=MenuStateResponse)
def limpar_estado_menu_api():
    """Limpa a acao pendente do menu.

    Recebe:
        Nenhum parametro.

    Retorna:
        Estado limpo do menu.
    """
    return _state_response(menu_state_store.limpar())


@router.post("/novo-jogo", response_model=MenuStateResponse, status_code=status.HTTP_200_OK)
def novo_jogo_menu_api():
    """Reinicia o banco e pede ao Streamlit para abrir a criacao de perfil.

    Recebe:
        Nenhum parametro.

    Retorna:
        Estado de menu apontando para a tela de perfil.
    """
    resetar_banco_de_dados()
    state = menu_state_store.definir(
        next_page="perfil",
        message="Novo jogo iniciado. Crie seu perfil para continuar.",
    )
    return _state_response(state)


@router.post("/continuar", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def continuar_menu_api(payload: NovoJogoRequest):
    """Carrega o save atual ou cria um perfil padrao para continuar.

    Recebe:
        payload: Nome e idade usados quando nao existir save.

    Retorna:
        Usuario existente ou criado para continuar a jornada.
    """
    usuario = carregar_usuario()
    if usuario is None:
        usuario = criar_usuario(payload.nome, payload.idade)

    menu_state_store.definir(
        next_page="mundos",
        message="Save carregado. Abrindo a tela de mundos.",
    )
    return usuario_para_response(usuario)
