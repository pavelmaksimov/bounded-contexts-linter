class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class Order:
    def __init__(self, customer: Customer, amount: float):
        self.customer = customer
        self.amount = amount
