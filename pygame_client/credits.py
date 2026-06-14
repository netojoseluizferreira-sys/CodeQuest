CREDIT_LINES = [
    ("small", ""),
    ("title", "CodeQuest"),
    ("section", "Equipe de Desenvolvimento"),
    ("body", "**Neto** - Backend & API"),
    ("small", "Sistema de XP e níveis | Banco de dados | API de mídia | Arquitetura"),
    ("body", "**Anthony** - Frontend & Interface"),
    ("small", "Interface Streamlit | Navegação | Cutscenes em Pygame | Design visual"),
    ("body", "**Mayanderson** - Conteúdo & Pedagogia"),
    ("small", "Aulas e exercícios | Progressão pedagógica | Narrativa | Revisão"),
    ("section", "Instituição e Disciplina"),
    ("body", "Universidade Federal de Alagoas (UFAL)"),
    ("small", "Curso: Ciência da Computação - 1º Período"),
    ("small", "Disciplina: Algoritmos e Programação de Computadores"),
    ("small", "Professor: Alexandre Barbosa"),
    ("section", "Data"),
    ("body", "Maio-Junho de 2025"),
    ("section", "Agradecimentos Especiais"),
    ("small", "Agradecemos ao Professor **Alexandre Barbosa** pela orientação e ensinamentos."),
    ("small", "Agradecemos também aos **colegas** que testaram e deram feedback."),
    ("small", "E a **comunidade de código aberto** pelas ferramentas utilizadas."),
    ("section", "Tecnologias Utilizadas"),
    ("body", "Python | Streamlit | Pygame | FastAPI | Git & GitHub"),
    ("section", "Mensagem Final"),
    (
        "quote",
        "Este projeto foi desenvolvido por Mayanderson, Neto e Anthony, alunos do primeiro período da UFAL.",
    ),
    (
        "quote",
        "Ficamos imensamente gratos por você ter embarcado nessa jornada conosco.",
    ),
    (
        "quote",
        "Esperamos que o CodeQuest tenha acendido uma centelha no seu interesse por programação.",
    ),
    ("quote", "Desejamos sorte no seu progresso e uma incrível jornada pela frente."),
    ("section", "Links"),
    ("small", "GitHub: github.com/netojoseluizferreira-sys/CodeQuest"),
    ("footer", "© 2025 CodeQuest - Todos os direitos reservados"),
]


def obter_linhas_creditos():
    """Retorna a lista estática de linhas que compõem a tela de créditos.

    Retorna:
        list[tuple[str, str]]: Cada tupla contém o estilo da linha
        ("title", "section", "body", "small", "quote" ou "footer") e o texto
        correspondente. Textos podem conter marcadores **palavra** para negrito
        inline renderizado por _desenhar_credito_inline.
    """
    return CREDIT_LINES
