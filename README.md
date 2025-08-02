# 💼 Coderr Backend

**Coderr** is the backend for a freelance platform, built with **Django** and **Django REST Framework (DRF)**. It provides a fully functional RESTful API that allows user registration, authentication, profile management (business and customer), offer and order handling, and a review system – all with strict role-based access control.

---

## 🔧 Features

- User registration and JWT authentication
- Business and customer profile types
- Create, manage, and delete offers
- Place and manage freelance orders
- Leave and manage reviews
- Clean and RESTful API structure
- Role-based access control

---

## 🚀 Tech Stack

- Python 3.13.1
- Django 5.2
- Django REST Framework (DRF)
- SQLite (for development)
- CORS support via `django-cors-headers`
- Nested routing with `drf-nested-routers`

---

## 📁 Project Structure

coderr/
├── user_auth_app/
├── profile_app/
├── offer_app/
├── order_app/
├── review_app/
├── core/ # API routing and settings
├── manage.py
└── db.sqlite3

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Patrick-Gogolin/coderr_backend.git
   cd coderr_backend

2. Create and activate a virtual environment

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies

    pip install -r requirements.txt

4. Apply migrations

    python manage.py migrate

5. Run the development server

    python manage.py runserver

🔑 API Endpoints

    🔐 Authentication

        POST /api/registration/ – Register a new user

        POST /api/login/ – Log in and receive JWT token
    
    👤 Profile

        GET /api/profile/{pk}/ – Retrieve a user profile

        PATCH /api/profile/{pk}/ – Update a profile

        GET /api/profiles/business/ – List all business profiles

        GET /api/profiles/customer/ – List all customer profiles
    
    💼 Offers

        GET /api/offers/ – List all offers

        POST /api/offers/ – Create a new offer
    
        GET /api/offers/{id}/ – Retrieve offer details

        PATCH /api/offers/{id}/ – Update an offer

        DELETE /api/offers/{id}/ – Delete an offer

        GET /api/offerdetails/{id}/ – Get extended offer information
    
    📦 Orders

        GET /api/orders/ – List all orders

        POST /api/orders/ – Create a new order

        PATCH /api/orders/{id}/ – Update an order

        DELETE /api/orders/{id}/ – Delete an order

        GET /api/order-count/{business_user_id}/ – Get total order count for a business user

        GET /api/completed-order-count/{business_user_id}/ – Get completed order count for a business user

    🌟 Reviews
        GET /api/reviews/ – List all reviews

        POST /api/reviews/ – Create a review

        PATCH /api/reviews/{id}/ – Update a review

        DELETE /api/reviews/{id}/ – Delete a review
    
    ℹ️ General Information

        GET /api/base-info/ – Fetch general platform information

🧪 Testing (Optional)
    
    python manage.py test

⚙️ Requirements

    asgiref==3.8.1
    Django==5.2.3
    django-cors-headers==4.7.0
    django-filter==25.1
    djangorestframework==3.16.0
    sqlparse==0.5.3
    tzdata==2025.2

📌 Notes

    SQLite is used for development; for production, consider switching to PostgreSQL or another robust database system.

    JWT authentication is implemented for secure login sessions.

    CORS is enabled, allowing communication with external frontend applications (e.g., React).

    Users can only access and manage their own data, based on their authenticated role (business or customer).

📨 Contact

    For questions or contributions, feel free to reach out or open an issue:

    Patrick Gogolin 

📄 License

    This project is licensed under the MIT License. See the LICENSE file for details.

    
    Let me know if you'd like:

    - Swagger or ReDoc API documentation setup
    - Docker support for easy deployment
    - A matching frontend `README.md` file

    I'm happy to help!