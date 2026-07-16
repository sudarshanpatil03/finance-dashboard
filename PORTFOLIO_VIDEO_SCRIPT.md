# 🎥 Portfolio Demo Video Script
**Target Length:** 2.5 to 3 Minutes
**Prep before recording:**
1. Have your live URL open (`https://finance-dash-sudarshan.web.app`)
2. Have VS Code open in the background showing `payoff.c` and `app.py`.
3. Make sure you already have some transactions added so the charts look good!

---

### [0:00 - 0:30] Introduction & Architecture
*(Screen: Show the Live Login Page, then log in to show the Dashboard)*

**"Hi, my name is Sudarshan Patil, and this is my Personal Finance & Debt Payoff Dashboard.**
**I built this as a full-stack application using React for the frontend, a Python Flask API for the backend, and a MySQL database.** 

**What makes this project unique is the core financial logic—I wrote a custom C-language engine that handles the heavy mathematical calculations for debt amortization. The entire app is deployed live using Firebase, Render, and Railway."**

### [0:30 - 1:10] The Dashboard & Standard Features
*(Screen: Scroll through the Dashboard showing the charts, then click the 'Transactions' tab)*

**"Once a user logs in via JWT authentication, they are greeted by a dynamic dashboard. I used Recharts to visualize income versus expenses and 6-month trends. Data is aggregated heavily on the backend via SQLAlchemy to keep the frontend fast.**

**Users can easily add daily transactions here, which automatically updates their monthly budget progress bars. If a user exceeds their budget for a category like 'Food', the progress bar dynamically shifts from green to red."**
*(Screen: Briefly show the Budget page)*

### [1:10 - 2:00] The Technical Highlight: The C-Engine
*(Screen: Go to the 'Debts' tab. Add a quick debt, or show existing ones. Then use the slider to generate a payoff plan)*

**"The standout feature of this app is the Debt Payoff Planner. Instead of calculating complex interest logic in Python or JavaScript, I wanted maximum performance.** 

**When a user selects a strategy like 'Avalanche' or 'Snowball' and hits 'Generate', the Python API takes their debts, formats them into JSON, and uses a subprocess to execute a compiled C binary."**

*(Screen: Switch to VS Code quickly, show `payoff.c` and `debts.py`)*

**"Here in the backend code, you can see the Flask route invoking the C program. Because my server is hosted on Render which uses Linux, I wrote an auto-compilation script that detects the operating system on startup and compiles the C code directly into a native Linux binary. The C engine calculates the exact month-by-month balances and returns a JSON payload back to Python."**

### [2:00 - 2:30] Conclusion
*(Screen: Switch back to the browser showing the generated line chart in the Debts tab)*

**"The frontend then renders this beautiful line chart showing exactly when the user will be debt-free and how much interest they saved.**

**This project challenged me to integrate multiple languages, handle secure authentication, navigate complex CORS deployment issues, and design a modern glassmorphism UI. Thank you for watching."**
