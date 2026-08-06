# ML Autoscaling E-Commerce Application

## Project Overview

The ML Autoscaling E-Commerce Application is a simple web-based e-commerce system developed as part of an MSc Advanced Computer Science project.

The main purpose of this application is to provide a realistic web application environment for studying Kubernetes auto-scaling techniques. The e-commerce functionality is kept simple because the main focus of this project is not developing a complete online shopping platform, but analysing application performance and investigating Machine Learning-based predictive auto-scaling approaches.

The application allows users to view products, view individual product details, register new accounts, and log in to the system. The system consists of a frontend application, backend REST API, and PostgreSQL database.

The complete application is containerised using Docker and managed using Docker Compose to create a consistent and reproducible deployment environment.

---

# Technologies Used

## Frontend

- HTML
- CSS
- JavaScript
- Nginx

## Backend

- Node.js
- Express.js
- REST API
- JSON Web Token (JWT) Authentication

## Database

- PostgreSQL

## Containerisation

- Docker
- Docker Compose

## Future Technologies

- Kubernetes
- Horizontal Pod Autoscaler (HPA)
- Prometheus
- Grafana
- k6 Load Testing
- Machine Learning-based predictive auto-scaling

---

# Application Features

The current application provides the following features:

## Product Management

- Display all available products
- View individual product details
- Display product images and information

## User Management

- User registration
- User login
- Password encryption
- JWT-based authentication

The application does not include advanced e-commerce features such as shopping carts, payment processing, and order management because these features are outside the main scope of this research project.

---

# Application Architecture

The application follows a three-tier architecture consisting of frontend, backend, and database layers.

The frontend layer is responsible for displaying the user interface and communicating with the backend through REST API requests. The frontend application is served using an Nginx container.

The backend layer is responsible for handling application logic, user authentication, and communication with the database. It is developed using Node.js and Express.js.

The database layer uses PostgreSQL to store user information and product data.

The overall architecture is:

             User Browser
                  |
                  |
          Frontend Container
               (Nginx)
             Port: 8080
                  |
                  |
          Backend Container
         (Node.js + Express)
             Port: 3000
                  |
                  |
      PostgreSQL Database Container
             Port: 5432


---

# Running the Application

## Prerequisites

Before running the application, make sure the following tools are installed:

- Docker
- Docker Compose

---

## Clone the Repository

git clone https://github.com/Jathurshan06/ml-autoscaling-ecommerce.git

## Start the Application

docker-compose up --build

## Frontend Application

http://localhost:8080

## Backend API

http://localhost:3000

## Stop the Application

docker-compose down
