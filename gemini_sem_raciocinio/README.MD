# Sistema de Gestão de Produção Industrial

Sistema CRUD para controle de produções e máquinas vinculado a usuários.

## 🚀 Como Executar

### Pré-requisitos
* **Docker**: [Download Docker](https://www.docker.com/products/docker-desktop/)
* **Docker Compose**: Incluído no Docker Desktop (Windows/Mac) ou instalável via terminal (Linux).

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd factory_project

   Subir o ambiente com Docker: No terminal, dentro da pasta raiz:

Bash
docker-compose up --build
Criar Banco de Dados e Usuário: Abra um novo terminal e execute:

Bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
Acessar o sistema: Abra o navegador em: http://localhost:8000

Regras do Sistema
Cada usuário pode ter no máximo 5 máquinas.

O botão Finalizar (Verde) na tela de detalhes só é efetivo se todas as máquinas estiverem em estados finais (Finished/Canceled).

Botões de Cancelamento (Vermelho) realizam o encerramento imediato.