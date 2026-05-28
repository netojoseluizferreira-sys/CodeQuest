from pydantic import BaseModel, Field


class UsuarioBase(BaseModel):
    """Campos de entrada compartilhados para usuario."""

    nome: str = Field(min_length=1, max_length=80)
    idade: int = Field(ge=1, le=120)


class UsuarioCreate(UsuarioBase):
    """Payload para criacao de usuario."""


class UsuarioUpdate(UsuarioBase):
    """Payload para atualizacao completa de usuario."""

    xp: int = Field(default=0, ge=0)
    nivel: int = Field(default=1, ge=1)
    conquistas: list[str] = Field(default_factory=list)


class UsuarioResponse(UsuarioUpdate):
    """Resposta padronizada com os dados do usuario."""

    id: int


class NovoJogoRequest(BaseModel):
    """Payload para preparar um novo jogo."""

    nome: str = Field(default="Aventureiro", min_length=1, max_length=80)
    idade: int = Field(default=18, ge=1, le=120)


class ConcluirExercicioRequest(BaseModel):
    """Payload para marcar um exercicio como concluido."""

    xp_ganho: int = Field(default=0, ge=0)
    usuario_id: int | None = Field(default=None, ge=1)


class RegistrarErroRequest(BaseModel):
    """Payload para registrar um erro de exercicio."""

    usuario_id: int | None = Field(default=None, ge=1)


class ProgressoExercicioResponse(BaseModel):
    """Resposta com status persistido de um exercicio."""

    mundo: str
    exercicio_id: str
    concluido: bool
    erros: int
    usuario_id: int
