

const url = "http://localhost:8000"

async function getData(trail) {
  const req_url = url+trail;
  try {
    const response = await fetch(req_url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    // console.log(result);
    return result //.then(data => {return data})
    // result.then(function(result) {
    // return result // "Some User token"
    // })
  } catch (error) {
    console.error(error.message);
  }
}

// ── Static placeholder data (remove once backend is connected) ──
// const menuItems = [
//     { id: 1, name: "Pizza", ingredients: "pepperoni, mushroom, mozzarella", price: 14, emoji: "🍕" },
//     { id: 2, name: "Hamburger", ingredients: "beef, cheese, lettuce", price: 12, emoji: "🍔" },
//     { id: 3, name: "Beer", ingredients: "grain, hops, yeast, water", price: 12, emoji: "🍺" },
// ];


const menuItems1 = [
    { item_id: 1, name: "Pizza", price: 14.5, description: "🍕" },
    { item_id: 2, name: "Hamburger", price: 12.00, description: "🍔" },
];

const store_id = 1;
const menuItems2 = await getData(`/menu/${store_id}`);

console.log("Old menu items:")
console.log(menuItems1);

console.log("\nNew menu items:")
console.log(menuItems2);

// menuItems2.then(function(result) {
//    console.log(result) // "Some User token"
//    })
