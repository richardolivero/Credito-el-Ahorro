import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import csv

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui-cambiala'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==================== MODELOS DE BASE DE DATOS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' o 'vendedor'
    vehicle_type = db.Column(db.String(20))  # 'propio' o 'empresa' (solo para vendedores)
    active = db.Column(db.Boolean, default=True)
    
    # Relaciones
    sales = db.relationship('Sale', backref='seller', lazy=True)
    collections = db.relationship('Collection', backref='collector', lazy=True)
    location_updates = db.relationship('LocationUpdate', backref='user', lazy=True)
    
    # Propiedades calculadas para el día actual
    @property
    def daily_revenue(self):
        today = datetime.now().date()
        sales_revenue = db.session.query(db.func.sum(Sale.total)).filter(
            Sale.seller_id == self.id,
            Sale.sale_type == 'contado',
            db.func.date(Sale.created_at) == today
        ).scalar() or 0
        
        collections_revenue = db.session.query(db.func.sum(Collection.amount)).filter(
            Collection.collector_id == self.id,
            db.func.date(Collection.collection_date) == today
        ).scalar() or 0
        
        return sales_revenue + collections_revenue
    
    @property
    def daily_commission(self):
        rate = 0.30 if self.vehicle_type == 'propio' else 0.15
        return self.daily_revenue * rate
    
    @property
    def daily_bonus_savings(self):
        return self.daily_commission * 0.01
    
    @property
    def total_bonus_accumulated(self):
        # Calcular acumulado histórico de aguinaldo
        total = 0
        for sale in self.sales:
            if sale.sale_type == 'contado':
                commission = sale.total * (0.30 if self.vehicle_type == 'propio' else 0.15)
                total += commission * 0.01
        for collection in self.collections:
            commission = collection.amount * (0.30 if self.vehicle_type == 'propio' else 0.15)
            total += commission * 0.01
        return total


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Debe ser cost * 3
    stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
    inventory_movements = db.relationship('InventoryMovement', backref='product', lazy=True)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    discount_percent = db.Column(db.Float, default=0)  # Descuento especial para cliente frecuente
    balance = db.Column(db.Float, default=0)  # Saldo pendiente por crédito
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    sales = db.relationship('Sale', backref='customer', lazy=True)
    collections = db.relationship('Collection', backref='customer', lazy=True)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sale_type = db.Column(db.String(20), nullable=False)  # 'contado' o 'credito'
    subtotal = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    items = db.relationship('SaleItem', backref='sale', lazy=True)


class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))  # Venta relacionada
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20))  # 'efectivo', 'transferencia', etc.
    notes = db.Column(db.Text)
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)


class InventoryMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'entrada' o 'salida'
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LocationUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== RUTAS ====================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('seller_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.active:
                flash('Usuario inactivo. Contacte al administrador.', 'error')
                return redirect(url_for('login'))
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    sellers = User.query.filter_by(role='vendedor', active=True).all()
    products_low_stock = Product.query.filter(Product.stock <= Product.min_stock).all()
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(10).all()
    recent_collections = Collection.query.order_by(Collection.collection_date.desc()).limit(10).all()
    
    # Totales del día
    today = datetime.now().date()
    total_revenue_today = db.session.query(db.func.sum(Sale.total)).filter(
        Sale.sale_type == 'contado',
        db.func.date(Sale.created_at) == today
    ).scalar() or 0
    
    total_collections_today = db.session.query(db.func.sum(Collection.amount)).filter(
        db.func.date(Collection.collection_date) == today
    ).scalar() or 0
    
    total_today = total_revenue_today + total_collections_today
    
    return render_template('admin/dashboard.html',
                         sellers=sellers,
                         products_low_stock=products_low_stock,
                         recent_sales=recent_sales,
                         recent_collections=recent_collections,
                         total_today=total_today)


@app.route('/admin/sellers')
@login_required
def admin_sellers():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    sellers = User.query.filter_by(role='vendedor').all()
    return render_template('admin/sellers.html', sellers=sellers)


@app.route('/admin/sellers/add', methods=['GET', 'POST'])
@login_required
def admin_add_seller():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        vehicle_type = request.form.get('vehicle_type')
        
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'error')
            return redirect(url_for('admin_add_seller'))
        
        new_seller = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='vendedor',
            vehicle_type=vehicle_type
        )
        db.session.add(new_seller)
        db.session.commit()
        flash('Vendedor creado exitosamente', 'success')
        return redirect(url_for('admin_sellers'))
    
    return render_template('admin/seller_form.html')


@app.route('/admin/sellers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_seller(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    seller = User.query.get_or_404(id)
    
    if request.method == 'POST':
        seller.vehicle_type = request.form.get('vehicle_type')
        seller.active = request.form.get('active') == 'on'
        
        if request.form.get('password'):
            seller.password_hash = generate_password_hash(request.form.get('password'))
        
        db.session.commit()
        flash('Vendedor actualizado exitosamente', 'success')
        return redirect(url_for('admin_sellers'))
    
    return render_template('admin/seller_form.html', seller=seller)


@app.route('/admin/products')
@login_required
def admin_products():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        cost = float(request.form.get('cost'))
        price = cost * 3  # Regla 3x1
        stock = int(request.form.get('stock', 0))
        min_stock = int(request.form.get('min_stock', 10))
        
        product = Product(name=name, cost=cost, price=price, stock=stock, min_stock=min_stock)
        db.session.add(product)
        
        # Registrar movimiento de entrada inicial
        if stock > 0:
            movement = InventoryMovement(
                product_id=product.id,
                movement_type='entrada',
                quantity=stock,
                reason='Stock inicial'
            )
            db.session.add(movement)
        
        db.session.commit()
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html')


@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.cost = float(request.form.get('cost'))
        product.price = product.cost * 3  # Regla 3x1
        old_stock = product.stock
        product.stock = int(request.form.get('stock', 0))
        product.min_stock = int(request.form.get('min_stock', 10))
        
        # Registrar movimiento si cambió el stock
        if product.stock != old_stock:
            diff = product.stock - old_stock
            movement_type = 'entrada' if diff > 0 else 'salida'
            movement = InventoryMovement(
                product_id=product.id,
                movement_type=movement_type,
                quantity=abs(diff),
                reason='Ajuste de inventario'
            )
            db.session.add(movement)
        
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=product)


@app.route('/admin/customers')
@login_required
def admin_customers():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    customers = Customer.query.all()
    return render_template('admin/customers.html', customers=customers)


@app.route('/admin/customers/add', methods=['GET', 'POST'])
@login_required
def admin_add_customer():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        discount_percent = float(request.form.get('discount_percent', 0))
        
        customer = Customer(name=name, phone=phone, address=address, discount_percent=discount_percent)
        db.session.add(customer)
        db.session.commit()
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('admin_customers'))
    
    return render_template('admin/customer_form.html')


@app.route('/admin/finance')
@login_required
def admin_finance():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    # Obtener parámetros de fecha
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query_sales = Sale.query.filter(Sale.sale_type == 'contado')
    query_collections = Collection.query
    
    if start_date:
        query_sales = query_sales.filter(Sale.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        query_collections = query_collections.filter(Collection.collection_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query_sales = query_sales.filter(Sale.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        query_collections = query_collections.filter(Collection.collection_date <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    
    sales = query_sales.all()
    collections = query_collections.all()
    
    total_sales = sum(s.total for s in sales)
    total_collections = sum(c.amount for c in collections)
    total_income = total_sales + total_collections
    
    # Calcular comisiones pagadas
    total_commissions = 0
    for seller in User.query.filter_by(role='vendedor').all():
        # Comisiones basadas en lo recaudado en el período
        seller_sales = [s for s in sales if s.seller_id == seller.id]
        seller_collections = [c for c in collections if c.collector_id == seller.id]
        
        revenue = sum(s.total for s in seller_sales) + sum(c.amount for c in seller_collections)
        rate = 0.30 if seller.vehicle_type == 'propio' else 0.15
        total_commissions += revenue * rate
    
    return render_template('admin/finance.html',
                         sales=sales,
                         collections=collections,
                         total_sales=total_sales,
                         total_collections=total_collections,
                         total_income=total_income,
                         total_commissions=total_commissions,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/admin/map')
@login_required
def admin_map():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    sellers = User.query.filter_by(role='vendedor', active=True).all()
    return render_template('admin/map.html', sellers=sellers)


@app.route('/admin/reports')
@login_required
def admin_reports():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    report_type = request.args.get('type', 'sales')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if report_type == 'sales':
        data = Sale.query
        if start_date:
            data = data.filter(Sale.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            data = data.filter(Sale.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        data = data.all()
        
    elif report_type == 'collections':
        data = Collection.query
        if start_date:
            data = data.filter(Collection.collection_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            data = data.filter(Collection.collection_date <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        data = data.all()
        
    elif report_type == 'inventory':
        data = Product.query.all()
        
    elif report_type == 'commissions':
        sellers = User.query.filter_by(role='vendedor').all()
        data = []
        for seller in sellers:
            seller_sales = Sale.query.filter(
                Sale.seller_id == seller.id,
                Sale.sale_type == 'contado'
            )
            seller_collections = Collection.query.filter(
                Collection.collector_id == seller.id
            )
            if start_date:
                seller_sales = seller_sales.filter(Sale.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
                seller_collections = seller_collections.filter(Collection.collection_date >= datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                seller_sales = seller_sales.filter(Sale.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
                seller_collections = seller_collections.filter(Collection.collection_date <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
            
            sales_total = sum(s.total for s in seller_sales.all())
            collections_total = sum(c.amount for c in seller_collections.all())
            revenue = sales_total + collections_total
            rate = 0.30 if seller.vehicle_type == 'propio' else 0.15
            commission = revenue * rate
            bonus = commission * 0.01
            
            data.append({
                'seller': seller,
                'revenue': revenue,
                'commission': commission,
                'bonus': bonus
            })
    
    return render_template('admin/reports.html', data=data, report_type=report_type, start_date=start_date, end_date=end_date)


@app.route('/admin/export/<report_type>')
@login_required
def admin_export(report_type):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    output = BytesIO()
    writer = csv.writer(output)
    
    if report_type == 'sales':
        writer.writerow(['ID', 'Cliente', 'Vendedor', 'Tipo', 'Subtotal', 'Descuento', 'Total', 'Fecha'])
        query = Sale.query
        if start_date:
            query = query.filter(Sale.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Sale.created_at <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        for item in query.all():
            writer.writerow([item.id, item.customer.name, item.seller.username, item.sale_type, 
                           item.subtotal, item.discount, item.total, item.created_at.strftime('%Y-%m-%d %H:%M')])
    
    elif report_type == 'collections':
        writer.writerow(['ID', 'Cliente', 'Cobrador', 'Monto', 'Método', 'Fecha'])
        query = Collection.query
        if start_date:
            query = query.filter(Collection.collection_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Collection.collection_date <= datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
        for item in query.all():
            writer.writerow([item.id, item.customer.name, item.collector.username, 
                           item.amount, item.payment_method, item.collection_date.strftime('%Y-%m-%d %H:%M')])
    
    elif report_type == 'inventory':
        writer.writerow(['ID', 'Producto', 'Costo', 'Precio Venta', 'Stock', 'Stock Mínimo'])
        for item in Product.query.all():
            writer.writerow([item.id, item.name, item.cost, item.price, item.stock, item.min_stock])
    
    elif report_type == 'commissions':
        writer.writerow(['Vendedor', 'Recaudado', 'Comisión', 'Aguinaldo Acumulado'])
        for seller in User.query.filter_by(role='vendedor').all():
            revenue = seller.daily_revenue
            commission = seller.daily_commission
            bonus = seller.total_bonus_accumulated
            writer.writerow([seller.username, revenue, commission, bonus])
    
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'{report_type}_report.csv')


# ==================== SELLER ROUTES ====================

@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if current_user.role != 'vendedor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    today = datetime.now().date()
    sales_today = Sale.query.filter(
        Sale.seller_id == current_user.id,
        db.func.date(Sale.created_at) == today
    ).all()
    
    collections_today = Collection.query.filter(
        Collection.collector_id == current_user.id,
        db.func.date(Collection.collection_date) == today
    ).all()
    
    # Clientes con saldo pendiente
    customers_with_balance = Customer.query.filter(Customer.balance > 0).all()
    
    return render_template('seller/dashboard.html',
                         sales_today=sales_today,
                         collections_today=collections_today,
                         customers_with_balance=customers_with_balance)


@app.route('/seller/sale/new', methods=['GET', 'POST'])
@login_required
def seller_new_sale():
    if current_user.role != 'vendedor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        sale_type = request.form.get('sale_type')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Obtener productos y cantidades del formulario
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        # Calcular totales
        subtotal = 0
        items_data = []
        
        for i, product_id in enumerate(product_ids):
            product = Product.query.get(int(product_id))
            quantity = int(quantities[i])
            
            if product.stock < quantity:
                flash(f'Stock insuficiente para {product.name}', 'error')
                return redirect(url_for('seller_new_sale'))
            
            total_item = product.price * quantity
            subtotal += total_item
            items_data.append({
                'product': product,
                'quantity': quantity,
                'unit_price': product.price,
                'total': total_item
            })
        
        # Aplicar descuento del cliente si existe
        customer = Customer.query.get(customer_id)
        discount = customer.discount_percent if customer else 0
        
        # Descuento manual adicional (si el vendedor tiene permiso)
        manual_discount = float(request.form.get('manual_discount', 0))
        discount += manual_discount
        
        total = subtotal * (1 - discount / 100)
        
        # Crear venta
        sale = Sale(
            customer_id=customer_id,
            seller_id=current_user.id,
            sale_type=sale_type,
            subtotal=subtotal,
            discount=discount,
            total=total,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None
        )
        db.session.add(sale)
        db.session.flush()  # Para obtener el ID de la venta
        
        # Crear items de la venta y actualizar stock
        for item_data in items_data:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total=item_data['total']
            )
            db.session.add(sale_item)
            
            # Actualizar stock
            item_data['product'].stock -= item_data['quantity']
            
            # Registrar movimiento de salida
            movement = InventoryMovement(
                product_id=item_data['product'].id,
                movement_type='salida',
                quantity=item_data['quantity'],
                reason=f'Venta #{sale.id}'
            )
            db.session.add(movement)
        
        # Si es crédito, actualizar saldo del cliente
        if sale_type == 'credito':
            customer.balance += total
        
        db.session.commit()
        flash('Venta registrada exitosamente', 'success')
        return redirect(url_for('seller_dashboard'))
    
    customers = Customer.query.all()
    products = Product.query.filter(Product.stock > 0).all()
    return render_template('seller/sale_form.html', customers=customers, products=products)


@app.route('/seller/collection/new', methods=['GET', 'POST'])
@login_required
def seller_new_collection():
    if current_user.role != 'vendedor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        sale_id = request.form.get('sale_id')
        amount = float(request.form.get('amount'))
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes')
        
        customer = Customer.query.get(customer_id)
        
        if customer.balance < amount:
            flash('El monto excede el saldo pendiente del cliente', 'error')
            return redirect(url_for('seller_new_collection'))
        
        # Registrar cobro
        collection = Collection(
            customer_id=customer_id,
            collector_id=current_user.id,
            sale_id=int(sale_id) if sale_id else None,
            amount=amount,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(collection)
        
        # Actualizar saldo del cliente
        customer.balance -= amount
        
        db.session.commit()
        flash('Cobro registrado exitosamente', 'success')
        return redirect(url_for('seller_dashboard'))
    
    customers_with_balance = Customer.query.filter(Customer.balance > 0).all()
    return render_template('seller/collection_form.html', customers_with_balance=customers_with_balance)


@app.route('/seller/my-commissions')
@login_required
def seller_commissions():
    if current_user.role != 'vendedor':
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    today = datetime.now().date()
    
    # Historial de ventas y cobros
    sales = Sale.query.filter_by(seller_id=current_user.id).order_by(Sale.created_at.desc()).all()
    collections = Collection.query.filter_by(collector_id=current_user.id).order_by(Collection.collection_date.desc()).all()
    
    return render_template('seller/commissions.html',
                         daily_revenue=current_user.daily_revenue,
                         daily_commission=current_user.daily_commission,
                         daily_bonus=current_user.daily_bonus_savings,
                         total_bonus=current_user.total_bonus_accumulated,
                         sales=sales,
                         collections=collections)


@app.route('/seller/update-location', methods=['POST'])
@login_required
def seller_update_location():
    if current_user.role != 'vendedor':
        return jsonify({'error': 'Acceso denegado'}), 403
    
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude and longitude:
        location = LocationUpdate(
            user_id=current_user.id,
            latitude=float(latitude),
            longitude=float(longitude)
        )
        db.session.add(location)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'Datos inválidos'}), 400


# ==================== API ENDPOINTS ====================

@app.route('/api/sellers/locations')
@login_required
def api_seller_locations():
    if current_user.role != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    
    sellers = User.query.filter_by(role='vendedor', active=True).all()
    result = []
    
    for seller in sellers:
        # Obtener última ubicación
        last_location = LocationUpdate.query.filter_by(user_id=seller.id).order_by(LocationUpdate.timestamp.desc()).first()
        
        # Obtener estadísticas del día
        today = datetime.now().date()
        sales_revenue = db.session.query(db.func.sum(Sale.total)).filter(
            Sale.seller_id == seller.id,
            Sale.sale_type == 'contado',
            db.func.date(Sale.created_at) == today
        ).scalar() or 0
        
        collections_revenue = db.session.query(db.func.sum(Collection.amount)).filter(
            Collection.collector_id == seller.id,
            db.func.date(Collection.collection_date) == today
        ).scalar() or 0
        
        total_revenue = sales_revenue + collections_revenue
        commission_rate = 0.30 if seller.vehicle_type == 'propio' else 0.15
        commission = total_revenue * commission_rate
        
        result.append({
            'id': seller.id,
            'username': seller.username,
            'vehicle_type': seller.vehicle_type,
            'latitude': last_location.latitude if last_location else None,
            'longitude': last_location.longitude if last_location else None,
            'timestamp': last_location.timestamp.isoformat() if last_location else None,
            'daily_revenue': total_revenue,
            'daily_commission': commission
        })
    
    return jsonify(result)


@app.route('/api/products')
@login_required
def api_products():
    products = Product.query.filter(Product.stock > 0).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'stock': p.stock
    } for p in products])


# ==================== INICIALIZACIÓN ====================

def create_sample_data():
    """Crear datos de ejemplo para pruebas"""
    
    # Administrador por defecto
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        print("Administrador creado: admin / admin123")
    
    # Vendedor de ejemplo
    seller = User.query.filter_by(username='vendedor1').first()
    if not seller:
        seller = User(
            username='vendedor1',
            password_hash=generate_password_hash('vendedor123'),
            role='vendedor',
            vehicle_type='propio'
        )
        db.session.add(seller)
        print("Vendedor creado: vendedor1 / vendedor123")
    
    # Productos de ejemplo
    if Product.query.count() == 0:
        products_data = [
            {'name': 'Producto A', 'cost': 10, 'stock': 100, 'min_stock': 20},
            {'name': 'Producto B', 'cost': 15, 'stock': 50, 'min_stock': 10},
            {'name': 'Producto C', 'cost': 20, 'stock': 75, 'min_stock': 15},
        ]
        for prod_data in products_data:
            product = Product(
                name=prod_data['name'],
                cost=prod_data['cost'],
                price=prod_data['cost'] * 3,
                stock=prod_data['stock'],
                min_stock=prod_data['min_stock']
            )
            db.session.add(product)
            db.session.flush()  # Obtener ID del producto
            
            # Registrar movimiento de entrada
            movement = InventoryMovement(
                product_id=product.id,
                movement_type='entrada',
                quantity=product.stock,
                reason='Stock inicial'
            )
            db.session.add(movement)
        print("Productos de ejemplo creados")
    
    # Clientes de ejemplo
    if Customer.query.count() == 0:
        customers = [
            Customer(name='Cliente Frecuente 1', phone='555-0001', address='Dirección 1', discount_percent=5, balance=0),
            Customer(name='Cliente Frecuente 2', phone='555-0002', address='Dirección 2', discount_percent=10, balance=150),
            Customer(name='Cliente Normal', phone='555-0003', address='Dirección 3', discount_percent=0, balance=0),
        ]
        for customer in customers:
            db.session.add(customer)
        print("Clientes de ejemplo creados")
    
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
