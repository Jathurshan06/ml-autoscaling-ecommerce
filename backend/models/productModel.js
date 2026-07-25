const pool = require("../config/db");

async function getAllProducts() {
    const result = await pool.query(`
        SELECT
            id,
            name,
            description,
            price,
            image_url,
            created_at
        FROM products
        ORDER BY id;
    `);

    return result.rows;
}

module.exports = {
    getAllProducts,
};