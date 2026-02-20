# CRUD Fábrica (Django + SQLite + Docker)

Sistema web CRUD com autenticação nativa do Django, suporte a múltiplos usuários e regras de negócio para gerenciamento de máquinas e produções.

## Tecnologias

- Backend: Django (Python)
- Banco: SQLite3
- Frontend: HTML + CSS + JS (templates Django)
- Conteinerização: Docker e Docker Compose

## Requisitos atendidos (resumo)

- Autenticação nativa do Django com tela de cadastro (signup), login e logout.
- Cada usuário pode cadastrar até **5 máquinas** (conta normal) ou **10 máquinas** (conta premium).
- `serialnumber` é **único** (não permite duplicidade).
- Produção só pode ser criada com **pelo menos 1 máquina**.
- No cadastro de produção, aparecem apenas **máquinas do usuário** e **disponíveis** (não vinculadas a outra produção ativa).
- É possível cancelar uma máquina específica de uma produção sem alterar o estado geral da produção.
- É possível cancelar uma produção, cancelando simultaneamente todas as máquinas associadas.
- Produção só pode ser finalizada quando todas as máquinas estiverem com status diferente de **STANDBY** e **ONGOING**.
- Cada vínculo Produção↔Máquina registra `working_time` (em minutos) ao **finalizar** ou **cancelar**.
- Soft delete via campo `deleted_at` com botão de exclusão na interface.
- Tema **Light/Dark** com seleção persistida no navegador.

---

# Como rodar com Docker (recomendado)

## Pré-requisitos

- Docker Desktop (Windows/Mac) ou Docker Engine + Docker Compose (Linux)

Links oficiais:
- Docker Desktop: https://www.docker.com/products/docker-desktop/
- Docker Engine (Linux): https://docs.docker.com/engine/install/
- Docker Compose: https://docs.docker.com/compose/

## Passos (Windows / macOS / Linux)

1. Abra um terminal e vá até a pasta do projeto.

2. Suba o sistema:

```bash
docker compose up --build
```

Obs.: o container executa `python manage.py migrate --noinput` automaticamente ao iniciar.

3. Acesse no navegador:

- http://localhost:8000

4. (Opcional) Crie um superusuário para acessar o admin:

Em outro terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

5. Admin do Django:

- http://localhost:8000/admin

### Persistência do SQLite

O banco fica em `data/db.sqlite3` e é montado no container via volume.

## Atualizar em produção (Docker)

```bash
docker compose up --build -d
```

Se houver novas migrations, elas serão aplicadas automaticamente no startup.

---

# Como rodar localmente (sem Docker)

## Pré-requisitos

- Python 3.12+

Links oficiais:
- Python: https://www.python.org/downloads/

## Passos (Linux/macOS)

1. Crie e ative um virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Rode migrations:

```bash
python manage.py migrate
```

4. Rode o servidor:

```bash
python manage.py runserver
```

5. Acesse:

- http://127.0.0.1:8000

## Passos (Windows - PowerShell)

1. Crie e ative um virtualenv:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Rode migrations:

```powershell
python manage.py migrate
```

4. Rode o servidor:

```powershell
python manage.py runserver
```

5. Acesse:

- http://127.0.0.1:8000

---

# Telas

- Cadastro/Login: `/accounts/signup/` e `/accounts/login/`
- Dashboard (área logada): `/`
- Cadastro de Máquinas: `/machines/`
- Cadastro de Produções: `/productions/`

---

# Regras de negócio (detalhes)

## Máquinas

- Um usuário pode cadastrar no máximo **5** máquinas (normal) ou **10** (premium).
- `serialnumber` não pode repetir.
- Uma máquina não pode ser selecionada para uma produção se estiver vinculada a outra produção com status **STANDBY** ou **ONGOING**.

## Produções

- Ao criar, produção e vínculos começam em **STANDBY**.
- Você pode iniciar a produção (muda para **ONGOING**) na tela de detalhe.
- Você pode finalizar máquina individualmente (muda para **FINISHED**) sem alterar a produção.
- Você pode cancelar máquina individualmente (muda para **CANCELED**) sem alterar a produção.
- Finalizar produção só é permitido quando não existir nenhuma máquina com status **STANDBY** ou **ONGOING**.
- Cancelar produção cancela todas as máquinas associadas.
- Ao finalizar/cancelar uma máquina, o sistema calcula e salva `working_time` em minutos (baseado em `started_at` → `finished_at`/`canceled_at`).

---

# Premium (is_premium)

- O campo `is_premium` existe no usuário e controla o limite de máquinas (5/10).
- Restrição do admin: apenas o usuário logado no admin com `name == "admin"` pode alterar `is_premium`.

---

# Estrutura do projeto

- `accounts/` app de autenticação (User custom + telas)
- `factory/` app de máquinas/produções (CRUD + dashboard)
- `core/` configurações Django
- `templates/` templates HTML
- `static/` CSS
- `data/` arquivo SQLite persistente

