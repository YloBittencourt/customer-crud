# Relatório de Atividade — TDD Aplicado ao Desenvolvimento de Software

**Disciplina:** Engenharia de Software  
**Instituição:** Universidade Estadual de Santa Cruz — UESC  
**Data:** 2026-11-19  

---

## 1. Introdução

O desenvolvimento de software confiável exige mais do que código correto: exige
um processo que torne a correção verificável e sustentável ao longo do tempo.
Nesse contexto, o **Test-Driven Development (TDD)** emerge como uma das práticas
mais consolidadas da Engenharia de Software moderna, unindo design, documentação
e validação em um único fluxo de trabalho.

Este relatório descreve a metodologia TDD, as ferramentas utilizadas e como
ambas foram aplicadas no desenvolvimento de um pequeno sistema de CRUD de
cadastro de clientes em Python.

---

## 2. Metodologia — Test-Driven Development (TDD)

### 2.1 Definição

TDD é uma técnica de desenvolvimento incremental proposta por Kent Beck como
parte do Extreme Programming (XP). Sua premissa central é inverter a ordem
tradicional do desenvolvimento: **os testes são escritos antes do código de
produção**, e o código é desenvolvido exclusivamente para fazer os testes
passarem.

### 2.2 O ciclo Red-Green-Refactor

O TDD opera em ciclos curtos e repetitivos compostos por três fases:

| Fase        | Descrição |
|-------------|-----------|
| **Red**     | Escrever um teste que descreve o comportamento desejado. O teste falha porque a funcionalidade ainda não existe. |
| **Green**   | Implementar o mínimo de código necessário para o teste passar — sem se preocupar com elegância. |
| **Refactor**| Reorganizar e limpar o código (produção e testes) sem quebrar os testes existentes. |

Cada iteração do ciclo adiciona um comportamento verificável e mantém a base de
código sempre em estado funcional.

### 2.3 Benefícios

- **Design emergente:** como os testes são escritos primeiro, o código tende a
  ter interfaces mais simples e coesas (difícil de testar geralmente significa
  difícil de usar).
- **Regressão automática:** a suite de testes acumulada detecta imediatamente
  qualquer quebra introduzida por uma mudança futura.
- **Documentação executável:** os testes descrevem o comportamento esperado em
  linguagem de código, servindo de especificação viva do sistema.
- **Confiança no refactor:** com cobertura alta, é possível reorganizar o código
  sem medo de introduzir defeitos silenciosos.

### 2.4 Limitações conhecidas

- Curva de aprendizado inicial: exige disciplina para resistir à tentação de
  escrever o código antes dos testes.
- Não elimina testes de integração e de sistema — cobre apenas o comportamento
  unitário.
- Pode ser mais lento no início de um projeto comparado ao desenvolvimento sem
  testes, embora o custo seja compensado na manutenção.

---

## 3. Ferramentas Utilizadas

### 3.1 Python 3

Linguagem de programação de alto nível, com suporte nativo a módulos de teste e
amplo ecossistema. Escolhida por sua legibilidade e pelo suporte direto às
ferramentas de TDD selecionadas.

Recursos utilizados:

- `dataclasses` — modelagem do tipo `Customer` com boilerplate mínimo.
- `uuid` — geração de identificadores únicos para clientes.
- `re` — validação de formato de e-mail via expressão regular.
- `typing` — anotações de tipo para melhor legibilidade e suporte a ferramentas
  de análise estática.

### 3.2 pytest

Framework de testes para Python, amplamente adotado pela indústria. Supera o
módulo padrão `unittest` em legibilidade e recursos:

| Recurso           | Descrição |
|-------------------|-----------|
| `@pytest.fixture` | Define objetos reutilizáveis entre testes (ex.: um repositório limpo). |
| Classes de teste  | Agrupamento lógico dos casos por operação CRUD. |
| `pytest.raises`   | Verificação declarativa de exceções esperadas. |
| Relatório `-v`    | Saída detalhada com nome de cada teste e status (PASSED/FAILED). |

**Instalação:** `pip install pytest`  
**Execução:** `pytest -v`

### 3.3 pdoc

Ferramenta de geração automática de documentação HTML a partir das docstrings do
código Python. Diferentemente do Sphinx, não exige arquivos de configuração
separados — basta apontar para o módulo.

| Recurso             | Descrição |
|---------------------|-----------|
| Docstrings Google   | Suporte nativo às seções `Args:`, `Returns:`, `Raises:`, `Example:`. |
| Saída HTML          | Documentação navegável e com destaque de sintaxe. |
| Servidor ao vivo    | `pdoc src/customer_crud.py` inicia servidor local com atualização automática. |

**Instalação:** `pip install pdoc`  
**Uso:** `pdoc src/customer_crud.py --output-dir docs/`

---

## 4. Aplicação da Metodologia e das Ferramentas no Projeto

### 4.1 Escopo do software desenvolvido

O sistema implementado é um **CRUD de cadastro de clientes** com as seguintes
entidades e operações:

**Entidade `Customer`:**

| Campo   | Tipo   | Descrição |
|---------|--------|-----------|
| `id`    | `str`  | UUID gerado automaticamente |
| `name`  | `str`  | Nome completo do cliente |
| `email` | `str`  | E-mail único (validado por regex) |
| `phone` | `str`  | Telefone (formato livre) |

**Operações (`CustomerRepository`):**

| Método      | Descrição |
|-------------|-----------|
| `create`    | Cadastra um novo cliente; valida campos e unicidade de e-mail. |
| `read`      | Retorna cliente pelo ID; lança `CustomerNotFoundError` se inexistente. |
| `update`    | Atualização parcial; apenas campos fornecidos são alterados. |
| `delete`    | Remove cliente pelo ID. |
| `list_all`  | Retorna lista de todos os clientes. |
| `count`     | Retorna contagem total de clientes. |

A persistência é in-memory (dicionário Python), mantendo o foco nos requisitos
de TDD sem dependências externas como banco de dados.

### 4.2 Como o TDD foi aplicado

O desenvolvimento seguiu rigorosamente o ciclo Red-Green-Refactor. A sequência
abaixo ilustra as primeiras iterações do desenvolvimento do método `create`:

**Iteração 1 — RED:**

```python
# Teste escrito primeiro — falha porque CustomerRepository não existe ainda
def test_create_returns_customer_instance(repo):
    c = repo.create("João Silva", "joao@email.com", "(73) 99000-0001")
    assert isinstance(c, Customer)
```

**Iteração 1 — GREEN:**

```python
# Implementação mínima para o teste passar
class CustomerRepository:
    def __init__(self):
        self._store = {}

    def create(self, name, email, phone):
        customer = Customer(name=name, email=email, phone=phone)
        self._store[customer.id] = customer
        return customer
```

**Iteração 2 — RED (novo comportamento):**

```python
# Novo requisito: e-mail duplicado deve ser rejeitado
def test_create_duplicate_email_raises(repo):
    repo.create("Cliente 1", "dup@email.com", "(11) 90000-0004")
    with pytest.raises(DuplicateEmailError):
        repo.create("Cliente 2", "dup@email.com", "(11) 90000-0005")
```

**Iteração 2 — GREEN:**

```python
# Adiciona verificação de duplicidade ao método create
def create(self, name, email, phone):
    if self._email_exists(email):
        raise DuplicateEmailError(f"O e-mail '{email}' já está cadastrado.")
    customer = Customer(name=name, email=email, phone=phone)
    self._store[customer.id] = customer
    return customer
```

**Iteração 2 — REFACTOR:**

Após os testes de validação passarem para todos os campos, o código de
validação foi extraído para o método privado `_validate`, eliminando
duplicação entre `create` e `update`.

Esse padrão se repetiu para cada operação CRUD até a suite atingir 33 casos
de teste, todos passando.

### 4.3 Organização dos testes

Os testes foram organizados em classes, uma por operação, facilitando a
leitura e a identificação de falhas:

```
TestCreate      (11 casos) — criação e validações de entrada
TestRead        ( 3 casos) — leitura e ID inexistente
TestUpdate      ( 9 casos) — atualização parcial e validações
TestDelete      ( 3 casos) — remoção e efeitos colaterais
TestListAndCount( 5 casos) — listagem e contagem
TestToDict      ( 2 casos) — serialização do modelo
```

Resultado final da execução:

```
============================== 33 passed in 0.05s ==============================
```

### 4.4 Documentação do código-fonte

Todas as classes, métodos e exceções foram documentados com docstrings no
padrão Google, incluindo seções `Args`, `Returns`, `Raises` e `Example`.
O pdoc extrai essas docstrings e gera uma página HTML navegável com:

- Descrição de cada classe e método;
- Tipos dos parâmetros e retornos;
- Exemplos de uso renderizados com destaque de sintaxe.

**Para visualizar a documentação:**

```bash
# Gerar HTML em docs/
pdoc src/customer_crud.py --output-dir docs/

# Ou servir localmente (abre o navegador automaticamente)
pdoc src/customer_crud.py
```

### 4.5 Controle de versão

O projeto foi versionado no Git. A estrutura de commits reflete o ciclo TDD:

```
feat: estrutura inicial do projeto
test: adiciona testes RED para Customer e CustomerRepository
feat: implementação GREEN do método create
test: adiciona testes RED para validação de e-mail e campos vazios
feat: implementação GREEN das validações de entrada
refactor: extrai lógica de validação para método _validate
test: adiciona testes RED para read, update e delete
feat: implementação GREEN de read, update, delete, list_all e count
refactor: adiciona docstrings completas e tipagem estática
docs: adiciona README com instruções de instalação e uso
```

---

## 5. Considerações Finais

A aplicação do TDD neste projeto demonstrou na prática como a metodologia dirige
o design do software: cada teste novo forçou uma decisão de interface antes de
qualquer linha de lógica ser escrita. O método `update`, por exemplo, surgiu com
atualização parcial (apenas campos fornecidos são alterados) precisamente porque
o teste foi escrito dessa forma antes da implementação existir.

O uso do pytest tornou a escrita de testes expressiva e sem boilerplate, enquanto
o pdoc eliminou o esforço manual de manter documentação separada do código — as
docstrings já são a documentação.

O resultado é um componente pequeno, mas completamente especificado por testes,
documentado automaticamente e versionado de forma rastreável.

---

## 6. Referências

- BECK, Kent. *Test Driven Development: By Example*. Addison-Wesley, 2002.
- MARTIN, Robert C. *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall, 2008.
- pytest Documentation. Disponível em: <https://docs.pytest.org/>. Acesso em: 2026-11-19.
- pdoc Documentation. Disponível em: <https://pdoc.dev/>. Acesso em: 2026-11-19.
