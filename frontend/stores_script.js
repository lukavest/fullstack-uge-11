import { api_get, api_call } from './api.js';

const user_id = 1;

await api_call(`/users/${user_id}/leave-store`, "POST", null)

async function loadStores() {
    const stores = await api_get("/stores");
    renderStores(stores);
}

function renderStores(stores) {
    const list = document.getElementById("stores-list");
    list.innerHTML = "";

    stores.forEach(function(store) {
        const div = document.createElement("div");
        div.className = "store-card";
        div.style.cursor = "pointer";
        div.style.padding = "20px";
        div.style.margin = "10px";
        div.style.border = "1px solid #ddd";
        div.style.borderRadius = "8px";
        div.style.textAlign = "center";
        div.innerHTML = `
            <h3>${store.name}</h3>
        `;
        div.onclick = function() {
            
            window.location.href = `index.html?store_id=${store.store_id}`;
        };
        list.appendChild(div);
    });
}

loadStores();

