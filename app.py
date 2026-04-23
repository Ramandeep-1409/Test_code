from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'eventmgmt_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db = SQLAlchemy(app)



class Admin(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Vendor(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False)   # Catering / Florist / Decoration / Lighting
    user_id  = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', backref='vendor', lazy=True, cascade='all, delete-orphan')

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_id  = db.Column(db.String(80), unique=True, nullable=False)
    orders   = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(120), nullable=False)
    price     = db.Column(db.Float, nullable=False)
    image     = db.Column(db.String(200), default='default.png')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

class CartItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)
    product    = db.relationship('Product')

class Order(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name           = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), nullable=False)
    address        = db.Column(db.String(250), nullable=False)
    city           = db.Column(db.String(80), nullable=False)
    state          = db.Column(db.String(80), nullable=False)
    pin_code       = db.Column(db.String(20), nullable=False)
    number         = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # Cash / UPI
    grand_total    = db.Column(db.Float, nullable=False)
    status         = db.Column(db.String(40), default='Received')
    items          = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    price      = db.Column(db.Float, nullable=False)
    product    = db.relationship('Product')

class RequestedItem(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    user      = db.relationship('User')



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return wrapper
    return decorator



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        uid = request.form.get('user_id', '').strip()
        pwd = request.form.get('password', '').strip()
        if not uid or not pwd:
            flash('All fields are required.', 'danger')
            return render_template('admin_login.html')
        admin = Admin.query.filter_by(user_id=uid).first()
        if admin and check_password_hash(admin.password, pwd):
            session['role'] = 'admin'
            session['uid']  = admin.id
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/maintain-user')
@login_required('admin')
def maintain_user():
    users   = User.query.all()
    vendors = Vendor.query.all()
    return render_template('maintain_user.html', users=users, vendors=vendors)

@app.route('/admin/maintain-vendor')
@login_required('admin')
def maintain_vendor():
    vendors = Vendor.query.all()
    return render_template('maintain_vendor.html', vendors=vendors)

@app.route('/admin/delete-user/<int:uid>')
@login_required('admin')
def delete_user(uid):
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('maintain_user'))

@app.route('/admin/delete-vendor/<int:vid>')
@login_required('admin')
def delete_vendor(vid):
    v = Vendor.query.get_or_404(vid)
    db.session.delete(v)
    db.session.commit()
    flash('Vendor deleted.', 'success')
    return redirect(url_for('maintain_vendor'))



@app.route('/vendor/signup', methods=['GET', 'POST'])
def vendor_signup():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        category = request.form.get('category', '').strip()
        user_id  = request.form.get('user_id', '').strip()
        if not all([name, email, password, category, user_id]):
            flash('All fields are mandatory.', 'danger')
            return render_template('vendor_signup.html')
        if Vendor.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('vendor_signup.html')
        if Vendor.query.filter_by(user_id=user_id).first():
            flash('User ID already taken.', 'danger')
            return render_template('vendor_signup.html')
        hashed = generate_password_hash(password)
        vendor = Vendor(name=name, email=email, password=hashed,
                        category=category, user_id=user_id)
        db.session.add(vendor)
        db.session.commit()
        flash('Vendor registered successfully. Please log in.', 'success')
        return redirect(url_for('vendor_login'))
    return render_template('vendor_signup.html')

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        uid = request.form.get('user_id', '').strip()
        pwd = request.form.get('password', '').strip()
        if not uid or not pwd:
            flash('All fields are required.', 'danger')
            return render_template('vendor_login.html')
        vendor = Vendor.query.filter_by(user_id=uid).first()
        if vendor and check_password_hash(vendor.password, pwd):
            session['role']      = 'vendor'
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.name
            return redirect(url_for('vendor_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
@login_required('vendor')
def vendor_dashboard():
    vendor   = Vendor.query.get(session['vendor_id'])
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('vendor_dashboard.html', vendor=vendor, products=products)

@app.route('/vendor/add-item', methods=['GET', 'POST'])
@login_required('vendor')
def add_item():
    if request.method == 'POST':
        name  = request.form.get('product_name', '').strip()
        price = request.form.get('product_price', '').strip()
        image_filename = 'default.png'

        if not name or not price:
            flash('Product name and price are required.', 'danger')
            return redirect(url_for('add_item'))

        try:
            price = float(price)
        except ValueError:
            flash('Price must be a number.', 'danger')
            return redirect(url_for('add_item'))

        file = request.files.get('product_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        product = Product(name=name, price=price, image=image_filename,
                          vendor_id=session['vendor_id'])
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully.', 'success')
        return redirect(url_for('vendor_dashboard'))
    return render_template('add_item.html')

@app.route('/vendor/update-item/<int:pid>', methods=['GET', 'POST'])
@login_required('vendor')
def update_item(pid):
    product = Product.query.get_or_404(pid)
    if product.vendor_id != session['vendor_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('vendor_dashboard'))
    if request.method == 'POST':
        product.name  = request.form.get('product_name', product.name).strip()
        try:
            product.price = float(request.form.get('product_price', product.price))
        except ValueError:
            flash('Invalid price.', 'danger')
            return redirect(url_for('update_item', pid=pid))
        file = request.files.get('product_image')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('vendor_dashboard'))
    return render_template('update_item.html', product=product)

@app.route('/vendor/delete-item/<int:pid>')
@login_required('vendor')
def delete_item(pid):
    product = Product.query.get_or_404(pid)
    if product.vendor_id != session['vendor_id']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('vendor_dashboard'))
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('vendor_dashboard'))

@app.route('/vendor/product-status')
@login_required('vendor')
def vendor_product_status():
    vendor  = Vendor.query.get(session['vendor_id'])
    orders = (db.session.query(Order)
              .join(OrderItem, Order.id == OrderItem.order_id)
              .join(Product, OrderItem.product_id == Product.id)
              .filter(Product.vendor_id == vendor.id)
              .distinct().all())
    return render_template('product_status.html', orders=orders, vendor=vendor)

@app.route('/vendor/requested-items')
@login_required('vendor')
def vendor_requested_items():
    items = RequestedItem.query.all()
    return render_template('requested_items_vendor.html', items=items)

@app.route('/vendor/update-order-status/<int:oid>', methods=['POST'])
@login_required('vendor')
def update_order_status(oid):
    order  = Order.query.get_or_404(oid)
    status = request.form.get('status')
    valid  = ['Received', 'Ready for Shipping', 'Out For Delivery']
    if status in valid:
        order.status = status
        db.session.commit()
        flash('Order status updated.', 'success')
    return redirect(url_for('vendor_product_status'))



@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user_id  = request.form.get('user_id', '').strip()
        if not all([name, email, password, user_id]):
            flash('All fields are mandatory.', 'danger')
            return render_template('user_signup.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('user_signup.html')
        if User.query.filter_by(user_id=user_id).first():
            flash('User ID already taken.', 'danger')
            return render_template('user_signup.html')
        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed, user_id=user_id)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_signup.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        uid = request.form.get('user_id', '').strip()
        pwd = request.form.get('password', '').strip()
        if not uid or not pwd:
            flash('All fields are required.', 'danger')
            return render_template('user_login.html')
        user = User.query.filter_by(user_id=uid).first()
        if user and check_password_hash(user.password, pwd):
            session['role']    = 'user'
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('user_portal'))
        flash('Invalid credentials.', 'danger')
    return render_template('user_login.html')

@app.route('/user/portal')
@login_required('user')
def user_portal():
    return render_template('user_portal.html')

@app.route('/user/vendors')
@login_required('user')
def user_vendors():
    category = request.args.get('category', '')
    if category:
        vendors = Vendor.query.filter_by(category=category).all()
    else:
        vendors = Vendor.query.all()
    categories = ['Catering', 'Florist', 'Decoration', 'Lighting']
    return render_template('vendor_page.html', vendors=vendors,
                           categories=categories, selected=category)

@app.route('/user/products/<int:vid>')
@login_required('user')
def user_products(vid):
    vendor   = Vendor.query.get_or_404(vid)
    products = Product.query.filter_by(vendor_id=vid).all()
    return render_template('products.html', vendor=vendor, products=products)

@app.route('/user/add-to-cart/<int:pid>')
@login_required('user')
def add_to_cart(pid):
    uid     = session['user_id']
    existing = CartItem.query.filter_by(user_id=uid, product_id=pid).first()
    if existing:
        existing.quantity += 1
    else:
        cart_item = CartItem(user_id=uid, product_id=pid, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash('Item added to cart.', 'success')
    return redirect(request.referrer or url_for('user_portal'))

@app.route('/user/cart')
@login_required('user')
def user_cart():
    uid   = session['user_id']
    items = CartItem.query.filter_by(user_id=uid).all()
    grand = sum(i.product.price * i.quantity for i in items)
    return render_template('cart.html', items=items, grand_total=grand)

@app.route('/user/cart/update/<int:cid>', methods=['POST'])
@login_required('user')
def update_cart(cid):
    item = CartItem.query.get_or_404(cid)
    qty  = int(request.form.get('quantity', 1))
    if qty < 1:
        db.session.delete(item)
    else:
        item.quantity = qty
    db.session.commit()
    return redirect(url_for('user_cart'))

@app.route('/user/cart/remove/<int:cid>')
@login_required('user')
def remove_cart(cid):
    item = CartItem.query.get_or_404(cid)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed.', 'success')
    return redirect(url_for('user_cart'))

@app.route('/user/cart/clear')
@login_required('user')
def clear_cart():
    CartItem.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    flash('Cart cleared.', 'success')
    return redirect(url_for('user_cart'))

@app.route('/user/checkout', methods=['GET', 'POST'])
@login_required('user')
def checkout():
    uid   = session['user_id']
    items = CartItem.query.filter_by(user_id=uid).all()
    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('user_cart'))
    grand = sum(i.product.price * i.quantity for i in items)

    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        city    = request.form.get('city', '').strip()
        state   = request.form.get('state', '').strip()
        pin     = request.form.get('pin_code', '').strip()
        number  = request.form.get('number', '').strip()
        payment = request.form.get('payment_method', '').strip()

        if not all([name, email, address, city, state, pin, number, payment]):
            flash('All fields are required.', 'danger')
            return render_template('checkout.html', items=items, grand_total=grand)

        order = Order(user_id=uid, name=name, email=email, address=address,
                      city=city, state=state, pin_code=pin, number=number,
                      payment_method=payment, grand_total=grand, status='Received')
        db.session.add(order)
        db.session.flush()

        for ci in items:
            oi = OrderItem(order_id=order.id, product_id=ci.product_id,
                           quantity=ci.quantity, price=ci.product.price)
            db.session.add(oi)

        CartItem.query.filter_by(user_id=uid).delete()
        db.session.commit()

        session['last_order_id'] = order.id
        return redirect(url_for('order_success'))

    return render_template('checkout.html', items=items, grand_total=grand)

@app.route('/user/order-success')
@login_required('user')
def order_success():
    oid   = session.get('last_order_id')
    order = Order.query.get(oid) if oid else None
    return render_template('success.html', order=order)

@app.route('/user/order-status')
@login_required('user')
def user_order_status():
    orders = Order.query.filter_by(user_id=session['user_id']).all()
    return render_template('order_status_user.html', orders=orders)

@app.route('/user/request-item', methods=['GET', 'POST'])
@login_required('user')
def request_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        if not item_name:
            flash('Item name is required.', 'danger')
            return render_template('request_item.html')
        ri = RequestedItem(user_id=session['user_id'], item_name=item_name)
        db.session.add(ri)
        db.session.commit()
        flash('Item requested successfully.', 'success')
        return redirect(url_for('user_portal'))
    return render_template('request_item.html')

@app.route('/user/guest-list')
@login_required('user')
def guest_list():
    users = User.query.all()
    return render_template('guest_list.html', users=users)



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(user_id='admin',
                          password=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: user_id='admin', password='admin123'")
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
