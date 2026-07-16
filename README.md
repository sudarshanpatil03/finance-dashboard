# 💰 Personal Finance & Debt Payoff Dashboard

![Live Demo](https://img.shields.io/badge/Live_Demo-Active-success)
![React](https://img.shields.io/badge/Frontend-React.js-blue)
![Flask](https://img.shields.io/badge/Backend-Python_Flask-green)
![C](https://img.shields.io/badge/Engine-C-lightgrey)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)

A full-stack, production-grade personal finance application designed to track transactions, manage monthly budgets, and simulate complex debt payoff strategies (Avalanche & Snowball) using a custom high-performance C engine.

**Live Application:** [https://finance-dash-sudarshan.web.app](https://finance-dash-sudarshan.web.app)

---

## ✨ Key Features

- **Robust Authentication:** Secure JWT-based user authentication and password hashing.
- **Financial Dashboard:** Real-time visual analytics using `Recharts` to track income vs expenses, category breakdowns, and 6-month trends.
- **Transaction & Budget Management:** Full CRUD capabilities for daily transactions, combined with automated monthly budget progress bars (safe/warning/danger thresholds).
- **Custom C-Engine Integration:** Features a standalone C program (`payoff.c`) that is dynamically compiled and invoked by the Python backend via subprocesses. It calculates complex interest amortization schedules in milliseconds.
- **Dynamic Deployments:** Cross-platform auto-compilation for the C-engine on Linux cloud environments (Render).
- **Modern UI/UX:** Built with a fully responsive, dark-themed glassmorphism design system.

---

## 🏗️ System Architecture

1. **Frontend (React.js):** Hosted on **Google Firebase**. Uses Axios interceptors for seamless JWT attachment and Context API for state management.
2. **Backend API (Flask):** Hosted on **Render**. Acts as the middleware connecting the database to the frontend, and orchestrates the C engine.
3. **Database (MySQL):** Hosted on **Railway.app**. Fully relational schema (`Users`, `Transactions`, `Categories`, `Budgets`, `Debts`, `PayoffPlans`).
4. **Computational Engine (C):** A highly optimized native binary that accepts JSON inputs, runs Snowball/Avalanche algorithms, and outputs structured JSON payoff schedules.

---

## 🛠️ Local Development Setup

### 1. Database (MySQL)
- Ensure MySQL is running on port `3306`.
- Create a database named `finance_dashboard`.

### 2. Backend (Flask)
```bash
cd backend
python -m venv venv
# Activate venv: .\venv\Scripts\activate (Windows) or source venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
```
- Create a `.env` file in the `backend` directory:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=finance_dashboard
JWT_SECRET=super_secret_key
```
- Start the server: `python app.py` (Runs on port 5000)

### 3. Frontend (React)
```bash
cd frontend
npm install
```
- Create a `.env.local` file in the `frontend` directory:
```env
REACT_APP_API_URL=http://127.0.0.1:5000/api
```
- Start the frontend: `npm start` (Runs on port 3000)

---

## 📸 Screenshots

*(Add screenshots of your Dashboard, Transactions, and Debt Payoff planner here)*

---
*Developed by Sudarshan Patil*
