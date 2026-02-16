# Avaliação de Desempenho — API

API REST para gerenciamento de avaliações de desempenho de colaboradores.

## Tecnologias

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL
- Docker

## Como executar

### Com Docker

```bash
docker-compose up --build
```

## Documentação da API
Acesse: http://localhost:8000/api/docs/

### USOS:
1. Conceitos de model rich -> acredito que abre mao de uso abusivos de orm, alem de poder utilizar a logica em outros lugares alem da view
2. bibliotecas de PEP8, para fortalecer o uso desse padrao
3. docker e dockerfile para facilitar a execucacao e uso de db
4. uso de CI/CD -> nao sei tanto irei aprender na hora
5. testes unitarios para ajudar na validacao da logica/maquina de estados -> rodar local