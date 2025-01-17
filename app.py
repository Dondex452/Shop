from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import current_user, login_required, UserMixin,LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, ProductForm
import os
from datetime import datetime
from math import ceil
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'szscffgsrdgdhdthdhdf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['UPLOAD_FOLDER'] = 'static/assets/goods'
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthorized users to the 'login' view

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    image = db.Column(db.String(200))
    short_note = db.Column(db.Text)  # Field for short notes


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))
    user_name = db.Column(db.String(80), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, product_id, user_name, comment):
        self.product_id = product_id
        self.user_name = user_name
        self.comment = comment

# Database Models
class Order(db.Model):
    __tablename__ = 'order'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')
    order_status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_date = db.Column(db.DateTime)
    stripe_payment_id = db.Column(db.String(200))
    
    # Shipping info
    shipping_address = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    
    # Billing info
    billing_address = db.Column(db.String(200))
    billing_city = db.Column(db.String(100))
    billing_country = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(20))

    # Relationships with cascade deletion
    billing_details = db.relationship('BillingDetails', backref='order', cascade='all, delete-orphan')
    shipping_details = db.relationship('ShippingDetails', backref='order', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class BillingDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

class ShippingDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'))
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('shop'))
        else:
            error_message = "Invalid email or password"
    return render_template('login.html', form=form, error_message=error_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.name.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        role = 'user'  # Default role for new registrations
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use another email.', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)  # Get the current page from query parameters
    per_page = 9  # Number of products to display per page
    search_query = request.args.get('search', '')  # Get search query
    category_filter = request.args.get('category', '')  # Get category filter

    # Base query for products
    query = Product.query

    # Apply search filter if search_query is provided
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    # Apply category filter if category_filter is provided
    if category_filter:
        query = query.filter(Product.category == category_filter)

    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page)
    products = pagination.items  # Get the products for the current page

    # Fetch distinct categories for the sidebar
    categories = Product.query.with_entities(Product.category).distinct()

    return render_template(
        'shop.html',
        products=products,
        pagination=pagination,
        search_query=search_query,
        categories=[category[0] for category in categories]  # Extract category names
    )


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'role' in session and session['role'] == 'admin':
        products = Product.query.all()
        users = User.query.all()
        transactions = Transaction.query.all()
        categories = [category.name for category in Category.query.all()]
        return render_template(
            'admin.html',
            products=products,
            users=users,
            transactions=transactions,
            categories=categories
        )
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))


# Delete product route
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'role' in session and session['role'] == 'admin':
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully!', 'success')
        else:
            flash('Product not found.', 'danger')
    return redirect(url_for('admin'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if 'role' in session and session['role'] == 'admin':  # Ensure the user is an admin
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            short_note = request.form.get('short_note', '')  # Optional short note
            image = request.files['image']

            if image:
                # Save the image to the correct folder
                image_path = os.path.join('assets/goods', image.filename)
                image.save(os.path.join('static', image_path))

                # Create and save the product
                product = Product(name=name, category=category, price=price, short_note=short_note, image=image_path)
                db.session.add(product)
                db.session.commit()

                flash('Product added successfully!', 'success')
            else:
                flash('Error: Image is required.', 'danger')

        except Exception as e:
            flash(f"Error adding product: {e}", 'danger')

    else:
        flash('Unauthorized access. Admins only.', 'danger')
    return redirect(url_for('admin'))


@app.route('/admin/add_category', methods=['POST'])
def add_category():
    if 'role' in session and session['role'] == 'admin':
        new_category = request.form.get('new_category').strip()
        if new_category and not Category.query.filter_by(name=new_category).first():
            category = Category(name=new_category)
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{new_category}" added successfully!', 'success')
        else:
            flash('Category already exists or is invalid.', 'danger')
    return redirect(url_for('admin'))

@app.route('/admin/delete_category/<category>', methods=['POST'])
def delete_category(category):
    if 'role' in session and session['role'] == 'admin':
        category_to_delete = Category.query.filter_by(name=category).first()
        if category_to_delete:
            db.session.delete(category_to_delete)
            db.session.commit()
            flash(f'Category "{category}" deleted successfully!', 'success')
        else:
            flash('Category not found.', 'danger')
    return redirect(url_for('admin'))




 # Add these routes to your app.py

@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if request.method == 'POST':
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        product = Product.query.get_or_404(product_id)
        
        # Convert cart dictionary keys to strings (session serialization requirement)
        cart = {str(k): v for k, v in cart.items()}
        
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': 1,
                'image': product.image
            }
        
        session['cart'] = cart
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'cart_count': sum(item['quantity'] for item in cart.values()),
                'cart_total': sum(item['price'] * item['quantity'] for item in cart.values())
            })
        
    return redirect(url_for('cart'))


@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity'))
    
    if 'cart' not in session:
        return jsonify({'success': False, 'message': 'Cart not found'}), 400
    
    cart = session['cart']
    
    if product_id not in cart:
        return jsonify({'success': False, 'message': 'Product not found in cart'}), 404
    
    if quantity <= 0:
        del cart[product_id]
    else:
        cart[product_id]['quantity'] = quantity
    
    session['cart'] = cart
    
    # Calculate new totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    tax = round(subtotal * 0.1, 2)  # 10% tax
    grand_total = subtotal + tax
    
    return jsonify({
        'success': True,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'cart_count': sum(item['quantity'] for item in cart.values())
    })

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' not in session:
        return jsonify({'success': False, 'message': 'Cart not found'}), 400
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        
        # Calculate new totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        tax = round(subtotal * 0.1, 2)  # 10% tax
        grand_total = subtotal + tax
        
        return jsonify({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values()),
            'subtotal': subtotal,
            'tax': tax,
            'grand_total': grand_total
        })
    
    return jsonify({'success': False, 'message': 'Product not found in cart'}), 404

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    page = request.args.get('page', 1, type=int)
    items_per_page = 4
    
    # Convert cart items to list and paginate
    cart_items = [{'id': k, **v} for k, v in cart.items()]
    total_items = len(cart_items)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    paginated_items = cart_items[start_idx:end_idx]
    total_pages = ceil(total_items / items_per_page)
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    tax = round(subtotal * 0.1, 2)
    grand_total = subtotal + tax
    
    return render_template(
        'cart.html',
        cart_items=paginated_items,
        cart_total=subtotal,
        tax=tax,
        grand_total=grand_total,
        current_page=page,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages
    )


class CartManager:
    @staticmethod
    def add_item(product_id, quantity=1):
        """Add or update item in cart"""
        if 'cart' not in session:
            session['cart'] = {}
            
        cart = session['cart']
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            product = Product.query.get(product_id)
            if not product:
                return False
                
            cart[product_id] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image
            }
            
        session['cart'] = cart
        return True
        
    @staticmethod
    def update_item(product_id, quantity):
        """Update item quantity in cart"""
        if 'cart' not in session:
            return False
            
        cart = session['cart']
        if product_id not in cart:
            return False
            
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
        else:
            del cart[product_id]
            
        session['cart'] = cart
        return True
        
    @staticmethod
    def remove_item(product_id):
        """Remove item from cart"""
        if 'cart' not in session:
            return False
            
        cart = session['cart']
        if product_id not in cart:
            return False
            
        del cart[product_id]
        session['cart'] = cart
        return True
        
    @staticmethod
    def get_cart_totals():
        """Calculate cart totals"""
        cart = session.get('cart', {})
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        tax = subtotal * 0.1  # 10% tax
        total = subtotal + tax
        return subtotal, tax, total

@app.before_request
def before_request():
    if 'cart' not in session:
        session['cart'] = {}   
    
# Add this context processor to make cart data available to all templates
@app.context_processor
def cart_context():
    cart = session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    return {
        'cart': cart,
        'cart_count': cart_count,
        'cart_total': cart_total
    }

from flask import g
from functools import wraps

def init_product_form():
    """Initialize product form with categories from database"""
    form = ProductForm()
    with app.app_context():
        categories = Category.query.all()
        form.category.choices = [(c.name, c.name) for c in categories]
    return form
# Example for Flask

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            # Save 'assets/media/products/image_name.png' to the database


@app.route('/add_review/<int:product_id>', methods=['POST'])
def add_review(product_id):
    if 'username' not in session:  # Check if user is logged in
        flash("Please login to add a review.", "danger")
        return redirect(url_for('login'))
        
    review_content = request.form.get('review')
    if not review_content:
        flash("Review content cannot be empty.", "danger")
        return redirect(url_for('product_detail', product_id=product_id))

    review = Review(
        product_id=product_id,
        user_name=session['username'],  # Use username from session instead of current_user
        comment=review_content
    )
    db.session.add(review)
    db.session.commit()
    flash("Review added successfully!", "success")
    return redirect(url_for('product_detail', product_id=product_id))


@app.route('/product_detail/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # Pagination setup
    page = request.args.get('page', 1, type=int)  # Default to page 1 if not provided
    reviews_per_page = 4  # Number of reviews per page

    # Paginate reviews
    reviews_paginated = Review.query.filter_by(product_id=product_id).paginate(
        page=page, per_page=reviews_per_page, error_out=False
    )

    return render_template(
        'product_detail.html',
        product=product,
        reviews=reviews_paginated.items,  # Paginated review items
        pagination=reviews_paginated       # Full pagination object
    )



@app.route('/delete_review/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    if 'username' not in session:  # Check if user is logged in
        return {"error": "Please login first"}, 401
        
    review = Review.query.get_or_404(review_id)

    if review.user_name != session['username']:  # Check if review belongs to logged in user
        return {"error": "Unauthorized"}, 403

    db.session.delete(review)
    db.session.commit()
    return {"message": "Review deleted successfully"}, 200


from flask import jsonify, redirect, url_for
from datetime import datetime
import stripe  # You'll need to pip install stripe

# Add these configurations to your Flask app
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51QgMvoPRBjc9OqRgzsPODzi2HI4363j2KfXZdnvinabBznfIl0pwNvzYHQE9SVUz07M0yVjhrNzWAWjY2GosL46B001HINsFea'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51QgMvoPRBjc9OqRgzKXxjIV3rbQpqBqDRY6sT7zQmMhSBxItRabxUeCBLzVb5mrim9b3wUdBzkcrQ2FCIzkEbLRM00ZcTa5N9E'
stripe.api_key = app.config['STRIPE_SECRET_KEY']




@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart = session.get('cart', {})
        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('cart'))

        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        tax = round(subtotal * 0.1, 2)
        shipping_fee = 10.00
        grand_total = subtotal + tax + shipping_fee

        try:
            # Create order with full shipping and billing information
            order = Order(
                user_id=current_user.id,
                total_amount=grand_total,
                payment_method=request.form.get('payment_method'),
                shipping_address=f"{request.form.get('house_address')} {request.form.get('apartment_address', '')}".strip(),
                shipping_city=request.form.get('state'),
                shipping_country=request.form.get('country'),
                shipping_postal_code=request.form.get('postal_code'),
                billing_address=f"{request.form.get('billing_house_address')} {request.form.get('billing_apartment_address', '')}".strip(),
                billing_city=request.form.get('billing_state'),
                billing_country=request.form.get('billing_country'),
                billing_postal_code=request.form.get('billing_postal_code')
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID without committing

            # Create complete billing details
            billing_details = BillingDetails(
                order_id=order.id,
                full_name=f"{request.form.get('billing_first_name')} {request.form.get('billing_last_name')}",
                email=request.form.get('billing_email'),
                address=f"{request.form.get('billing_house_address')} {request.form.get('billing_apartment_address', '')}".strip(),
                city=request.form.get('billing_state'),
                postal_code=request.form.get('billing_postal_code'),
                country=request.form.get('billing_country')
            )
            db.session.add(billing_details)

            # Create complete shipping details
            shipping_details = ShippingDetails(
                order_id=order.id,
                full_name=f"{request.form.get('first_name')} {request.form.get('last_name')}",
                address=f"{request.form.get('house_address')} {request.form.get('apartment_address', '')}".strip(),
                city=request.form.get('state'),
                postal_code=request.form.get('postal_code'),
                country=request.form.get('country')
            )
            db.session.add(shipping_details)

            # Save all order items with complete information
            for product_id, item in cart.items():
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=int(product_id),
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_item)

            if request.form.get('payment_method') == 'Card':
                order.payment_status = 'awaiting_payment'
                order.order_status = 'pending'
                try:
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(grand_total * 100),
                                'product_data': {
                                    'name': f'Order #{order.id}',
                                },
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=url_for('payment_success', order_id=order.id, _external=True),
                        cancel_url=url_for('payment_cancel', order_id=order.id, _external=True),
                    )
                    order.stripe_payment_id = checkout_session.id
                    db.session.commit()
                    return redirect(checkout_session.url)
                except Exception as e:
                    db.session.rollback()
                    print(f"Stripe error: {str(e)}")
                    flash('Error processing card payment', 'error')
                    return redirect(url_for('checkout'))
            
            elif request.form.get('payment_method') == 'COD':
                order.payment_status = 'pending'
                order.order_status = 'processing'
                db.session.commit()
                session.pop('cart', None)  # Clear the cart after successful order
                flash('Order placed successfully! You will pay on delivery.', 'success')
                return redirect(url_for('order_confirmation', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            flash('Error processing order', 'error')
            return redirect(url_for('checkout'))

    # Rest of the GET request handling remains the same
    cart = session.get('cart', {})
    cart_items = []
    
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            cart_items.append({
                'id': product_id,
                'name': product.name,
                'price': item['price'],
                'quantity': item['quantity'],
                'total': item['price'] * item['quantity'],
                'image': product.image
            })

    subtotal = sum(item['total'] for item in cart_items)
    tax = round(subtotal * 0.1, 2)
    shipping_fee = 10.00
    grand_total = subtotal + tax + shipping_fee

    return render_template(
        'checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        grand_total=grand_total,
        stripe_public_key=app.config['STRIPE_PUBLIC_KEY']
    )


@app.route('/payment/success/<int:order_id>')
@login_required
def payment_success(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Verify order belongs to current user
        if order.user_id != current_user.id:
            flash('Unauthorized access', 'error')
            return redirect(url_for('shop'))
        
        # Verify payment with Stripe
        if order.stripe_payment_id:
            session_data = stripe.checkout.Session.retrieve(order.stripe_payment_id)
            if session_data.payment_status == 'paid':
                order.payment_status = 'completed'
                order.order_status = 'processing'
                order.payment_date = datetime.utcnow()
                db.session.commit()
                
                # Clear cart after successful payment
                session.pop('cart', None)
                
                flash('Payment successful! Your order has been confirmed.', 'success')
                return redirect(url_for('order_confirmation', order_id=order.id))
        
        flash('Payment verification failed', 'error')
        return redirect(url_for('checkout'))
            
    except Exception as e:
        print(f"Payment success error: {str(e)}")
        flash('Error processing payment', 'error')
        return redirect(url_for('checkout'))


@app.route('/payment/cancel/<int:order_id>')
@login_required
def payment_cancel(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Verify order belongs to current user
        if order.user_id != session['user_id']:
            flash('Unauthorized access', 'error')
            return redirect(url_for('index'))
            
        order.payment_status = 'cancelled'
        order.order_status = 'cancelled'
        db.session.commit()
        flash('Payment was cancelled.', 'error')
        return redirect(url_for('checkout'))
        
    except Exception as e:
        flash('Error cancelling order', 'error')
        return redirect(url_for('checkout'))

@app.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Verify order belongs to current user
        if order.user_id != session['user_id']:
            flash('Unauthorized access', 'error')
            return redirect(url_for('index'))
            
        return render_template('order_confirmation.html', order=order)
        
    except Exception as e:
        flash('Error displaying order', 'error')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route("/index")
def index():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template("about.html")

def seed_categories():
    initial_categories = ['Perfume', 'Skin Care', 'Makeup']
    for category_name in initial_categories:
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name)
            db.session.add(category)
    db.session.commit()

# Initialize the Database and Seed Categories
with app.app_context():
    db.create_all()
    seed_categories()


if __name__ == '__main__':
    app.run(debug=True)