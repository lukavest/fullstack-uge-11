async function api_call(trail,method,body) {
    const url = "http://localhost:8000"
    const req_url = url+trail;
    console.log(`${req_url} ${method} ${body}`)

    try {
        const response = await fetch(req_url, {
            method: method,
            body: body,
            headers: { "Content-Type": "application/json" }
        });
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

async function api_get(trail) {
    return api_call(trail,"GET",null)
}

async function api_post(trail,method,body) {
    if (body != null) {body = JSON.stringify(body)}
    return api_call(trail,method,body)
}

const store_id = 1;
const user_id = 1;
const menuItems = await api_get(`/menu/${store_id}`);
const quantities = {};

// should do this call when choosing store from list
await api_call(`/users/${user_id}/visit-store/${store_id}`, "POST", null)

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

function changeQty(id, delta) {
    console.log(`ChangeQty ${id} ${delta}`)
    if (quantities[id] === undefined) {
        quantities[id] = 0;
    }
    quantities[id] = Math.max(0, quantities[id] + delta);
    document.getElementById(`qty-${id}`).textContent = quantities[id];
    renderOrderSummary();
}


function removeItem(id) {
    quantities[id] = 0;
    document.getElementById(`qty-${id}`).textContent = 0;
    renderOrderSummary();
}

async function addAllCart(orderItems) {
    for (const item of orderItems) {
        await api_post(`/users/${user_id}/cart/add-item`, "POST", item);
    }
}

async function checkout() {
    // Build order items from quantities
    const orderItems = menuItems
        .filter(item => quantities[item.item_id] > 0)
        .map(item => ({
            item_id: item.item_id,
            quantity: quantities[item.item_id]
        }));

    if (orderItems.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    await addAllCart(orderItems)

    // const checkoutData = {
    //     items: orderItems
    // };

    try {
        const response = await api_call(`/users/${user_id}/checkout`, "POST", null);
        console.log("Checkout successful:", response);
        alert("Order placed successfully!");
        // Reset quantities after successful checkout
        Object.keys(quantities).forEach(key => quantities[key] = 0);
        renderOrderSummary();
        renderMenu(menuItems);
    } catch (error) {
        console.error("Checkout failed:", error);
        alert("Checkout failed. Please try again.");
    }
}

renderMenu(menuItems);
renderOrderSummary();

// Expose functions to global scope for inline onclick handlers
window.changeQty = changeQty;
window.removeItem = removeItem;
window.checkout = checkout;