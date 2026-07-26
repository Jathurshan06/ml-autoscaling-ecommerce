const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const userModel = require("../models/userModel");

async function register(req, res, next) {
    try {
        const { first_name, last_name, email, password } = req.body;

        // Check required fields
        if (!first_name || !last_name || !email || !password) {
            res.status(400);
            throw new Error("All fields are required");
        }

        // Check if user already exists
        const existingUser = await userModel.findUserByEmail(email);

        if (existingUser) {
            res.status(400);
            throw new Error("Email already exists");
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Save user
        const user = await userModel.createUser(
            first_name,
            last_name,
            email,
            hashedPassword
        );

        res.status(201).json({
            success: true,
            message: "User registered successfully",
            user,
        });

    } catch (error) {
        next(error);
    }
}

async function login(req, res, next) {
    try {
        const { email, password } = req.body;

        // Check required fields
        if (!email || !password) {
            res.status(400);
            throw new Error("Email and password are required");
        }

        // Find user
        const user = await userModel.findUserByEmail(email);

        if (!user) {
            res.status(401);
            throw new Error("Invalid email or password");
        }

        // Compare password
        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            res.status(401);
            throw new Error("Invalid email or password");
        }

        // Generate JWT
        const token = jwt.sign(
            {
                id: user.id,
                email: user.email
            },
            process.env.JWT_SECRET,
            {
                expiresIn: "1d"
            }
        );

        res.status(200).json({
            success: true,
            message: "Login successful",
            token,
            user: {
                id: user.id,
                first_name: user.first_name,
                last_name: user.last_name,
                email: user.email
            }
        });

    } catch (error) {
        next(error);
    }
}

module.exports = {
    register,
    login,
};