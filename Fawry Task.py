from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class Shippable(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_weight(self):
        pass

class Product(ABC):
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def is_available(self, requested_qty):
        return self.quantity >= requested_qty

    def reduce_quantity(self, qty):
        self.quantity -= qty

    @abstractmethod
    def is_expired(self):
        pass

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

class ExpirableProduct(Product, Shippable):
    def __init__(self, name, price, quantity, weight, expiry_date):
        super().__init__(name, price, quantity)
        self.weight = weight
        self.expiry_date = expiry_date

    def is_expired(self):
        return datetime.now() > self.expiry_date

    def get_weight(self):
        return self.weight

class NonExpirableProduct(Product, Shippable):
    def __init__(self, name, price, quantity, weight):
        super().__init__(name, price, quantity)
        self.weight = weight

    def is_expired(self):
        return False

    def get_weight(self):
        return self.weight

class DigitalProduct(Product):
    def is_expired(self):
        return False

class CartItem:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

class Cart:
    def __init__(self):
        self.items = []

    def add(self, product, quantity):
        if product.is_available(quantity):
            self.items.append(CartItem(product, quantity))
        else:
            raise ValueError(f"Insufficient stock for product: {product.get_name()}")

    def is_empty(self):
        return len(self.items) == 0

    def get_items(self):
        return self.items

class Customer:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def deduct(self, amount):
        self.balance -= amount

    def get_balance(self):
        return self.balance

class ShippingService:
    @staticmethod
    def ship(items):
        total_weight = 0
        print("** Shipment notice **")
        for item in items:
            weight = item.get_weight()
            total_weight += weight
            print(f"{item.get_name()} {int(weight * 1000)}g")
        print(f"Total package weight {total_weight:.1f}kg\n")

def checkout(customer, cart):
    if cart.is_empty():
        raise Exception("Cart is empty")

    subtotal = 0
    shipping = 0
    shipping_items = []

    for item in cart.get_items():
        product = item.product
        if not product.is_available(item.quantity):
            raise Exception(f"Product out of stock: {product.get_name()}")
        if product.is_expired():
            raise Exception(f"Product expired: {product.get_name()}")

        subtotal += product.get_price() * item.quantity
        product.reduce_quantity(item.quantity)

        if isinstance(product, Shippable):
            shipping_items.extend([product] * item.quantity)
            shipping += 10 * item.quantity

    total = subtotal + shipping

    if customer.get_balance() < total:
        raise Exception("Insufficient balance")

    ShippingService.ship(shipping_items)

    print("** Checkout receipt **")
    for item in cart.get_items():
        print(f"{item.quantity}x {item.product.get_name()}\t{item.product.get_price() * item.quantity:.0f}")
    print("--------------------")
    print(f"Subtotal\t{subtotal:.0f}")
    print(f"Shipping\t{shipping:.0f}")
    print(f"Amount\t{total:.0f}")

    customer.deduct(total)
    print(f"Balance after payment: {customer.get_balance():.2f}")

def display_products(products):
    print("\nAvailable Products:")
    for i, product in enumerate(products):
        exp = f" (expires: {product.expiry_date.date()})" if isinstance(product, ExpirableProduct) else ""
        print(f"{i + 1}. {product.get_name()} - ${product.get_price()} ({product.quantity} in stock){exp}")

def main():
    cheese = ExpirableProduct("Cheese", 100, 10, 0.2, datetime.now() + timedelta(days=5))
    biscuits = ExpirableProduct("Biscuits", 150, 5, 0.7, datetime.now() + timedelta(days=2))
    tv = NonExpirableProduct("TV", 1000, 3, 8)
    scratch_card = DigitalProduct("ScratchCard", 50, 100)

    products = [cheese, biscuits, tv, scratch_card]

    customer = Customer("Rawan", 1000)
    cart = Cart()

    while True:
        display_products(products)
        choice = input("\nEnter product number to add to cart (or 'checkout' to finish): ")
        if choice.lower() == 'checkout':
            break
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(products):
            print("Invalid choice. Try again.")
            continue

        qty = input("Enter quantity: ")
        if not qty.isdigit() or int(qty) <= 0:
            print("Invalid quantity. Try again.")
            continue

        product = products[int(choice) - 1]
        try:
            cart.add(product, int(qty))
            print(f"Added {qty}x {product.get_name()} to cart.")
        except ValueError as e:
            print(e)

    try:
        checkout(customer, cart)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
