const express = require("express");
const router = express.Router();

const productController = require("../controllers/productController");

// GET /api/products
router.get("/", productController.getAllProducts);

// GET /api/products/:id
router.get("/:id", productController.getProductById);


module.exports = router;