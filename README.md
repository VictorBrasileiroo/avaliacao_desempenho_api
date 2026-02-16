# API Avaliação de Desempenho  

API REST para gerenciamento de avaliações de desempenho de colaboradores, feita com Django e Django REST Framework.

## Tecnologias

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL 16
- Docker / Docker Compose
- drf-spectacular (Swagger/OpenAPI)
- pytest / pytest-django / pytest-cov
- black / flake8 (formatação e linting)
- GitHub Actions (CI)

## Como rodar

### Pré-requisitos

- Docker e Docker Compose instalados

### Subindo o projeto

```bash
docker-compose up --build
```

A API vai rodar em `http://localhost:8000/api/` e o banco já sobe junto com as migrations aplicadas automaticamente.

### Rodando sem Docker (local)

```bash
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

# configurar as variáveis de ambiente (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
# ou criar um .env na raiz do projeto

python manage.py migrate
python manage.py runserver
```

## Documentação da API

Com o projeto rodando, acesse:

- Swagger UI: http://localhost:8000/api/docs/

## Endpoints principais

| Recurso | Endpoint | Métodos |
|---------|----------|---------|
| Colaboradores | `/api/colaboradores/` | GET, POST, PUT, PATCH, DELETE |
| Tipos de Item | `/api/tipos-item-avaliacao/` | GET, POST, PUT, PATCH, DELETE |
| Avaliações | `/api/avaliacoes/` | GET, POST, PUT, PATCH, DELETE |
| Itens da Avaliação | `/api/itens-avaliacao/` | GET, POST, PUT, PATCH, DELETE |

### Ações da máquina de estados

| Ação | Endpoint | Transição |
|------|----------|-----------|
| Iniciar | `POST /api/avaliacoes/{id}/iniciar/` | Criada → Em elaboração |
| Dar feedback | `POST /api/avaliacoes/{id}/dar-feedback/` | Em elaboração → Em avaliação |
| Concluir | `POST /api/avaliacoes/{id}/concluir/` | Em avaliação → Concluída |

## Máquina de estados

A avaliação passa por 4 estados, sempre nessa ordem:

```
Criada → Em elaboração → Em avaliação → Concluída
```

- **Criada**: estado inicial, ao criar a avaliação já são gerados os itens com base nos tipos cadastrados.
- **Em elaboração**: supervisor preenche as notas dos itens (1 a 5).
- **Em avaliação**: avaliado pode adicionar observações, nota é recalculada.
- **Concluída**: avaliação finalizada, nota final calculada.

## Cálculo da nota

```
nota = (soma_das_notas_dos_itens / (quantidade_de_tipos * 5)) * 100
```

## Testes

```bash
pytest -v
pytest -v --cov=avaliacoes
```

Os testes cobrem a lógica dos models (máquina de estados e validações).

## CI/CD

O projeto tem um workflow do GitHub Actions (`.github/workflows/ci.yml`) que roda em todo push/PR na main:

1. Sobe um PostgreSQL de serviço
2. Instala as dependências
3. Roda os testes com cobertura
4. Verifica PEP8 com flake8

## Decisões técnicas

- **Models ricos**: a lógica de negócio (máquina de estados, cálculo de nota) fica nos models, não nas views. Isso facilita testar e reutilizar em outros lugares.
- **Formatação PEP8**: uso de black para formatação e flake8 para linting.
- **Docker**: facilita subir o projeto sem precisar configurar PostgreSQL na máquina.
- **Testes unitários**: focados na validação da lógica de negócio e transições de estado.

## Estrutura do projeto

```
avaliacoes/
├── models.py          # Models, máquina de estados, cálculo de nota
├── serializers.py     # Serializers do DRF
├── views.py           # ViewSets e actions
├── urls.py            # Rotas da API
├── admin.py           # Configuração do Django Admin
├── tests/
│   └── test_models.py # Testes unitários
└── migrations/
```