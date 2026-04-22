from core import *

def display_cart(user: User):
    if user.cart == None:
        print("User not visiting any store")
        return    
    print(f"{user.name}'s Cart:")
    for item in user.cart.items:
        menu_item = user.store_visiting.get_item_by_id(item.item_id)
        print(f"{item.quantity}x {menu_item}")
    print(f"Total: ${user.cart.total:.2f}\n")

def main():
    # Create a restaurant with a menu and an order
    r = Store(store_id=1, name="Testaurant")
    r.add_menu_item(MenuItem(item_id=1, name="Burger", price=9.99))
    r.add_menu_item(MenuItem(item_id=2, name="Fries", price=3.49))
    
    u = User(user_id=1, name="Alice")
    u.visit_store(r)
    u.add_to_cart(item_id=1, quantity=2)  # 2x Test Burger
    u.add_to_cart(item_id=2, quantity=1)  # 1x Test Fries

    display_cart(u)
    
    u.add_to_cart(2,3)
    display_cart(u)
    
    u.place_order()
    display_cart(u)
    u.leave_store()
    display_cart(u)

if __name__ == "__main__":
    main()