# Factory CRUD (Django + SQLite + Docker)

Sistema web CRUD com interface (HTML/CSS/JS) para:
- Autenticação nativa do Django (login com **username** e senha)
- Cadastro de Máquinas (limite de 5 por usuário)
- Cadastro de Produções (obrigatório selecionar máquinas disponíveis)
- Dashboard com métricas e status de todas as produções
- Cancelamento por máquina (quando houver mais de uma)
- Cancelamento de produção (cancela todas as máquinas)
- Finalização de produção conforme regra de negócio

---

## Requisitos de Negócio Implementados

### Modelos
Todos os modelos herdam um Base Model com:
- `id` autoincrement (fornecido automaticamente pelo Django)
- `created_at`, `updated_at`
- `deleted_at` (soft delete)

### Funcionais
1. Múltiplos usuários (Django Auth).
2. Cada usuário cadastra até 5 máquinas.
3. Não permite cadastrar produção sem máquinas associadas.
4. Cancelar execução em uma máquina específica sem alterar produção e outras máquinas (quando a produção tem mais de 1 máquina).
5. Cancelar produção cancela simultaneamente todas as máquinas associadas.
6. Produção só pode ser definida como FINISHED quando todas as máquinas estiverem com status diferente de STANDBY e ONGOING.
7. Usa autenticação nativa do Django.

### Restrições
1. Não permite `serialnumber` duplicado (unique global).
2. Ao cadastrar produção, usuário só seleciona máquinas de sua propriedade (filtrado no form).
3. Não permite associar uma máquina que já está vinculada a outra produção que ainda não foi finalizada ou cancelada.

---

## Rodar com Docker (Windows / MacOS / Linux)

### 1) Instalar Docker
- Windows/Mac: instale o Docker Desktop:
  https://www.docker.com/products/docker-desktop/
- Linux: instale Docker Engine + Compose Plugin:
  https://docs.docker.com/engine/install/

Após instalar, confirme:
```bash
docker --version
docker compose version

2) Subir o sistema

Na pasta do projeto:

docker compose up --build


Acesse no navegador:

http://localhost:8000/login/

3) Criar usuário administrador (superuser)

Em outro terminal:

docker compose exec web python manage.py createsuperuser


Siga o prompt e depois faça login em:

http://localhost:8000/login/

Opcional: acessar admin:

http://localhost:8000/admin/

4) Parar o sistema
docker compose down

Rodar sem Docker (Windows / MacOS / Linux)
Pré-requisitos

Python 3.12+ (recomendado)
Download oficial:
https://www.python.org/downloads/

Verifique:

python --version


No Windows, pode ser py --version.

1) Criar e ativar ambiente virtual
Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1


Se houver bloqueio de execução de scripts, execute:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Windows (CMD)
py -m venv .venv
.\.venv\Scripts\activate.bat

MacOS/Linux
python3 -m venv .venv
source .venv/bin/activate

2) Instalar dependências
pip install -r requirements.txt

3) Rodar migrations
python manage.py migrate

4) Criar superuser
python manage.py createsuperuser

5) Subir o servidor
python manage.py runserver


Acesse:

http://127.0.0.1:8000/login/

Como usar

Faça login

/login/

Cadastre máquinas

Menu Máquinas -> Cadastrar Máquina

Limite de 5 por usuário

serialnumber não pode repetir

Cadastre produção

Menu Produções -> Cadastrar Produção

Na lista de máquinas aparecem apenas as disponíveis

Seleção por checkbox no formato MODEL / SERIALNUMBER

Gerenciar produção

Acesse os detalhes de uma produção

Ações:

Iniciar: muda produção de STANDBY -> ONGOING e marca máquinas STANDBY -> ONGOING

Cancelar Máquina: disponível quando há mais de uma máquina na produção

Cancelar Produção: cancela produção e todas as máquinas associadas

Finalizar Produção: só finaliza se todas as máquinas não estiverem em STANDBY ou ONGOING

Observações Técnicas

Banco de dados: SQLite.

No Docker, o SQLite é persistido em um volume (sqlite_data) via symlink para /app/db_data/db.sqlite3.

Soft delete: delete() seta deleted_at. A interface não expõe “Excluir”, mas o campo existe e o manager filtra automaticamente.

Estrutura (resumo)

accounts/: User customizado (username + name + email único + cnpj)

core/: Machine, Production, ProductionMachine + regras de negócio e telas

templates/: HTML

static/: CSS (Light Mode) e JS (confirmar cancelamentos)