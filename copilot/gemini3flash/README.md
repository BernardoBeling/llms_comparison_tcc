# Sistema de Controle de Produção

Este é um sistema web CRUD desenvolvido com Django para gerenciamento de produções e máquinas, com suporte a múltiplos usuários, controle de status e restrições de negócio automatizadas.

## Tecnologias Utilizadas

- **Backend:** Python / Django
- **Banco de Dados:** SQLite3 (Persistido em arquivo local)
- **Frontend:** HTML5, CSS3 (Light Mode), JavaScript
- **Conteinerização:** Docker / Docker Compose

## Pré-requisitos

Para rodar o projeto, você precisará de uma das seguintes opções instaladas:

- **Docker e Docker Compose** (Recomendado para todas as plataformas)
- **OU** **Python 3.12+** instalado localmente.

### Links para Instalação (se necessário):
- [Download Docker](https://www.docker.com/products/docker-desktop/)
- [Download Python](https://www.python.org/downloads/)

---

## Como Executar o Sistema

### 1. Usando Docker (Recomendado)

Este método funciona de forma idêntica em **Windows, MacOS e Linux**.

1. Certifique-se de que o Docker está em execução.
2. No terminal, na raiz do projeto, execute:
   ```bash
   docker-compose up --build
   ```
3. O sistema estará disponível em [http://localhost:8000](http://localhost:8000).

### Criando um Superusuário (Admin)
Para acessar a interface administrativa do Django (/admin), execute o seguinte comando com os containers rodando:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

### 2. Execução Local (Sem Docker)

#### No Windows:
1. Abra o PowerShell ou CMD na pasta do projeto.
2. Crie um ambiente virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Execute as migrações:
   ```powershell
   python manage.py migrate
   ```
5. Inicie o servidor:
   ```powershell
   python manage.py runserver
   ```
6. (Opcional) Criar Superusuário: `python manage.py createsuperuser`
7. Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000).

#### No Linux / MacOS:
1. Abra o terminal na pasta do projeto.
2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Execute as migrações:
   ```bash
   python3 manage.py migrate
   ```
5. Inicie o servidor:
   ```bash
   python3 manage.py runserver
   ```
6. (Opcional) Criar Superusuário: `python3 manage.py createsuperuser`
7. Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Funcionalidades e Regras de Negócio Implementadas

1. **Autenticação:** Sistema de login e registro nativo do Django.
2. **Limite de Máquinas:** Cada usuário pode cadastrar no máximo 5 máquinas.
3. **Restrição de Propriedade:** Usuários só visualizam e associam máquinas de sua propriedade.
4. **Disponibilidade de Máquinas:** Uma máquina não pode ser associada a uma nova produção se já estiver em uma produção ativa (`STANDBY` ou `ONGOING`).
5. **Produção Segura:** Não é permitido criar produções sem ao menos uma máquina selecionada.
6. **Cancelamento Granular:** É possível cancelar uma única máquina sem cancelar a produção inteira.
7. **Cancelamento Total:** Ao cancelar uma produção, todas as suas máquinas são canceladas automaticamente.
8. **Validação de Finalização:** Uma produção só pode ser marcada como `FINALIZADA` se todas as suas máquinas associadas já tiverem sido concluídas ou canceladas.

## Estrutura do Projeto

- `core/`: Contém os modelos, views, formulários e lógica do sistema.
- `templates/`: Interface visual (Light Mode).
- `production_system/`: Configurações centrais do Django.
- `db.sqlite3`: Banco de dados local.
- `Dockerfile` & `docker-compose.yml`: Configurações de conteinerização.
