from core import *

def display_cart(user: User):
    if user.cart == None:
        print("User not visiting any store")
        return    
    print(f"{user.name}'s Cart:")
    for item in user.cart.items:
        print(f" - Store {item.store_id}, Item {item.item_id}, Quantity {item.quantity}")
    print(f"Total: ${user.cart.total:.2f}")

def main():
    # Create a restaurant with a menu and an order
    r = Store(store_id=1, name="Testaurant")
    AddMenuItem(r,MenuItem(item_id=1, name="Burger", price=9.99))
    AddMenuItem(r,MenuItem(item_id=2, name="Fries", price=3.49))
    
    u = User(user_id=1, name="Alice")
    VisitStore(u,r)
    AddToCart(u, r, item_id=1, quantity=2)  # 2x Test Burger
    AddToCart(u, r, item_id=2, quantity=1)  # 1x Test Fries
    display_cart(u)

    PlaceOrder(u,r)
    display_cart(u)
    
    LeaveStore(u,r)
    display_cart(u)

if __name__ == "__main__":
    main()