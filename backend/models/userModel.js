const pool = require("../config/db");

async function findUserByEmail(email) {
    const result = await pool.query(
        `
        SELECT *
        FROM users
        WHERE email = $1;
        `,
        [email]
    );

    return result.rows[0];
}

async function createUser(firstName, lastName, email, hashedPassword) {
    const result = await pool.query(
        `
        INSERT INTO users
        (first_name, last_name, email, password)
        VALUES ($1, $2, $3, $4)
        RETURNING id, first_name, last_name, email, created_at;
        `,
        [firstName, lastName, email, hashedPassword]
    );

    return result.rows[0];
}

module.exports = {
    findUserByEmail,
    createUser,
};