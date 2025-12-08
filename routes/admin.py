from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from models import get_db_connection, get_orders, get_order_details, update_order_status, delete_order
from models import get_clients, add_client, update_client, delete_client
from models import get_products, get_product, add_product, update_product, delete_product

admin_bp = Blueprint('admin', __name__)


# Перед доступом до захищених маршрутів перевіряємо, чи увійшов адмін
@admin_bp.before_request
def require_admin_login():
    # Дозволяємо сторінки логіну та виходу без перевірки
    allowed_endpoints = ('admin.login', 'admin.logout', 'admin.static')
    if request.endpoint in allowed_endpoints:
        return
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        # Пароль беремо з конфігурації додатку (app.config['ADMIN_PASSWORD'])
        if password == current_app.config.get('ADMIN_PASSWORD', 'prikol123'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin'))
        flash('Неправильний пароль', 'error')
        return redirect(url_for('admin.login'))
    return render_template('admin_login.html')


@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Ви вийшли з адмін-панелі', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/admin')
def admin():
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback').fetchall()
    conn.close()
    orders = get_orders()
    clients = get_clients()
    products = get_products()
    return render_template('admin.html', feedback=feedback, orders=orders, clients=clients, products=products)

@admin_bp.route('/admin/delete_feedback/<int:id>', methods=['POST'])
def delete_feedback(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM feedback WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/clients/add', methods=['POST'])
def add_client_route():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    has_courses = request.form.get('has_courses')
    has_flag = 1 if has_courses in ('1', 'on', 'true', 'yes') else 0
    if name:
        add_client(name, email, phone, address, has_flag)
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/clients/edit/<int:client_id>', methods=['POST'])
def edit_client_route(client_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    # has_courses may come from checkbox or JS param
    has_courses = request.form.get('has_courses')
    has_flag = 1 if has_courses in ('1', 'on', 'true', 'yes') else 0
    update_client(client_id, name, email, phone, address, has_flag)
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/clients/delete/<int:client_id>', methods=['POST'])
def delete_client_route(client_id):
    delete_client(client_id)
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/order/<int:order_id>')
def order_details(order_id):
    order, items = get_order_details(order_id)
    # Admin can edit status but not limited to contact edits
    return render_template('order_details.html', order=order, items=items, can_edit_status=True, can_edit_contact=False)

@admin_bp.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
def update_order(order_id):
    status = request.form['status']
    update_order_status(order_id, status)
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/delete_order/<int:order_id>', methods=['POST'])
def delete_order_route(order_id):
    delete_order(order_id)
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/products/add', methods=['POST'])
def add_product_route():
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '0')
    image = request.form.get('image', '')
    try:
        price = float(price)
        if name and price > 0:
            add_product(name, price, image)
            flash('Товар додано', 'info')
    except ValueError:
        flash('Неправильна ціна', 'error')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/products/edit/<int:product_id>', methods=['POST'])
def edit_product_route(product_id):
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '0')
    image = request.form.get('image', '')
    try:
        price = float(price)
        if name and price > 0:
            update_product(product_id, name, price, image)
            flash('Товар оновлено', 'info')
    except ValueError:
        flash('Неправильна ціна', 'error')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product_route(product_id):
    delete_product(product_id)
    flash('Товар видалено', 'info')
    return redirect(url_for('admin.admin'))