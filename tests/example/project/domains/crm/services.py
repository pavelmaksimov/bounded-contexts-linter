from project.domains.crm.models import Customer, Order
from project.domains.sales.models import Product

x = Product


class CustomerService:
    def create_customer(self, name: str, email: str) -> Customer:
        return Customer(name, email)


class OrderService:
    def create_order(self, customer: Customer, amount: float) -> Order:
        return Order(customer, amount)
