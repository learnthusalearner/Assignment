# Product Management System - Full Stack Application

## 📌 Overview
A **Full Stack Product Management System** built with **React (Frontend)** and **Node.js + Express + MongoDB (Backend)**. This application allows users to **manage products**, including **adding, viewing, editing, and deleting** products. It features **user authentication (JWT)**, **role-based access control**, and a **responsive UI** built with **Tailwind CSS** and **shadcn/ui**.

## 🚀 Features

### Frontend (React + React Router + shadcn/ui)
- **User Authentication (Login/Signup)**
  - JWT-based authentication
  - Protected routes
- **Product Management**
  - Add, view, edit, and delete products
  - Search & filter products
- **Responsive UI**
  - Built with **Tailwind CSS** & **shadcn/ui**
  - Dark/Light mode support
- **State Management**
  - React Context API for global state
  - React Query for API calls

### Backend (Node.js + Express + MongoDB)
- **RESTful API** for product & user management
- **JWT Authentication**
  - Secure login/signup with **bcrypt password hashing**
- **MongoDB Database**
  - Stores users & products
- **Role-Based Access Control (Admin/User)**
- **Environment Variables** (`.env`) for security

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React | Frontend framework |
| React Router DOM | Client-side routing |
| Tailwind CSS | Utility-first CSS framework |
| shadcn/ui | UI component library |
| Axios | HTTP requests to backend |
| React Hook Form | Form management |
| Zod | Form validation |

### Backend
| Technology | Purpose |
|------------|---------|
| Node.js | JavaScript runtime |
| Express | Web framework |
| MongoDB | NoSQL database |
| Mongoose | MongoDB ODM |
| Bcrypt | Password hashing |
| JSON Web Token (JWT) | Authentication |
| Dotenv | Environment variables |

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/product-management-system.git
cd product-management-system