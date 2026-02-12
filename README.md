 # 📚 Library Management System

A simple and efficient **Library Management System** built using **Django**.  
This project allows an admin to manage members, books, book lending, and returns through an easy-to-use dashboard.

Developed by **Mantavya Kumar**

---

## 🚀 Features

- Admin Login Authentication
- Add and Manage Members
- Add and Manage Books
- Issue (Lend) Books to Members
- Return Books
- Dashboard Statistics
  - Total Members
  - Total Books
  - Borrowed Books
  - Total Collection Amount
- Recently Added Books Display

---

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

Library-Management-System-Django/
│
├── core/ # Project settings
├── library/ # Main app (models, views, urls)
├── templates/ # HTML templates
├── static/ # CSS & JS files
├── manage.py
└── requirements.txt


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Mantavyakumar/Library-management-system.git
cd Library-management-system
2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Migrations
python manage.py migrate
5️⃣ Start Server
python manage.py runserver
Open browser:

http://127.0.0.1:8000/
🔐 Admin Login
Create admin user:

python manage.py createsuperuser
Then login at:

http://127.0.0.1:8000/admin/
📸 Screenshots
Dashboard View
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/da4a7c00-ca62-410d-9267-6fdfb4fa3dac" />

Add Member

Add Book

Lending Books

Payments Overview

✅ Future Improvements
Automatic fine calculation

Book search & filters

Member borrowing history

Email notifications

👨‍💻 Author
Mantavya Kumar
