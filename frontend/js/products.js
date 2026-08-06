const API_URL = `${API_BASE_URL}/products`;

async function loadProducts() {

    const response = await fetch(API_URL);

    const products = await response.json();

    const container = document.getElementById("product-container");


    products.forEach(product => {

        const card = document.createElement("div");

        card.className = "product-card";


        card.innerHTML = `
            <img 
                src="${IMAGE_BASE_URL}${product.image_url}"
                alt="${product.name}"
            >

            <h3>${product.name}</h3>

            <p>${product.description}</p>

            <p>
                Price: £${product.price}
            </p>

            <a href="product.html?id=${product.id}">
                <button>
                     View Details
                </button>
            </a>
        `;


        container.appendChild(card);

    });

}


loadProducts();