# 🏔️ TrekAnnex — Smart Trek Booking System

A full-featured web application for discovering and booking treks in Nepal, powered by an AI/ML recommendation engine and a role-based admin panel.

---

## ✨ Features

### 👤 User Side
- **Home** — Featured treks with smart homepage recommendations
- **Smart Trek Finder** — AI-powered trek matching using TF-IDF & cosine similarity
- **Explore** — Browse all treks with advanced filters (region, difficulty, duration, budget)
- **Booking System** — Book treks with guide selection and eSewa payment integration
- **Authentication** — Secure register/login with strong password validation
- **Profile Management** — Edit personal info and change password
- **Guides Directory** — Browse available guides with filters

### 🛠️ Admin Panel (Role-Based)

| Role | Capabilities |
|------|-------------|
| **SuperAdmin** | Full access — manage treks, bookings, guides, admins, users |
| **Admin** | Manage treks, bookings, guides; view users |
| **Guide** | View & manage assigned bookings; manage own profile |

---

## 🧠 Smart Trek Finder (AI/ML)

Uses **TF-IDF vectorization** and **cosine similarity** to match user preferences with trek profiles based on:

- Budget range & duration
- Altitude & difficulty level
- Region & best season
- Interests: scenic, adventure, photography, wildlife, cultural, family-friendly

Returns top 5 matching treks with a match score ≥ 3%.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2 |
| Frontend | HTML, CSS, Bootstrap 5, JavaScript |
| Database | SQLite |
| ML | scikit-learn (TF-IDF, Cosine Similarity) |
| Rich Text | django-ckeditor |
| Images | Pillow |
| Payment | eSewa (test environment) |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/TrekAnnex-Smart-Trek-Booking-System.git
cd TrekAnnex-Smart-Trek-Booking-System
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create SuperAdmin
```bash
python create_superadmin.py
```
> Default credentials — Username: `superadmin` | Password: `Macbook@M1`

### 6. Run the server
```bash
python manage.py runserver
```

### 7. Access the app
| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | User site |
| http://127.0.0.1:8000/admin-login/ | Admin panel |

---

## 📁 Project Structure

```
TrekAnnex/
├── accounts/          # User auth & custom user model
├── treks/             # Trek listings & management
├── bookings/          # Booking system & eSewa payment
├── guides/            # Guide profiles & management
├── recommendation/    # AI/ML recommendation engine
├── templates/
│   ├── user/          # User-facing templates
│   ├── admin_panel/   # Admin panel templates
│   └── auth/          # Login & register templates
├── static/            # CSS, JS, images
├── trek_annex/        # Django project settings
├── manage.py
└── requirements.txt
```

---

## 🔐 Security

- CSRF protection on all forms
- Password hashing (Django default)
- Role-based view restrictions with decorators
- Strong password policy enforced on all accounts
- Unique username & email validation

### Password Requirements
All passwords must have: 8+ characters, uppercase, lowercase, number, and special character.

---

## 📸 Screenshots

> _Add screenshots here after deployment_

---

## 🔮 Future Enhancements

- [ ] Payment gateway (live eSewa / Khalti)
- [ ] Email notifications for bookings
- [ ] Trek reviews & ratings
- [ ] Analytics dashboard
- [ ] Multi-language support (Nepali/English)

---

## 📄 License

This project is built for educational purposes as a college project.

---

## 📬 Contact

For queries: mail@trekbooking.com
