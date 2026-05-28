from fastapi import APIRouter, HTTPException, status

from api.mappers import usuario_para_response, usuario_update_para_modelo
from api.schemas import NovoJogoRequest, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from utils.database import (
    carregar_usuario,
    criar_usuario,
    deletar_usuario,
    listar_usuarios,
    resetar_banco_de_dados,
    salvar_usuario,
)


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios_api():
    """Lista os usuarios persistidos.

    Recebe:
        Nenhum parametro.

    Retorna:
        Lista de usuarios salvos no banco SQLite.
    """
    return [usuario_para_response(usuario) for usuario in listar_usuarios()]


@router.get("/ativo", response_model=UsuarioResponse)
def carregar_usuario_ativo_api():
    """Carrega o usuario ativo salvo no banco.

    Recebe:
        Nenhum parametro.

    Retorna:
        Usuario ativo salvo.
    """
    usuario = carregar_usuario()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario ativo encontrado.",
        )
    return usuario_para_response(usuario)


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario_api(payload: UsuarioCreate):
    """Cria o usuario ativo.

    Recebe:
        payload: Nome e idade do usuario.

    Retorna:
        Usuario criado no banco.
    """
    usuario = criar_usuario(payload.nome, payload.idade)
    return usuario_para_response(usuario)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario_api(usuario_id: int, payload: UsuarioUpdate):
    """Atualiza completamente um usuario.

    Recebe:
        usuario_id: ID do usuario atualizado.
        payload: Dados completos do usuario.

    Retorna:
        Usuario atualizado.
    """
    usuario = usuario_update_para_modelo(usuario_id, payload)
    salvar_usuario(usuario)
    return usuario_para_response(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario_api(usuario_id: int):
    """Remove um usuario pelo ID.

    Recebe:
        usuario_id: ID do usuario removido.

    Retorna:
        None.
    """
    deletar_usuario(usuario_id)


@router.post("/novo-jogo", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def novo_jogo_api(payload: NovoJogoRequest):
    """Prepara um novo jogo apagando dados locais e criando usuario.

    Recebe:
        payload: Nome e idade usados para criar o novo usuario.

    Retorna:
        Usuario criado apos reset do banco.
    """
    resetar_banco_de_dados()
    usuario = criar_usuario(payload.nome, payload.idade)
    return usuario_para_response(usuario)


@router.post("/continuar", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def continuar_jogo_api(payload: NovoJogoRequest):
    """Carrega o save atual ou cria um usuario inicial.

    Recebe:
        payload: Nome e idade usados se ainda nao houver save.

    Retorna:
        Usuario existente ou recem-criado.
    """
    usuario = carregar_usuario()
    if usuario is None:
        usuario = criar_usuario(payload.nome, payload.idade)
    return usuario_para_response(usuario)
