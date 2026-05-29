import os
import subprocess
import sys
import time

from frontend.api_client import StreamlitApiClient


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_URL = os.environ.get("CODEQUEST_API_URL", "http://127.0.0.1:8000")
API_CLIENT = StreamlitApiClient(API_URL)
_api_process = None
_pygame_process = None


def obter_python_runtime():
    """Escolhe o Python correto para subprocessos locais do projeto.

    Recebe:
        Nenhum parametro.

    Retorna:
        Caminho do Python do venv quando existir; caso contrario, sys.executable.
    """
    if os.name == "nt":
        venv_python = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(BASE_DIR, "venv", "bin", "python")

    if os.path.exists(venv_python):
        return venv_python
    return sys.executable


def api_esta_disponivel():
    """Verifica se a API local esta respondendo.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando a API responde ao health check; caso contrario, False.
    """
    try:
        API_CLIENT.health()
        return True
    except Exception:
        return False


def iniciar_api_local():
    """Inicia a API local em segundo plano quando ela ainda nao estiver ativa.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando a API esta disponivel; caso contrario, False.
    """
    global _api_process

    if api_esta_disponivel():
        return True

    if _api_process is None or _api_process.poll() is not None:
        _api_process = subprocess.Popen(
            [
                obter_python_runtime(),
                "-m",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy(),
        )

    for _ in range(20):
        if api_esta_disponivel():
            return True
        time.sleep(0.15)

    return False


def iniciar_menu_pygame():
    """Abre o menu Pygame em um processo separado.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando o processo foi iniciado ou ja estava aberto; caso contrario, False.
    """
    global _pygame_process

    if os.environ.get("CODEQUEST_DISABLE_PYGAME") == "1":
        return False

    if _pygame_process is not None and _pygame_process.poll() is None:
        return True

    _pygame_process = subprocess.Popen(
        [
            obter_python_runtime(),
            "-m",
            "pygame_client.menu_app",
            "--api-url",
            API_URL,
        ],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
    )
    return True


def obter_estado_menu():
    """Consulta a acao pendente do menu Pygame pela API.

    Recebe:
        Nenhum parametro.

    Retorna:
        Dicionario com estado do menu ou None quando a API falhar.
    """
    try:
        return API_CLIENT.obter_estado_menu()
    except Exception:
        return None


def limpar_estado_menu():
    """Limpa a acao pendente do menu pela API.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    try:
        API_CLIENT.limpar_estado_menu()
    except Exception:
        pass
