# 🚀 CodeQuest

**CodeQuest** é uma plataforma educacional gamificada para ensinar lógica de programação e Python por meio de aulas curtas, exercícios, XP e progressão por mundos.

## 📋 Sobre o Projeto

O projeto organiza o aprendizado em mundos temáticos. No estado atual, o usuário cria um perfil, entra no Mundo 1, lê uma aula dividida em telas e responde exercícios intercalados no estilo Duolingo.

Cada exercício começa valendo 10 XP. A cada erro, a recompensa disponível cai em 2 XP, até o mínimo de 2 XP. Exercícios já concluídos ficam salvos no SQLite para evitar ganho duplicado de XP após reiniciar o app.

## 🧱 Estrutura Atual

```text
CodeQuest/
├── app_streamlit.py                         # Ponto de entrada do Streamlit
├── api/                                     # API REST inicial com FastAPI
│   ├── main.py                              # Fábrica e instância da aplicação
│   ├── schemas.py                           # Schemas Pydantic de entrada e saída
│   └── routes/                              # Rotas de health, usuários e progresso
├── backend/                                 # Regras de domínio e carregamento de conteúdo
│   ├── exercicio.py                         # Leitura dos JSONs de aulas e exercícios
│   ├── usuario.py                           # Dataclass de usuário
│   └── xp_system.py                         # Regras de XP e nível
├── frontend/                                # Estado e renderização do Streamlit
│   ├── exercise_state.py                    # Estado e persistência de tentativas
│   ├── exercise_validation.py               # Validação de respostas
│   ├── exercise_xp.py                       # Cálculo e mensagens de XP por exercício
│   ├── lesson_flow.py                       # Renderização do fluxo aula/exercícios
│   ├── lesson_flow_state.py                 # Estado do fluxo de aula
│   ├── lesson_track.py                      # Montagem da trilha de aula
│   ├── navigation.py                        # Navegação e estado global
│   └── pages/                               # Telas do app
│       ├── codequest.py                     # Roteador das telas
│       ├── exercicio.py                     # Renderização de um exercício
│       ├── menu.py                          # Menu principal
│       ├── mundos.py                        # Lista de mundos
│       └── perfil.py                        # Perfil do usuário
├── pygame_client/                           # Cliente Pygame inicial para menu e créditos
│   ├── audio.py                             # Trilha e efeitos sonoros gerados em memória
│   ├── credits.py                           # Conteúdo da tela de créditos
│   ├── menu_actions.py                      # Ações futuras para integração com API
│   ├── menu_app.py                          # Loop principal do menu Pygame
│   ├── palette.py                           # Paleta visual alinhada ao Streamlit
│   ├── settings.py                          # Configurações de janela
│   └── ui.py                                # Componentes visuais reutilizáveis
├── utils/                                   # Persistência e infraestrutura
│   ├── database.py                          # Fachada de compatibilidade da persistência
│   ├── database_config.py                   # Caminhos e constantes do banco
│   ├── database_connection.py               # Conexão e schema SQLite
│   ├── exercise_progress_repository.py      # Persistência de erros e conclusões
│   ├── user_mapper.py                       # Conversão de dados para Usuario
│   └── user_repository.py                   # CRUD de usuário com SQLite
├── data/                                    # Aulas e exercícios versionados
├── requirements.txt                         # Dependências do projeto
└── README.md
```

## 🕹️ Funcionalidades Atuais

- 👤 Criação e carregamento de perfil local.
- ⚡ API REST inicial para usuário, novo jogo, continuar e progresso.
- 🌍 Menu de mundos com Mundo 1 disponível.
- 📚 Aula teórica dividida em páginas curtas.
- 📝 Exercícios em sequência, um por tela, intercalados com textos de aula.
- ⭐ Sistema de XP e níveis.
- 🎯 XP dinâmico por exercício: 10, 8, 6, 4 e mínimo de 2 XP.
- ⚠️ Persistência de erros por exercício.
- 💾 Persistência local em SQLite para usuário, erros e exercícios concluídos.
- 🧪 Botão de teste para zerar o banco local.
- 🧩 Código refatorado em módulos menores para facilitar manutenção.
- 🎮 Menu inicial em Pygame preparado para futura integração com API.

## 📊 Progresso do MVP

| Item | Status | Observação |
| --- | --- | --- |
| Interface Streamlit | ✅ Feito | Entrada em `app_streamlit.py`. |
| Perfil do usuário | ✅ Feito | Modelo com `dataclass` e CRUD em SQLite. |
| Salvamento local | ✅ Feito | Persistência via SQLite em `data/codequest.db`. |
| Mundo 1 | ✅ Parcial | Cabana do Oráculo disponível. |
| Aula teórica | ✅ Feito | Aula 1 dividida em textos de estudo. |
| Exercícios | ✅ Feito | Aula 1 possui 15 exercícios intercalados em blocos de 5. |
| Fluxo aula → exercícios | ✅ Feito | Trilha no padrão texto → 5 exercícios → texto → 5 exercícios. |
| Sistema de XP | ✅ Feito | XP por acerto com penalidade de 2 XP por erro, até o mínimo de 2 XP. |
| Sistema de níveis | ✅ Feito | Nível calculado por faixas de XP. |
| Feedback acerto/erro | ✅ Feito | Feedback imediato no Streamlit. |
| Refatoração de monolitos | ✅ Feito | Frontend e persistência separados por responsabilidade. |
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

## 🎮 Menu Pygame

O menu Pygame inicial roda isolado e ainda não conversa com FastAPI. Nesta etapa ele prepara os botões de `Novo jogo`, `Continuar` e `Créditos`, deixando apenas a tela de créditos totalmente funcional.

```bash
python -m pygame_client.menu_app
```

## ⚡ API REST

A API inicial roda separada do Streamlit e do Pygame. Ela expõe rotas para saúde do serviço, usuário ativo, novo jogo, continuar jogo e progresso de exercícios.

```bash
uvicorn api.main:app --reload
```

Documentação automática:

```text
http://localhost:8000/docs
```

## 🧪 Testes e Validação

Validações usadas durante a refatoração:

```bash
python -m compileall app_streamlit.py backend frontend utils
python -c "import json; from pathlib import Path; [json.load(open(path, encoding='utf-8')) for path in Path('data').glob('*.json')]"
```

Se `pytest` estiver instalado e houver testes locais disponíveis:

```bash
python -m pytest tests
```

## 🗂️ Dados

Conteúdos versionados:

- `data/aulas.json`
- `data/exercicios.json`

## ✅ Revisão Técnica Atual

Última revisão feita no repositório:

- migração da persistência local para SQLite;
- CRUD de usuário organizado com `dataclass`;
- persistência de exercícios concluídos e erros por exercício;
- separação de monolitos do frontend em navegação, páginas, fluxo de aula, estado de exercício, validação e XP;
- separação da persistência em configuração, conexão, repositório de usuário e repositório de progresso de exercícios;
- criação da API REST inicial com FastAPI;
- remoção de funções sem uso atual;
- padronização de docstrings nas funções rastreadas;
- validação de sintaxe com `compileall`;
- validação de JSON em `data/aulas.json` e `data/exercicios.json`;
- verificação manual de inicialização do Streamlit.
