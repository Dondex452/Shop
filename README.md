# Shop
# Violet - Cosmetics E-Commerce Platform

## Overview
Violet is a full-featured e-commerce platform built with Flask, specifically designed for cosmetics and beauty products. The platform offers a comprehensive shopping experience with user authentication, product management, shopping cart functionality, and secure payment processing.

## Features

### User Management
- User registration and authentication
- Role-based access control (Admin/User)
- Secure password hashing
- Session management

### Product Management
- Product listing with categories
- Product search functionality
- Detailed product views
- Product reviews and ratings
- Image upload for products

### Shopping Features
- Dynamic shopping cart
- Real-time cart updates
- Product quantity management
- Wishlist functionality
- Pagination for product listings

### Checkout System
- Secure checkout process
- Multiple payment methods:
  - Stripe integration for card payments
  - Cash on Delivery (COD) option
- Order tracking
- Order confirmation emails

### Admin Dashboard
- Product management (Add/Edit/Delete)
- Category management
- User management
- Order tracking
- Sales analytics

## Technical Stack

### Backend
- Flask (Python web framework)
- SQLAlchemy (ORM)
- Flask-Login (User session management)
- Werkzeug (Password hashing)
- Stripe (Payment processing)

### Frontend
- HTML5/CSS3
- JavaScript (jQuery)
- Bootstrap 5
- Font Awesome icons
- Custom responsive design

### Database
- SQLite (Development)
- Supports easy migration to PostgreSQL/MySQL for production

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd violet-cosmetics
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export STRIPE_PUBLIC_KEY=your_stripe_public_key
export STRIPE_SECRET_KEY=your_stripe_secret_key
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Configuration

### Required Environment Variables
- `FLASK_APP`: Set to `app.py`
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Your secret key for session management
- `STRIPE_PUBLIC_KEY`: Your Stripe public key
- `STRIPE_SECRET_KEY`: Your Stripe secret key

### Database Configuration
The application uses SQLite by default. To use a different database, modify the `SQLALCHEMY_DATABASE_URI` in `config.py`.

## Project Structure
```
violet-cosmetics/
├── app.py
├── forms.py
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
├── templates/
├── instance/
├── requirements.txt
└── README.md
```

## Security Features
- Password hashing using Werkzeug
- CSRF protection
- Secure session management
- XSS prevention
- SQL injection protection through SQLAlchemy
- Secure file upload handling

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Font Awesome for icons
- Bootstrap team
- Stripe for payment processing
- Flask and SQLAlchemy communities

## Contact
Dondex Tech
okekedavid106@gmail.com
