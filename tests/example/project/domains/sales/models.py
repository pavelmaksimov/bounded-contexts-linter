class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price


class Sale:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
        self.total = product.price * quantity
