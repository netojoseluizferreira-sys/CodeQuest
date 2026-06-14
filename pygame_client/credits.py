"""Conteudo estruturado exibido na tela de creditos do jogo."""


CREDIT_LINES = [
    ("small", ""),
    ("title", "CodeQuest"),
    ("subtitle", "Uma Jornada pelo Arquipelago de Bythos"),
    ("section", "Equipe de Desenvolvimento"),
    ("body", "**Neto** - Backend e Persistencia"),
    ("small", "Sistema de XP, SQLite, organizacao de dados e arquitetura"),
    ("body", "**Anthony** - Interface e Experiencia"),
    ("small", "Telas Pygame, navegacao, estilo visual e polimento de interacao"),
    ("body", "**Mayanderson** - Conteudo e Pedagogia"),
    ("small", "Aulas, exercicios, progressao pedagogica, narrativa e revisao"),
    ("section", "Instituicao e Disciplina"),
    ("body", "Universidade Federal de Alagoas (UFAL)"),
    ("small", "Curso: Ciencia da Computacao - 1o Periodo"),
    ("small", "Disciplina: Algoritmos e Programacao de Computadores"),
    ("small", "Professor: Alexandre Barbosa"),
    ("section", "Data"),
    ("body", "Maio-Junho de 2025"),
    ("section", "Agradecimentos"),
    ("small", "Ao Professor **Alexandre Barbosa** pela orientacao ao longo da disciplina."),
    ("small", "Aos **colegas** que testaram o jogo e ajudaram com feedback."),
    ("section", "Tecnologias"),
    ("body", "Python | Pygame | SQLite | Pytest | Git e GitHub"),
    ("section", "Mensagem Final"),
    (
        "quote",
        "Este projeto foi desenvolvido por Mayanderson, Neto e Anthony, alunos do primeiro periodo da UFAL.",
    ),
    ("quote", "Obrigado por embarcar nessa jornada pelo Arquipelago de Bythos."),
    ("quote", "Que o CodeQuest ajude a acender sua curiosidade por programacao."),
    ("section", "Links"),
    ("small", "GitHub: github.com/netojoseluizferreira-sys/CodeQuest"),
    ("footer", "2025 CodeQuest"),
]


def obter_linhas_creditos():
    """Retorna as linhas renderizadas na tela de creditos.

    Recebe:
        Nenhum parametro.

    Retorna:
        list[tuple[str, str]]: Tuplas no formato (estilo, texto). O estilo
        define fonte, cor e espacamento; o texto pode usar marcadores
        **palavra** para trechos em negrito no renderizador Pygame.
    """
    return CREDIT_LINES
