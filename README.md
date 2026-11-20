# customer-crud

CRUD de cadastro de clientes desenvolvido com **Python** e **pytest**, seguindo
a metodologia de **Test-Driven Development (TDD)**.  
Projeto acadêmico — Engenharia de Software · UESC.

---

## Descrição

O sistema gerencia clientes em memória por meio de um repositório que expõe as
operações Create, Read, Update e Delete.  
Cada cliente possui: **id** (UUID gerado automaticamente), **name**, **email** e
**phone**.

Regras de negócio garantidas por testes:

- Nome e telefone não podem ser vazios.
- E-mail deve ter formato válido (`usuario@dominio.tld`).
- Dois clientes não podem compartilhar o mesmo e-mail.

---

## Estrutura do projeto

```
customer-crud/
├── src/
│   ├── __init__.py
│   └── customer_crud.py     # Lógica principal (Customer, CustomerRepository)
├── tests/
│   ├── __init__.py
│   └── test_customer_crud.py  # Suite de testes TDD (33 casos)
├── requirements.txt
└── README.md
```

---

## Pré-requisitos

- Python 3.10 ou superior
- pip

---

## Instalação

```bash
# Clone o repositório
git clone <URL-DO-REPOSITORIO>
cd customer-crud

# Instale as dependências
pip install -r requirements.txt
```

---

## Executar os testes

```bash
# Rodar toda a suite
pytest -v

# Resultado esperado: 33 passed
```

Saída esperada (resumida):

```
tests/test_customer_crud.py::TestCreate::test_create_returns_customer_instance PASSED
...
============================== 33 passed in 0.05s ==============================
```

---

## Gerar e visualizar a documentação

A documentação do código-fonte é gerada com **pdoc**.

```bash
# Gerar HTML da documentação
pdoc src/customer_crud.py --output-dir docs/

# Abrir no navegador (Linux)
xdg-open docs/customer_crud.html

# Abrir no navegador (macOS)
open docs/customer_crud.html

# Ou servir localmente com visualização ao vivo
pdoc src/customer_crud.py
```

Ao executar `pdoc src/customer_crud.py` sem `--output-dir`, o pdoc inicia um
servidor local e abre a documentação automaticamente no navegador padrão
(geralmente em `http://localhost:8080`).

---

## Uso rápido

```python
from src.customer_crud import CustomerRepository

repo = CustomerRepository()

# Criar
cliente = repo.create("João Silva", "joao@email.com", "(73) 99000-0001")
print(cliente.id)  # UUID gerado

# Ler
c = repo.read(cliente.id)

# Atualizar (apenas campos informados são alterados)
repo.update(cliente.id, phone="(73) 98888-0000")

# Listar todos
for c in repo.list_all():
    print(c.to_dict())

# Remover
repo.delete(cliente.id)
```

---

## Dependências

| Pacote  | Versão mínima | Finalidade                     |
|---------|--------------|--------------------------------|
| pytest  | 8.0.0        | Execução dos testes TDD        |
| pdoc    | 14.0.0       | Geração de documentação HTML   |

---

## Licença

Projeto acadêmico — uso educacional.
