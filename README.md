# Taggy-Green Backend API

Esta é a API Backend do projeto **Taggy-Green**, uma solução white-label de pagamento automático de mobilidade com foco no processamento de métricas ESG (economia de emissões de CO2, combustível e tempo).

## 🚀 Tecnologias

- **Linguagem:** Python 3.11+
- **Framework Web:** FastAPI
- **Validação:** Pydantic
- **Banco de Dados:** SQLite (MVP) + SQLAlchemy 2.0+
- **Migrations:** Alembic
- **Gerenciamento de Pacotes/Ambiente:** Poetry

## 📁 Estrutura do Projeto (Arquitetura em Camadas)

O projeto segue uma arquitetura estrita em camadas para garantir responsabilidade única:

- `src/api/`: Declaração de endpoints FastAPI. Não contém regras de negócio.
- `src/services/`: O cérebro da aplicação. Onde residem os cálculos do Motor ESG e regras de negócio.
- `src/repositories/`: Isolamento do Banco de Dados. Todo uso do SQLAlchemy (`session.query`, agregações, etc.) ocorre aqui.
- `src/schemas/`: Classes Pydantic para validação estrita de Input/Output (Request/Response).
- `src/models/`: Classes declarativas do SQLAlchemy mapeando as tabelas do banco de dados.
- `src/database/`: Configuração de sessão e conexão com o banco.
- `src/core/`: Configurações gerais da aplicação (variáveis de ambiente, etc).

## ⚙️ Configuração do Ambiente

Siga as instruções abaixo para configurar e executar o projeto localmente.

### 1. Pré-requisitos

- [Python 3.11+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation) instalado na máquina.

### 2. Instalação das Dependências

Na raiz do projeto, instale as dependências usando o Poetry:

```bash
poetry install
```

Isso criará automaticamente um ambiente virtual e instalará todos os pacotes listados no `pyproject.toml`.

### 3. Ativando o Ambiente Virtual

Para rodar comandos dentro do ambiente virtual, você pode prefixá-los com `poetry run` ou ativar o shell do ambiente:

```bash
poetry shell
```

### 4. Banco de Dados e Migrations

O projeto utiliza o SQLite como banco de dados local (MVP). O controle de versão das tabelas é feito de forma rigorosa pelo **Alembic**.

**A. Inicializando ou Atualizando o Banco Local (Primeira Execução / Pull da Main):**
Sempre que clonar o repositório ou baixar alterações da equipe, rode o comando abaixo para aplicar todas as *migrations* (mudanças de esquema) e criar/atualizar o arquivo `taggy_green.db`:

```bash
poetry run alembic upgrade head
```

**B. Criando uma Nova Migration (Alterou o código em `src/models/`?):**
Sempre que você criar uma nova entidade ou alterar atributos nas classes SQLAlchemy, é obrigatório gerar uma migration para refletir no banco de dados:

```bash
poetry run alembic revision --autogenerate -m "sua_mensagem_curta_e_descritiva"
```

Isso gerará um novo arquivo na pasta `alembic/versions/`. Lembre-se: **toda a pasta `alembic/` (incluindo `script.py.mako`, `env.py` e os arquivos gerados em `versions/`) DEVE ser versionada no Git**. O único arquivo que é mantido fora do Git (via `.gitignore`) é o banco de dados propriamente dito (`.db`).
### 5. Executando a Aplicação

Para iniciar o servidor de desenvolvimento (Uvicorn) com *hot-reload*:

```bash
poetry run uvicorn src.main:app --reload
```

A API estará disponível em: `http://localhost:8000`
A documentação interativa (Swagger UI) pode ser acessada em: `http://localhost:8000/docs`