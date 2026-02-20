# Production System

Sistema web CRUD desenvolvido em Django para controle de produções e máquinas.

## Requisitos

- Docker
- Docker Compose

### Instalação do Docker
https://docs.docker.com/get-docker/

---

## Executando o Projeto

### 1. Clone o repositório

```bash
git clone <repo>
cd production_system

2. Suba o ambiente
docker-compose up --build

3. Acesse

http://localhost:8000

Criar usuário administrador
docker-compose exec web python manage.py createsuperuser

Observações

Banco SQLite3 interno ao container

Soft delete implementado

Autenticação nativa do Django