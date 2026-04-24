// script.js
// This is where menu items are rendered dynamically.
// In a full-stack project, replace the `menuItems` array with a fetch() call to your backend API.

// ── Example: fetch from backend (uncomment when backend is ready) ──
// async function loadMenu() {
//   const response = await fetch('/api/menu');
//   const menuItems = await response.json();
//   renderMenu(menuItems);
// }



async function getData(trail) {
    const url = "http://localhost:8000"
    const req_url = url+trail;
    try {
        const response = await fetch(req_url);
        if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
        }
        const result = await response.json();
        return result
        // console.log(result);
    } catch (error) {
        console.error(error.message);
    }
}


// Exactly this is returned by the api call
// const menuItems = [
//     {
//     name: 'Test Burger',
//     description: '🍔',
//     price: 12.75,
//     category: '',
//     available: true,
//     item_id: 1,
//     store_id: 1
//   },
//   {
//     name: 'Test Fries',
//     description: '🍟',
//     price: 6.5,
//     category: '',
//     available: true,
//     item_id: 2,
//     store_id: 1
//   }
//     ];

const store_id = 1;
const menuItems = await getData(`/menu/${store_id}`);
// log confirms fetch works
console.log('menuItems:', menuItems);
const quantities = {};

function renderMenu(items) {
    const list = document.getElementById("menu-list");
    list.innerHTML = "";

    items.forEach(function(item) {
        if (quantities[item.item_id] === undefined) {
            quantities[item.item_id] = 0;
        }

        const div = document.createElement("div");
        div.className = "menu-item";
        div.id = `menu-item-${item.item_id}`;
        div.innerHTML = `
            <div class="menu-item-emoji">${item.description}</div>
            <div class="menu-item-info">
                <h4>${item.name}</h4>
                <p class="price">$${item.price}</p>
            </div>
            <div class="quantity-control">
                <button onclick="changeQty(${item.item_id}, -1)">−</button>
                <div class="qty-display" id="qty-${item.item_id}">${quantities[item.item_id]}</div>
                <button onclick="changeQty(${item.item_id}, +1)">+</button>
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
        if (quantities[item.item_id] > 0) {
            total += item.price * quantities[item.item_id];

            const li = document.createElement("li");
            li.innerHTML = `
                <span class="item-name">
                    ${item.name}
                    <button class="remove-btn" onclick="removeItem(${item.item_id})">remove</button>
                </span>
                <span>$${item.price * quantities[item.item_id]}</span>
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
