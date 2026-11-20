"""
Módulo de CRUD para cadastro de clientes.

Fornece a classe :class:`CustomerRepository` que gerencia clientes em memória,
e a classe :class:`Customer` que representa um cliente.

Exemplo de uso::

    from src.customer_crud import CustomerRepository

    repo = CustomerRepository()
    repo.create("João Silva", "joao@email.com", "(73) 99999-0001")
    clientes = repo.list_all()
    print(clientes)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


# ---------------------------------------------------------------------------
# Modelo de dados
# ---------------------------------------------------------------------------

@dataclass
class Customer:
    """Representa um cliente cadastrado no sistema.

    Attributes:
        name:  Nome completo do cliente.
        email: Endereço de e-mail único do cliente.
        phone: Número de telefone do cliente (formato livre).
        id:    Identificador único gerado automaticamente (UUID4).

    Example::

        c = Customer(name="Maria", email="maria@email.com", phone="(73) 98888-0000")
        print(c.id)   # UUID gerado automaticamente
    """

    name: str
    email: str
    phone: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        """Converte o cliente para dicionário.

        Returns:
            Dicionário com os campos ``id``, ``name``, ``email`` e ``phone``.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }


# ---------------------------------------------------------------------------
# Exceções de domínio
# ---------------------------------------------------------------------------

class CustomerNotFoundError(Exception):
    """Lançada quando um cliente não é encontrado pelo ID fornecido."""


class DuplicateEmailError(Exception):
    """Lançada quando já existe um cliente com o mesmo e-mail."""


class ValidationError(Exception):
    """Lançada quando os dados fornecidos são inválidos."""


# ---------------------------------------------------------------------------
# Repositório
# ---------------------------------------------------------------------------

class CustomerRepository:
    """Repositório in-memory para gerenciar clientes.

    Todas as operações são realizadas sobre um dicionário interno.
    Não há persistência entre instâncias distintas.

    Attributes:
        _store: Dicionário interno ``{id: Customer}``.

    Example::

        repo = CustomerRepository()
        c = repo.create("Ana", "ana@email.com", "(73) 91111-0000")
        repo.read(c.id)
        repo.update(c.id, name="Ana Paula")
        repo.delete(c.id)
    """

    _EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self) -> None:
        self._store: Dict[str, Customer] = {}

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _validate(self, name: str, email: str, phone: str) -> None:
        """Valida os campos obrigatórios de um cliente.

        Args:
            name:  Nome do cliente; não pode ser vazio.
            email: E-mail do cliente; deve ter formato válido.
            phone: Telefone do cliente; não pode ser vazio.

        Raises:
            ValidationError: Se qualquer campo for inválido.
        """
        if not name or not name.strip():
            raise ValidationError("O nome não pode ser vazio.")
        if not phone or not phone.strip():
            raise ValidationError("O telefone não pode ser vazio.")
        if not email or not self._EMAIL_PATTERN.match(email):
            raise ValidationError(f"E-mail inválido: '{email}'.")

    def _email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica se um e-mail já está cadastrado.

        Args:
            email:      E-mail a verificar.
            exclude_id: ID do cliente a ignorar na verificação (útil no update).

        Returns:
            ``True`` se o e-mail já existir em outro cliente.
        """
        return any(
            c.email == email and c.id != exclude_id
            for c in self._store.values()
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, name: str, email: str, phone: str) -> Customer:
        """Cria e persiste um novo cliente.

        Args:
            name:  Nome completo.
            email: E-mail único.
            phone: Telefone.

        Returns:
            O :class:`Customer` recém-criado.

        Raises:
            ValidationError:    Se algum campo for inválido.
            DuplicateEmailError: Se o e-mail já estiver em uso.

        Example::

            repo = CustomerRepository()
            c = repo.create("Pedro", "pedro@email.com", "(11) 90000-0000")
            assert c.name == "Pedro"
        """
        self._validate(name, email, phone)
        if self._email_exists(email):
            raise DuplicateEmailError(f"O e-mail '{email}' já está cadastrado.")
        customer = Customer(name=name.strip(), email=email.strip(), phone=phone.strip())
        self._store[customer.id] = customer
        return customer

    def read(self, customer_id: str) -> Customer:
        """Retorna um cliente pelo ID.

        Args:
            customer_id: UUID do cliente.

        Returns:
            O :class:`Customer` correspondente.

        Raises:
            CustomerNotFoundError: Se o ID não existir.
        """
        customer = self._store.get(customer_id)
        if customer is None:
            raise CustomerNotFoundError(f"Cliente '{customer_id}' não encontrado.")
        return customer

    def update(
        self,
        customer_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Customer:
        """Atualiza parcialmente os dados de um cliente.

        Apenas os campos fornecidos (não-None) são alterados.

        Args:
            customer_id: UUID do cliente a atualizar.
            name:        Novo nome (opcional).
            email:       Novo e-mail (opcional).
            phone:       Novo telefone (opcional).

        Returns:
            O :class:`Customer` atualizado.

        Raises:
            CustomerNotFoundError: Se o ID não existir.
            ValidationError:       Se os novos dados forem inválidos.
            DuplicateEmailError:   Se o novo e-mail já estiver em uso.
        """
        customer = self.read(customer_id)
        new_name  = name.strip()  if name  is not None else customer.name
        new_email = email.strip() if email is not None else customer.email
        new_phone = phone.strip() if phone is not None else customer.phone

        self._validate(new_name, new_email, new_phone)
        if email is not None and self._email_exists(new_email, exclude_id=customer_id):
            raise DuplicateEmailError(f"O e-mail '{new_email}' já está cadastrado.")

        customer.name  = new_name
        customer.email = new_email
        customer.phone = new_phone
        return customer

    def delete(self, customer_id: str) -> None:
        """Remove um cliente pelo ID.

        Args:
            customer_id: UUID do cliente a remover.

        Raises:
            CustomerNotFoundError: Se o ID não existir.
        """
        self.read(customer_id)  # garante que existe antes de deletar
        del self._store[customer_id]

    def list_all(self) -> List[Customer]:
        """Retorna todos os clientes cadastrados.

        Returns:
            Lista de :class:`Customer`; vazia se não houver nenhum.
        """
        return list(self._store.values())

    def count(self) -> int:
        """Retorna o número total de clientes cadastrados.

        Returns:
            Inteiro com a contagem.
        """
        return len(self._store)
