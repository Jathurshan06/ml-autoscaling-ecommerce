const API_URL = `${API_BASE_URL}/products`;

async function loadFeaturedProducts() {

    const response = await fetch(API_URL);

    const products = await response.json();


    const container = document.getElementById(
        "featured-container"
    );


    products.slice(0, 6).forEach(product => {

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
                £${product.price}
            </p>
        `;


        container.appendChild(card);

    });

}


loadFeaturedProducts();