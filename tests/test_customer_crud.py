"""
Suite de testes para o módulo customer_crud.

Organizada por operação CRUD, seguindo o ciclo TDD:
  RED   → teste escrito primeiro, falha porque a lógica não existe.
  GREEN → implementação mínima para o teste passar.
  REFACTOR → código limpo, testes continuam verdes.

Executar com::

    pytest -v
"""

import pytest
from src.customer_crud import (
    Customer,
    CustomerNotFoundError,
    CustomerRepository,
    DuplicateEmailError,
    ValidationError,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def repo() -> CustomerRepository:
    """Repositório limpo para cada teste."""
    return CustomerRepository()


@pytest.fixture
def populated_repo(repo: CustomerRepository) -> CustomerRepository:
    """Repositório com três clientes pré-cadastrados."""
    repo.create("Alice Santos",  "alice@email.com",  "(73) 91111-0001")
    repo.create("Bruno Lima",   "bruno@email.com",   "(73) 92222-0002")
    repo.create("Carla Souza",  "carla@email.com",   "(73) 93333-0003")
    return repo


# ===========================================================================
# CREATE
# ===========================================================================

class TestCreate:
    """Testes para CustomerRepository.create."""

    def test_create_returns_customer_instance(self, repo):
        """Criar um cliente deve retornar um objeto Customer."""
        c = repo.create("João Silva", "joao@email.com", "(73) 99000-0001")
        assert isinstance(c, Customer)

    def test_create_stores_correct_name(self, repo):
        """O nome armazenado deve ser idêntico ao informado (após strip)."""
        c = repo.create("  Maria Oliveira  ", "maria@email.com", "(11) 90000-0001")
        assert c.name == "Maria Oliveira"

    def test_create_stores_correct_email(self, repo):
        c = repo.create("Pedro Alves", "pedro@email.com", "(21) 90000-0002")
        assert c.email == "pedro@email.com"

    def test_create_stores_correct_phone(self, repo):
        c = repo.create("Ana Ramos", "ana@email.com", "(73) 98765-4321")
        assert c.phone == "(73) 98765-4321"

    def test_create_generates_unique_id(self, repo):
        """Dois clientes distintos devem ter IDs diferentes."""
        c1 = repo.create("Cliente A", "a@email.com", "(11) 90000-0001")
        c2 = repo.create("Cliente B", "b@email.com", "(11) 90000-0002")
        assert c1.id != c2.id

    def test_create_increments_count(self, repo):
        repo.create("Cliente X", "x@email.com", "(11) 90000-0003")
        assert repo.count() == 1

    def test_create_duplicate_email_raises(self, repo):
        """Dois clientes com o mesmo e-mail devem levantar DuplicateEmailError."""
        repo.create("Cliente 1", "dup@email.com", "(11) 90000-0004")
        with pytest.raises(DuplicateEmailError):
            repo.create("Cliente 2", "dup@email.com", "(11) 90000-0005")

    def test_create_empty_name_raises(self, repo):
        with pytest.raises(ValidationError):
            repo.create("", "email@email.com", "(11) 90000-0006")

    def test_create_blank_name_raises(self, repo):
        with pytest.raises(ValidationError):
            repo.create("   ", "email@email.com", "(11) 90000-0007")

    def test_create_invalid_email_raises(self, repo):
        with pytest.raises(ValidationError):
            repo.create("Nome", "nao-e-email", "(11) 90000-0008")

    def test_create_empty_phone_raises(self, repo):
        with pytest.raises(ValidationError):
            repo.create("Nome", "nome@email.com", "")


# ===========================================================================
# READ
# ===========================================================================

class TestRead:
    """Testes para CustomerRepository.read."""

    def test_read_returns_correct_customer(self, populated_repo):
        """Deve retornar exatamente o cliente do ID fornecido."""
        all_customers = populated_repo.list_all()
        target = all_customers[0]
        result = populated_repo.read(target.id)
        assert result.id == target.id
        assert result.name == target.name

    def test_read_nonexistent_raises(self, repo):
        """ID inexistente deve levantar CustomerNotFoundError."""
        with pytest.raises(CustomerNotFoundError):
            repo.read("id-que-nao-existe")

    def test_read_does_not_remove_customer(self, repo):
        """Leitura não deve alterar o repositório."""
        c = repo.create("Leitura", "leitura@email.com", "(11) 90000-0009")
        repo.read(c.id)
        assert repo.count() == 1


# ===========================================================================
# UPDATE
# ===========================================================================

class TestUpdate:
    """Testes para CustomerRepository.update."""

    def test_update_name_only(self, repo):
        """Atualizar apenas o nome não deve alterar e-mail ou telefone."""
        c = repo.create("Nome Antigo", "antigo@email.com", "(11) 90000-0010")
        updated = repo.update(c.id, name="Nome Novo")
        assert updated.name == "Nome Novo"
        assert updated.email == "antigo@email.com"
        assert updated.phone == "(11) 90000-0010"

    def test_update_email_only(self, repo):
        c = repo.create("Fulano", "fulano@email.com", "(11) 90000-0011")
        updated = repo.update(c.id, email="novo@email.com")
        assert updated.email == "novo@email.com"

    def test_update_phone_only(self, repo):
        c = repo.create("Ciclano", "ciclano@email.com", "(11) 90000-0012")
        updated = repo.update(c.id, phone="(99) 99999-9999")
        assert updated.phone == "(99) 99999-9999"

    def test_update_all_fields(self, repo):
        c = repo.create("Beltrano", "beltrano@email.com", "(11) 90000-0013")
        updated = repo.update(c.id, name="Novo Nome", email="novo2@email.com", phone="(88) 88888-8888")
        assert updated.name == "Novo Nome"
        assert updated.email == "novo2@email.com"
        assert updated.phone == "(88) 88888-8888"

    def test_update_to_same_email_does_not_raise(self, repo):
        """Atualizar para o mesmo e-mail já pertencente ao cliente não deve falhar."""
        c = repo.create("Mesmo Email", "mesmo@email.com", "(11) 90000-0014")
        updated = repo.update(c.id, email="mesmo@email.com")
        assert updated.email == "mesmo@email.com"

    def test_update_to_duplicate_email_raises(self, repo):
        c1 = repo.create("C1", "c1@email.com", "(11) 90000-0015")
        repo.create("C2", "c2@email.com", "(11) 90000-0016")
        with pytest.raises(DuplicateEmailError):
            repo.update(c1.id, email="c2@email.com")

    def test_update_nonexistent_raises(self, repo):
        with pytest.raises(CustomerNotFoundError):
            repo.update("id-fantasma", name="Teste")

    def test_update_to_invalid_email_raises(self, repo):
        c = repo.create("Inv Email", "inv@email.com", "(11) 90000-0017")
        with pytest.raises(ValidationError):
            repo.update(c.id, email="invalido")

    def test_update_to_empty_name_raises(self, repo):
        c = repo.create("Nome OK", "ok@email.com", "(11) 90000-0018")
        with pytest.raises(ValidationError):
            repo.update(c.id, name="")


# ===========================================================================
# DELETE
# ===========================================================================

class TestDelete:
    """Testes para CustomerRepository.delete."""

    def test_delete_removes_customer(self, repo):
        c = repo.create("Para Deletar", "del@email.com", "(11) 90000-0019")
        repo.delete(c.id)
        assert repo.count() == 0

    def test_delete_nonexistent_raises(self, repo):
        with pytest.raises(CustomerNotFoundError):
            repo.delete("id-inexistente")

    def test_delete_does_not_affect_others(self, populated_repo):
        """Remover um cliente não deve afetar os demais."""
        all_customers = populated_repo.list_all()
        target = all_customers[0]
        populated_repo.delete(target.id)
        assert populated_repo.count() == 2
        with pytest.raises(CustomerNotFoundError):
            populated_repo.read(target.id)


# ===========================================================================
# LIST_ALL / COUNT
# ===========================================================================

class TestListAndCount:
    """Testes para CustomerRepository.list_all e count."""

    def test_list_empty_repo(self, repo):
        assert repo.list_all() == []

    def test_list_returns_all(self, populated_repo):
        result = populated_repo.list_all()
        assert len(result) == 3

    def test_count_empty(self, repo):
        assert repo.count() == 0

    def test_count_after_creates(self, repo):
        repo.create("A", "a@a.com", "1")
        repo.create("B", "b@b.com", "2")
        assert repo.count() == 2

    def test_count_after_delete(self, repo):
        c = repo.create("A", "a2@a.com", "1")
        repo.delete(c.id)
        assert repo.count() == 0


# ===========================================================================
# TO_DICT
# ===========================================================================

class TestToDict:
    """Testes para Customer.to_dict."""

    def test_to_dict_has_all_keys(self, repo):
        c = repo.create("Dict Test", "dict@email.com", "(11) 90000-0020")
        d = c.to_dict()
        assert set(d.keys()) == {"id", "name", "email", "phone"}

    def test_to_dict_values_match(self, repo):
        c = repo.create("Dict Match", "match@email.com", "(11) 90000-0021")
        d = c.to_dict()
        assert d["name"] == "Dict Match"
        assert d["email"] == "match@email.com"
        assert d["id"] == c.id
