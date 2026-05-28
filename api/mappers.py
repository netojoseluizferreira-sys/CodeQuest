from backend.usuario import Usuario
from api.schemas import UsuarioResponse


def usuario_para_response(usuario):
    """Converte o modelo de dominio Usuario para schema de resposta.

    Recebe:
        usuario: Instancia de Usuario ou None.

    Retorna:
        UsuarioResponse quando houver usuario; caso contrario, None.
    """
    if usuario is None:
        return None

    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        idade=usuario.idade,
        xp=usuario.xp,
        nivel=usuario.nivel,
        conquistas=list(usuario.conquistas),
    )


def usuario_update_para_modelo(usuario_id, payload):
    """Converte payload de atualizacao em Usuario.

    Recebe:
        usuario_id: Identificador do usuario atualizado.
        payload: Schema UsuarioUpdate recebido pela API.

    Retorna:
        Instancia de Usuario pronta para persistencia.
    """
    return Usuario(
        id=usuario_id,
        nome=payload.nome.strip(),
        idade=payload.idade,
        xp=payload.xp,
        nivel=payload.nivel,
        conquistas=list(payload.conquistas),
    )
