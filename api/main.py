from fastapi import FastAPI

from api.routes import health, progress, users


def criar_app():
    """Cria a aplicacao FastAPI do CodeQuest.

    Recebe:
        Nenhum parametro.

    Retorna:
        Instancia FastAPI com as rotas registradas.
    """
    app = FastAPI(
        title="CodeQuest API",
        description="API REST inicial para integrar Streamlit, Pygame e persistencia local.",
        version="0.1.0",
    )
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(progress.router)
    return app


app = criar_app()
