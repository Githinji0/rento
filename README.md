 Rent Management System (Rento App)

> A modern, SaaS-inspired **Rent Management System** built with **Python + PySide6 + SQLite**
> Designed for landlords, property managers, and real-world business use 💼

---

## 🚀 Overview

This is a **full-featured desktop application** that helps manage:

* 🏢 Properties
* 🏘️ Units
* 👤 Tenants
* 💰 Rent Payments
* 📊 Analytics Dashboard
* 🔐 Authentication & Roles

Built with a **clean SaaS UI**, this project demonstrates **real-world software engineering practices**.

---
##screenshots
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/5105c9c2-d416-4175-a641-a2ec318667a7" />

<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/bcd68820-17df-49ea-bb7b-698b89b5ee2f" />



## ✨ Features

### 🔐 Authentication System

* User registration & login
* Secure password hashing
* Session management
* Logout functionality
* Role-based access (Admin / Staff)

---

### 🏢 Property Management

* Add / Edit / Delete properties
* Store address & details
* Scalable multi-property system

---

### 🏘️ Units Management

* Assign units to properties
* Track rent amount
* Occupancy status (Vacant / Occupied)

---

### 👤 Tenant Management

* Assign tenants to units
* Store contact details
* Track move-in dates & deposits

---

### 💰 Payments System

* Record rent payments
* Track monthly payments
* Calculate arrears ⚠️
* Payment history

---

### 📊 Dashboard Analytics

* Total properties
* Occupied vs vacant units
* Total tenants
* Total income 💰
* Arrears summary ⚠️

---

### 🎨 Modern SaaS UI

* Sidebar navigation
* Card-based dashboard
* Clean, professional layout

---

## 🛠️ Tech Stack

* **Frontend (Desktop UI):** PySide6 (Qt for Python)
* **Backend Logic:** Python
* **Database:** SQLite
* **Architecture:** Modular (UI + Core + Database)
* **Packaging:** PyInstaller

---



## ⚙️ Installation

### 1️⃣ Clone the repository

```
git clone https://github.com/yourusername/rent-management-system.git
cd rent-management-system
```

---

### 2️⃣ Create virtual environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install dependencies

```
pip install PySide6
```

---

### 4️⃣ Run the app

```
python main.py
```

---

## 📦 Build Executable (Windows)

```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Output:

```
dist/main.exe
```

---

## 🔐 Default Roles

| Role  | Access                                    |
| ----- | ----------------------------------------- |
| Admin | Full system                               |
| Staff | Limited (no delete / restricted features) |

---

## 🧠 Key Concepts Demonstrated

* Desktop app architecture (MVC-style)
* CRUD operations with SQLite
* Authentication & session handling
* Role-based authorization
* UI/UX design (SaaS-inspired)
* Modular scalable code structure

---

## 🔥 Future Improvements

* 📊 Charts & data visualization
* 🧾 PDF receipts generation
* ☁️ Cloud sync (multi-device)
* 🔐 Password reset system
* 👥 Multi-tenant system
* 🌐 Web version (Django + React)

---

## 💼 Real-World Use

This project can be used as:

* A **portfolio project** ⭐
* A **commercial desktop app** 💰
* A **startup MVP** 🚀
* A base for a **SaaS platform**

---

## 👨‍💻 Author

**Githinji William**
💻 Developer | UI/UX Enthusiast | SaaS Builder

---

## ⭐ Support

If you like this project:

⭐ Star the repo
🍴 Fork it
🚀 Build on top of it

---

## 📜 License

MIT License — Free to use and modify

---

