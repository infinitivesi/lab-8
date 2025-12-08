from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import get_products, add_order, get_order_details, get_orders_by_email

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/shop')
def shop():
    # Read filter/search parameters from query string
    q = request.args.get('q', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    has_image_param = request.args.get('has_image')

    # Parse numeric filters
    try:
        min_price_val = float(min_price) if min_price != '' else None
    except ValueError:
        min_price_val = None
    try:
        max_price_val = float(max_price) if max_price != '' else None
    except ValueError:
        max_price_val = None

    has_image_flag = True if has_image_param in ('1', 'on', 'true', 'yes') else None

    products = get_products(q=q or None, min_price=min_price_val, max_price=max_price_val, has_image=has_image_flag)
    return render_template('shop.html', products=products, q=q, min_price=min_price, max_price=max_price, has_image=has_image_flag)

@shop_bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart = session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {'id': product_id, 'name': product['name'], 'price': product['price'], 'quantity': 1}
        session['cart'] = cart
    return redirect(url_for('shop.shop'))

@shop_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)

@shop_bp.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    email = request.form['email']
    address = request.form['address']
    phone = request.form.get('phone', '')
    try:
        order_id = add_order(email, address, cart, phone)
    except Exception as e:
        flash('Помилка при оформленні замовлення. Спробуйте пізніше.', 'error')
        return redirect(url_for('shop.cart'))

    # remember user email in session so they can view order history
    session['user_email'] = email
    session['cart'] = {}
    flash('Замовлення оформлено успішно.', 'info')
    return redirect(url_for('shop.orders'))


@shop_bp.route('/orders', methods=['GET', 'POST'])
def orders():
    # If user POSTs an email to view orders, use that; otherwise use session
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        session['user_email'] = email
        return redirect(url_for('shop.orders'))

    email = session.get('user_email')
    if not email:
        # show simple form to enter email
        return render_template('orders.html', orders=None, email=None)

    orders = get_orders_by_email(email)
    return render_template('orders.html', orders=orders, email=email)


@shop_bp.route('/orders/<int:order_id>')
def order_history_details(order_id):
    order, items = get_order_details(order_id)
    # simple protection: only allow viewing if session email matches order email
    user_email = session.get('user_email')
    if user_email and order and order['email'] != user_email:
        flash('Ви не маєте доступу до цього замовлення', 'error')
        return redirect(url_for('shop.orders'))
    # Users can edit contact info but cannot edit status
    return render_template('order_details.html', order=order, items=items, can_edit_status=False, can_edit_contact=True)


@shop_bp.route('/orders/<int:order_id>/update_contact', methods=['POST'])
def update_order_contact(order_id):
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    # verify ownership
    user_email = session.get('user_email')
    order = get_order_details(order_id)[0]
    if order and user_email and order['email'] != user_email:
        flash('Ви не маєте доступу для оновлення цього замовлення', 'error')
        return redirect(url_for('shop.orders'))
    # update contact info
    from models import update_order_contact
    update_order_contact(order_id, address, phone)
    flash('Контактні дані оновлено', 'info')
    return redirect(url_for('shop.order_history_details', order_id=order_id))