const productModel = require("../models/productModel");

async function getAllProducts(req, res) {
    try {
        const products = await productModel.getAllProducts();

        res.status(200).json(products);
    } catch (error) {
        console.error("Error fetching products:", error);

        res.status(500).json({
            message: "Internal Server Error",
        });
    }
}

module.exports = {
    getAllProducts,
};