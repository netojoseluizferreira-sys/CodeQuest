from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Verifica se a API esta pronta para receber chamadas.

    Recebe:
        Nenhum parametro.

    Retorna:
        Dicionario simples com status e nome do servico.
    """
    return {"status": "ok", "service": "codequest-api"}
