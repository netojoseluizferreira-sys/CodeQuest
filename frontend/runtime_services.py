import os
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from urllib.parse import urlparse

from frontend.api_client import StreamlitApiClient


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(BASE_DIR, "venv")
VENV_SITE_PACKAGES = os.path.join(
    VENV_DIR,
    "Lib" if os.name == "nt" else "lib",
    "site-packages",
)
API_URL = os.environ.get("CODEQUEST_API_URL", "http://127.0.0.1:8000")
_api_url_parseada = urlparse(API_URL)
API_HOST = os.environ.get("CODEQUEST_API_HOST", _api_url_parseada.hostname or "127.0.0.1")
API_PORT = os.environ.get("CODEQUEST_API_PORT", str(_api_url_parseada.port or 8000))
API_LOG_PATH = os.path.join(BASE_DIR, "data", "api_runtime.log")
API_CLIENT = StreamlitApiClient(API_URL, timeout=0.5)
_api_process = None
_api_thread = None
_api_server = None
_pygame_process = None


def reparar_pyvenv_cfg():
    """Corrige caminhos mojibake no pyvenv.cfg quando o projeto fica em pasta acentuada.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando o arquivo foi corrigido; caso contrario, False.
    """
    pyvenv_cfg = os.path.join(VENV_DIR, "pyvenv.cfg")
    if not os.path.exists(pyvenv_cfg):
        return False

    with open(pyvenv_cfg, "rb") as arquivo:
        conteudo_bytes = arquivo.read()

    try:
        conteudo = conteudo_bytes.decode("utf-8")
    except UnicodeDecodeError:
        encoding_local = "mbcs" if os.name == "nt" else "latin-1"
        conteudo = conteudo_bytes.decode(encoding_local, errors="replace")
        with open(pyvenv_cfg, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
        return True

    try:
        conteudo_corrigido = conteudo.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return False

    if conteudo_corrigido == conteudo:
        return False

    with open(pyvenv_cfg, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo_corrigido)
    return True


def obter_python_do_venv():
    """Retorna o executavel Python esperado dentro do venv local.

    Recebe:
        Nenhum parametro.

    Retorna:
        Caminho do Python do venv.
    """
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def obter_python_runtime():
    """Escolhe o Python correto para subprocessos locais do projeto.

    Recebe:
        Nenhum parametro.

    Retorna:
        Caminho do Python do venv quando existir; caso contrario, sys.executable.
    """
    reparar_pyvenv_cfg()
    venv_python = obter_python_do_venv()
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable


def obter_python_runtimes():
    """Lista runtimes Python candidatos para iniciar subprocessos.

    Recebe:
        Nenhum parametro.

    Retorna:
        Lista ordenada de executaveis Python sem duplicatas.
    """
    reparar_pyvenv_cfg()
    candidatos = [
        os.environ.get("CODEQUEST_PYTHON_RUNTIME"),
        obter_python_do_venv(),
        sys.executable,
    ]

    runtimes = []
    for candidato in candidatos:
        if not candidato or candidato in runtimes:
            continue
        if os.path.exists(candidato):
            runtimes.append(candidato)
    return runtimes


def runtime_eh_venv(python_runtime):
    """Verifica se um runtime aponta para o Python do venv local.

    Recebe:
        python_runtime: Caminho do executavel Python analisado.

    Retorna:
        True quando o runtime e o Python do venv; caso contrario, False.
    """
    if not python_runtime:
        return False
    return os.path.normcase(os.path.abspath(python_runtime)) == os.path.normcase(
        os.path.abspath(obter_python_do_venv())
    )


def preparar_env_subprocesso(python_runtime=None):
    """Monta o ambiente usado pelos subprocessos locais do CodeQuest.

    Recebe:
        Nenhum parametro.

    Retorna:
        Dicionario de variaveis de ambiente com o diretorio do projeto no PYTHONPATH.
    """
    env = os.environ.copy()
    pythonpath_atual = env.get("PYTHONPATH", "")
    caminhos = [BASE_DIR]
    if runtime_eh_venv(python_runtime) and os.path.exists(VENV_SITE_PACKAGES):
        caminhos.append(VENV_SITE_PACKAGES)
    if pythonpath_atual:
        caminhos.append(pythonpath_atual)
    env["PYTHONPATH"] = os.pathsep.join(caminhos)
    if os.path.exists(VENV_DIR):
        env["VIRTUAL_ENV"] = VENV_DIR
    if os.name == "nt":
        scripts_dir = os.path.join(VENV_DIR, "Scripts")
    else:
        scripts_dir = os.path.join(VENV_DIR, "bin")
    if os.path.exists(scripts_dir):
        env["PATH"] = os.pathsep.join([scripts_dir, env.get("PATH", "")])
    return env


def registrar_log_api(mensagem):
    """Registra uma mensagem de diagnostico da API local.

    Recebe:
        mensagem: Texto que descreve o evento de runtime.

    Retorna:
        None.
    """
    os.makedirs(os.path.dirname(API_LOG_PATH), exist_ok=True)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(API_LOG_PATH, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{data_hora}] {mensagem}\n")


def ler_log_api(max_linhas=30):
    """Le as linhas finais do log da API local.

    Recebe:
        max_linhas: Quantidade maxima de linhas retornadas.

    Retorna:
        Texto com as ultimas linhas do log, ou mensagem vazia quando nao houver log.
    """
    if not os.path.exists(API_LOG_PATH):
        return ""

    with open(API_LOG_PATH, "r", encoding="utf-8", errors="replace") as arquivo:
        linhas = arquivo.readlines()
    return "".join(linhas[-max_linhas:]).replace("\ufffd", "?").strip()


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

    if iniciar_api_em_thread():
        for _ in range(30):
            if api_esta_disponivel():
                registrar_log_api("API em thread interna respondeu ao health check.")
                return True
            time.sleep(0.15)

    if reparar_pyvenv_cfg():
        registrar_log_api("pyvenv.cfg corrigido para remover caminhos com mojibake.")

    runtimes = obter_python_runtimes()
    if not runtimes:
        registrar_log_api("Nenhum runtime Python disponivel para iniciar a API.")
        return False

    if _api_process is not None and _api_process.poll() is None:
        runtimes = []

    for python_runtime in runtimes:
        registrar_log_api(
            f"Iniciando API com Python '{python_runtime}' em {API_HOST}:{API_PORT}."
        )
        try:
            with open(API_LOG_PATH, "a", encoding="utf-8") as log_api:
                _api_process = subprocess.Popen(
                    [
                        python_runtime,
                        "-m",
                        "uvicorn",
                        "api.main:app",
                        "--host",
                        API_HOST,
                        "--port",
                        API_PORT,
                        "--app-dir",
                        BASE_DIR,
                    ],
                    cwd=BASE_DIR,
                    stdout=log_api,
                    stderr=log_api,
                    env=preparar_env_subprocesso(python_runtime),
                )
        except OSError as exc:
            registrar_log_api(f"Falha ao criar processo da API: {exc}.")
            continue

        for _ in range(30):
            if api_esta_disponivel():
                registrar_log_api("API respondeu ao health check.")
                return True
            if _api_process is not None and _api_process.poll() is not None:
                registrar_log_api(
                    f"Processo da API encerrou com codigo {_api_process.returncode}."
                )
                break
            time.sleep(0.15)

    if iniciar_api_http_basica():
        for _ in range(30):
            if api_esta_disponivel():
                registrar_log_api("API HTTP basica respondeu ao health check.")
                return True
            time.sleep(0.15)

    registrar_log_api("API nao respondeu dentro do tempo limite de inicializacao.")
    return False


def iniciar_api_em_thread():
    """Inicia a API dentro do processo atual quando subprocessos falham.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando a thread foi iniciada ou ja esta ativa; caso contrario, False.
    """
    global _api_thread

    if _api_thread is not None and _api_thread.is_alive():
        return True

    try:
        import uvicorn

        from api.main import app
    except Exception as exc:
        registrar_log_api(f"Falha ao importar API para thread interna: {exc}.")
        return False

    def executar_api():
        try:
            config = uvicorn.Config(
                app,
                host=API_HOST,
                port=int(API_PORT),
                log_level="info",
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as exc:
            registrar_log_api(f"API em thread interna encerrou com erro: {exc}.")

    registrar_log_api(f"Iniciando API em thread interna em {API_HOST}:{API_PORT}.")
    _api_thread = threading.Thread(
        target=executar_api,
        name="CodeQuestAPI",
        daemon=True,
    )
    _api_thread.start()
    return True


def _resposta_menu_state(state):
    """Converte estado interno do menu para dicionario HTTP.

    Recebe:
        state: Estado retornado pelo menu_state_store.

    Retorna:
        Dicionario com next_page e message.
    """
    return {"next_page": state.next_page, "message": state.message}


def _usuario_para_dict(usuario):
    """Converte usuario de dominio para dicionario HTTP simples.

    Recebe:
        usuario: Instancia de Usuario ou None.

    Retorna:
        Dicionario serializavel em JSON com os dados publicos do usuario.
    """
    if usuario is None:
        return {}
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "idade": usuario.idade,
        "xp": usuario.xp,
        "nivel": usuario.nivel,
        "conquistas": list(usuario.conquistas),
    }


class CodeQuestFallbackApiHandler(BaseHTTPRequestHandler):
    """Handler HTTP minimo para manter a API local sem FastAPI."""

    def log_message(self, format, *args):
        """Registra chamadas HTTP no log da API local.

        Recebe:
            format: Template de mensagem do BaseHTTPRequestHandler.
            args: Valores usados pelo template.

        Retorna:
            None.
        """
        registrar_log_api(format % args)

    def _enviar_json(self, payload, status_code=200):
        """Envia resposta JSON para o cliente HTTP.

        Recebe:
            payload: Dicionario serializavel em JSON.
            status_code: Codigo HTTP da resposta.

        Retorna:
            None.
        """
        corpo = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_json(self):
        """Le o corpo JSON da requisicao atual.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario enviado no corpo ou dicionario vazio.
        """
        tamanho = int(self.headers.get("Content-Length", "0") or 0)
        if tamanho <= 0:
            return {}
        corpo = self.rfile.read(tamanho).decode("utf-8")
        return json.loads(corpo or "{}")

    def do_GET(self):
        """Atende rotas GET usadas pelo Streamlit e Pygame.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.path == "/health":
            self._enviar_json({"status": "ok", "service": "codequest-api-fallback"})
            return
        if self.path == "/menu/estado":
            from api.menu_state import menu_state_store

            self._enviar_json(_resposta_menu_state(menu_state_store.obter()))
            return
        self._enviar_json({"detail": "Rota nao encontrada."}, status_code=404)

    def do_POST(self):
        """Atende rotas POST usadas pelo menu local.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        from api.menu_state import menu_state_store
        from utils.database import carregar_usuario, criar_usuario, resetar_banco_de_dados

        if self.path == "/menu/limpar":
            self._enviar_json(_resposta_menu_state(menu_state_store.limpar()))
            return

        if self.path == "/menu/novo-jogo":
            resetar_banco_de_dados()
            state = menu_state_store.definir(
                next_page="perfil",
                message="Novo jogo iniciado. Crie seu perfil para continuar.",
            )
            self._enviar_json(_resposta_menu_state(state))
            return

        if self.path == "/menu/continuar":
            payload = self._ler_json()
            nome = payload.get("nome", "Aventureiro")
            idade = int(payload.get("idade", 18))
            usuario = carregar_usuario()
            if usuario is None:
                usuario = criar_usuario(nome, idade)
            menu_state_store.definir(
                next_page="mundos",
                message="Save carregado. Abrindo a tela de mundos.",
            )
            self._enviar_json(_usuario_para_dict(usuario))
            return

        self._enviar_json({"detail": "Rota nao encontrada."}, status_code=404)


def iniciar_api_http_basica():
    """Inicia uma API HTTP minima quando FastAPI/Pydantic nao puder carregar.

    Recebe:
        Nenhum parametro.

    Retorna:
        True quando o servidor fallback foi iniciado ou ja esta ativo.
    """
    global _api_server, _api_thread

    if _api_thread is not None and _api_thread.is_alive():
        return True

    try:
        _api_server = ThreadingHTTPServer((API_HOST, int(API_PORT)), CodeQuestFallbackApiHandler)
    except OSError as exc:
        registrar_log_api(f"Falha ao iniciar API HTTP basica: {exc}.")
        return False

    registrar_log_api(f"Iniciando API HTTP basica em {API_HOST}:{API_PORT}.")
    _api_thread = threading.Thread(
        target=_api_server.serve_forever,
        name="CodeQuestFallbackAPI",
        daemon=True,
    )
    _api_thread.start()
    return True


def obter_status_api():
    """Coleta informacoes de diagnostico da API local.

    Recebe:
        Nenhum parametro.

    Retorna:
        Dicionario com disponibilidade, processo, runtime e ultimas linhas de log.
    """
    processo_ativo = _api_process is not None and _api_process.poll() is None
    thread_ativa = _api_thread is not None and _api_thread.is_alive()
    codigo_saida = None
    if _api_process is not None:
        codigo_saida = _api_process.poll()

    return {
        "url": API_URL,
        "disponivel": api_esta_disponivel(),
        "processo_ativo": processo_ativo,
        "thread_ativa": thread_ativa,
        "codigo_saida": codigo_saida,
        "python_runtime": obter_python_runtime(),
        "runtimes": obter_python_runtimes(),
        "log": ler_log_api(),
    }


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
        env=preparar_env_subprocesso(obter_python_runtime()),
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
