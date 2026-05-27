# 🚀 CodeQuest

**CodeQuest** é uma plataforma educacional gamificada para ensinar lógica de programação e Python por meio de aulas, exercícios, XP e progressão por mundos.

## 📋 Sobre o Projeto

O projeto organiza o aprendizado em mundos temáticos. No estado atual, o usuário cria um perfil, entra no Mundo 1, lê uma aula e responde exercícios em sequência. Cada exercício pode conceder XP quando acertado dentro do limite de tentativas com recompensa.

O foco do MVP é validar o ciclo principal:

1. criar ou carregar perfil;
2. acessar um mundo;
3. estudar uma aula;
4. responder exercícios em telas separadas;
5. ganhar XP e acompanhar nível.

## 🧱 Estrutura Atual

```text
CodeQuest/
├── app_streamlit.py              # Ponto de entrada do Streamlit
├── backend/                      # Regras de usuário, XP, progresso e carregamento de conteúdo
├── frontend/pages/               # Telas e componentes de fluxo do Streamlit
├── data/                         # Aulas e exercícios versionados em JSON
├── utils/                        # Persistência JSON do usuário local
├── requirements.txt              # Dependências do projeto
└── README.md
```

Arquivos locais ignorados pelo Git:

- `app.py`
- `.vscode/`
- `data/usuarios.json`
- `data/progresso.json`
- ambientes virtuais e caches Python

## 🕹️ Funcionalidades Atuais

- 👤 Criação e carregamento de perfil local.
- 🌍 Menu de mundos com Mundo 1 disponível.
- 📚 Aula teórica renderizada antes dos exercícios.
- 📝 Exercícios em sequência, um por tela.
- ⭐ Sistema de XP e níveis.
- 🎯 Limite de 3 tentativas com XP por exercício.
- ⚠️ Tentativas extras continuam liberadas, mas sem conceder XP.
- 💾 Persistência local do usuário em JSON.

## 📊 Progresso do MVP

| Item | Status | Observação |
| --- | --- | --- |
| Interface Streamlit | ✅ Feito | Entrada em `app_streamlit.py`. |
| Perfil do usuário | ✅ Feito | Nome, idade, XP, nível e conquistas. |
| Salvamento local | ✅ Feito | Persistência via JSON. |
| Mundo 1 | ✅ Parcial | Cabana do Oráculo disponível. |
| Aula teórica | ✅ Feito | Aula 1 carregada de `data/aulas.json`. |
| Exercícios | 🟡 Em progresso | Há 3 exercícios no JSON; documentação do MVP prevê 5. |
| Fluxo aula → exercícios | ✅ Feito | Telas separadas e sequência controlada no frontend. |
| Sistema de XP | ✅ Feito | XP por acerto dentro do limite de tentativas. |
| Sistema de níveis | ✅ Feito | Nível calculado por faixas de XP. |
| Feedback acerto/erro | ✅ Feito | Feedback imediato no Streamlit. |
| Cutscenes/API de mídia | 🔜 Pendente | Planejado no documento atualizado. |
| Tela de créditos | 🔜 Pendente | Planejada para fechamento do MVP. |

## 🧭 Pós-MVP

Funcionalidades planejadas após estabilizar o MVP:

- 🧩 Módulo 2: Operadores, a Forja das Runas.
- 🏛️ Módulo 3: Estruturas de decisão, a Torre dos Julgamentos.
- 🔁 Módulos futuros de repetição, funções e listas.
- 🗺️ Mapa interativo do mundo.
- 🎬 Cutscenes intermediárias por módulo.
- 🏆 Ranking online.
- 🔐 Autenticação real com login/senha.
- 🎨 Skins simples para personalização.
- 🏅 Conquistas por módulo.
- 🔊 Música e efeitos sonoros.
- 🤖 Feedback com IA como recurso opcional.
- ☁️ Hospedagem online.

## 🔧 Como Rodar

1. Crie e ative um ambiente virtual.

```bash
python -m venv venv
```

2. Instale as dependências.

```bash
pip install -r requirements.txt
```

3. Rode o Streamlit.

```bash
streamlit run app_streamlit.py
```

4. Acesse no navegador:

```text
http://localhost:8501
```

## 🗂️ Dados

Os conteúdos versionados ficam em:

- `data/aulas.json`
- `data/exercicios.json`

Os dados gerados localmente são ignorados pelo Git para evitar misturar progresso pessoal com código do projeto:

- `data/usuarios.json`
- `data/progresso.json`

## ✅ Revisão Técnica Atual

Última revisão feita no repositório:

- remoção de `.vscode/` do índice do Git;
- atualização do README para refletir o app Streamlit atual;
- correção do nível inicial do usuário para `1`;
- ajuste do caminho de `data/progresso.json` para ser independente do diretório de execução;
- remoção de `sqlite3` de `requirements.txt`, pois é biblioteca nativa do Python;
- validação de sintaxe com `compileall`;
- validação de JSON em `data/aulas.json` e `data/exercicios.json`.
