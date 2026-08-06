const params = new URLSearchParams(window.location.search);

const id = params.get("id");

const API_URL = `${API_BASE_URL}/products/${id}`;

async function loadProduct() {

    const response = await fetch(API_URL);

    const product = await response.json();

    document.getElementById("product-details").innerHTML = `

        <div class="product-card">

            <img
                src="${IMAGE_BASE_URL}${product.image_url}"
                alt="${product.name}"
            >

            <h2>${product.name}</h2>

            <p>${product.description}</p>

            <h3>£${product.price}</h3>

        </div>

    `;
}

loadProduct();