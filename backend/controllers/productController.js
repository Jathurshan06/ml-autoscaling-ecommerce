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

async function getProductById(req, res) {
    try {
        const id = req.params.id;

        const product = await productModel.getProductById(id);

        if (!product) {
            return res.status(404).json({
                message: "Product not found",
            });
        }

        res.status(200).json(product);

    } catch (error) {
        console.error("Error fetching product:", error);

        res.status(500).json({
            message: "Internal Server Error",
        });
    }
}

module.exports = {
    getAllProducts,
    getProductById,
};