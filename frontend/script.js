// script.js
// This is where menu items are rendered dynamically.
// In a full-stack project, replace the `menuItems` array with a fetch() call to your backend API.

// ── Example: fetch from backend (uncomment when backend is ready) ──
// async function loadMenu() {
//   const response = await fetch('/api/menu');
//   const menuItems = await response.json();
//   renderMenu(menuItems);
// }

// ── Static placeholder data (remove once backend is connected) ──
const menuItems = [
    { id: 1, name: "Pizza", ingredients: "pepperoni, mushroom, mozzarella", price: 14, emoji: "🍕" },
    { id: 2, name: "Hamburger", ingredients: "beef, cheese, lettuce", price: 12, emoji: "🍔" },
    { id: 3, name: "Beer", ingredients: "grain, hops, yeast, water", price: 12, emoji: "🍺" },
];

const quantities = {};

function renderMenu(items) {
    const list = document.getElementById("menu-list");
    list.innerHTML = "";

    items.forEach(function(item) {
        if (quantities[item.id] === undefined) {
            quantities[item.id] = 0;
        }

        const div = document.createElement("div");
        div.className = "menu-item";
        div.id = `menu-item-${item.id}`;
        div.innerHTML = `
            <div class="menu-item-emoji">${item.emoji}</div>
            <div class="menu-item-info">
                <h4>${item.name}</h4>
                <p class="ingredients">${item.ingredients}</p>
                <p class="price">$${item.price}</p>
            </div>
            <div class="quantity-control">
                <button onclick="changeQty(${item.id}, -1)">−</button>
                <div class="qty-display" id="qty-${item.id}">${quantities[item.id]}</div>
                <button onclick="changeQty(${item.id}, +1)">+</button>
            </div>
        `;
        list.appendChild(div);
    });
}

function changeQty(id, delta) {
    if (quantities[id] === undefined) {
        quantities[id] = 0;
    }
    quantities[id] = Math.max(0, quantities[id] + delta);
    document.getElementById(`qty-${id}`).textContent = quantities[id];
    renderOrderSummary();
}

function renderOrderSummary() {
    const orderList = document.getElementById("order-items");
    const totalEl = document.getElementById("total-price");
    orderList.innerHTML = "";
    let total = 0;

    menuItems.forEach(function(item) {
        if (quantities[item.id] > 0) {
            total += item.price * quantities[item.id];

            const li = document.createElement("li");
            li.innerHTML = `
                <span class="item-name">
                    ${item.name}
                    <button class="remove-btn" onclick="removeItem(${item.id})">remove</button>
                </span>
                <span>$${item.price * quantities[item.id]}</span>
            `;
            orderList.appendChild(li);
        }
    });

    totalEl.textContent = `$${total}`;
}

function removeItem(id) {
    quantities[id] = 0;
    document.getElementById(`qty-${id}`).textContent = 0;
    renderOrderSummary();
}


renderMenu(menuItems);
renderOrderSummary();
// Expose functions to global scope for inline onclick handlers
window.changeQty = changeQty;
window.removeItem = removeItem;