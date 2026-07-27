const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const notFound = require("./middleware/notFound");
const errorHandler = require("./middleware/errorHandler");
const authRoutes = require("./routes/authRoutes");
const path = require("path");

dotenv.config();

const app = express();

const productRoutes = require("./routes/productRoutes");

// Middleware
app.use(cors());
app.use(express.json());

app.use(
    "/images",
    express.static(path.join(__dirname, "public/images"))
);

// Home Route
app.get("/", (req, res) => {
    res.send("ML Autoscaling E-commerce Backend API");
});

// Product Routes
app.use("/api/products", productRoutes);

// Authentication Routes
app.use("/api/auth", authRoutes);

app.use(notFound);
app.use(errorHandler);

// Start Server
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});