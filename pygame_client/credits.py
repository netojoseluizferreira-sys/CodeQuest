"""Conteúdo estruturado exibido na tela de créditos do jogo."""


CREDIT_LINES = [
    ("small", ""),
    ("title", "CodeQuest"),
    ("subtitle", "Uma Jornada pelo Arquipélago de Bythos"),
    ("section", "Equipe de Desenvolvimento"),
    ("body", "**Neto** - Backend e Persistência"),
    ("small", "Sistema de XP, SQLite, organização de dados e arquitetura"),
    ("body", "**Anthony** - Interface e Experiência"),
    ("small", "Telas Pygame, navegação, estilo visual e polimento de interação"),
    ("body", "**Mayanderson** - Conteúdo e Pedagogia"),
    ("small", "Aulas, exercícios, progressão pedagógica, narrativa e revisão"),
    ("section", "Instituição e Disciplina"),
    ("body", "Universidade Federal de Alagoas (UFAL)"),
    ("small", "Curso: Ciência da Computação - 1º Período"),
    ("small", "Disciplina: Algoritmos e Programação de Computadores"),
    ("small", "Professor: Alexandre Barbosa"),
    ("section", "Data"),
    ("body", "Maio-Junho de 2025"),
    ("section", "Tecnologias"),
    ("body", "Python | Pygame | SQLite | Pytest | Git e GitHub"),
    ("section", "Links"),
    ("small", "GitHub: https://github.com/netojoseluizferreira-sys/CodeQuest"),
    ("footer", "2026 CodeQuest"),
]


def obter_linhas_creditos():
    """Retorna as linhas renderizadas na tela de créditos.

    Recebe:
        Nenhum parâmetro.

    Retorna:
        list[tuple[str, str]]: Tuplas no formato (estilo, texto). O estilo
        define fonte, cor e espaçamento; o texto pode usar marcadores
        **palavra** para trechos em negrito no renderizador Pygame.
    """
    return CREDIT_LINES
