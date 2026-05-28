from fastapi import APIRouter

from api.schemas import (
    ConcluirExercicioRequest,
    ProgressoExercicioResponse,
    RegistrarErroRequest,
)
from backend.usuario import Usuario
from utils.database import (
    exercicio_foi_concluido,
    marcar_exercicio_concluido,
    obter_erros_exercicio,
    registrar_erro_exercicio,
)
from utils.user_repository import obter_usuario_id


router = APIRouter(prefix="/progresso", tags=["progresso"])


def _usuario_por_id(usuario_id):
    """Cria uma referencia minima de usuario para consultas por ID.

    Recebe:
        usuario_id: ID do usuario desejado ou None.

    Retorna:
        Usuario com ID informado ou None para usar o usuario ativo padrao.
    """
    if usuario_id is None:
        return None
    return Usuario(id=usuario_id, nome="api", idade=1)


@router.get("/{mundo}/{exercicio_id}", response_model=ProgressoExercicioResponse)
def obter_progresso_exercicio_api(mundo: str, exercicio_id: str, usuario_id: int | None = None):
    """Carrega o progresso persistido de um exercicio.

    Recebe:
        mundo: Identificador do mundo.
        exercicio_id: Identificador do exercicio.
        usuario_id: ID opcional do usuario consultado.

    Retorna:
        Status de conclusao, erros e usuario relacionado.
    """
    usuario = _usuario_por_id(usuario_id)
    return ProgressoExercicioResponse(
        mundo=mundo,
        exercicio_id=str(exercicio_id),
        concluido=exercicio_foi_concluido(mundo, exercicio_id, usuario),
        erros=obter_erros_exercicio(mundo, exercicio_id, usuario),
        usuario_id=obter_usuario_id(usuario),
    )


@router.post("/{mundo}/{exercicio_id}/erro", response_model=ProgressoExercicioResponse)
def registrar_erro_exercicio_api(mundo: str, exercicio_id: str, payload: RegistrarErroRequest):
    """Registra um erro para um exercicio.

    Recebe:
        mundo: Identificador do mundo.
        exercicio_id: Identificador do exercicio.
        payload: ID opcional do usuario.

    Retorna:
        Status atualizado do exercicio.
    """
    usuario = _usuario_por_id(payload.usuario_id)
    erros = registrar_erro_exercicio(mundo, exercicio_id, usuario)
    return ProgressoExercicioResponse(
        mundo=mundo,
        exercicio_id=str(exercicio_id),
        concluido=exercicio_foi_concluido(mundo, exercicio_id, usuario),
        erros=erros,
        usuario_id=obter_usuario_id(usuario),
    )


@router.post("/{mundo}/{exercicio_id}/concluir", response_model=ProgressoExercicioResponse)
def concluir_exercicio_api(mundo: str, exercicio_id: str, payload: ConcluirExercicioRequest):
    """Marca um exercicio como concluido.

    Recebe:
        mundo: Identificador do mundo.
        exercicio_id: Identificador do exercicio.
        payload: XP ganho e ID opcional do usuario.

    Retorna:
        Status atualizado do exercicio.
    """
    usuario = _usuario_por_id(payload.usuario_id)
    marcar_exercicio_concluido(mundo, exercicio_id, payload.xp_ganho, usuario)
    return ProgressoExercicioResponse(
        mundo=mundo,
        exercicio_id=str(exercicio_id),
        concluido=True,
        erros=obter_erros_exercicio(mundo, exercicio_id, usuario),
        usuario_id=obter_usuario_id(usuario),
    )
