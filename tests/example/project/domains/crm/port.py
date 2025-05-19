"""
Contract module for the CRM bounded context.

This module defines interfaces that can be used by other bounded contexts
to interact with the CRM context without violating isolation.
"""

from project.domains.crm.models import Customer


class CustomerContract:
    """
    Contract interface for Customer entity.
    This can be safely imported by other bounded contexts.
    """

    def __init__(self, customer: Customer):
        self.id = customer.id if hasattr(customer, "id") else None
        self.name = customer.name
        self.email = customer.email

    @classmethod
    def create(cls, name: str, email: str) -> "CustomerContract":
        """
        Create a new customer contract.
        """
        customer = Customer(name, email)
        return cls(customer)
