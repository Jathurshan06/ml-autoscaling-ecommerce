const params = new URLSearchParams(window.location.search);

const id = params.get("id");

const API_URL = `http://localhost:3000/api/products/${id}`;

async function loadProduct() {

    const response = await fetch(API_URL);

    const product = await response.json();

    document.getElementById("product-details").innerHTML = `

        <div class="product-card">

            <img
                src="http://localhost:3000${product.image_url}"
                alt="${product.name}"
            >

            <h2>${product.name}</h2>

            <p>${product.description}</p>

            <h3>£${product.price}</h3>

        </div>

    `;
}

loadProduct();