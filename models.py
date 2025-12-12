import os
import sqlite3
from datetime import datetime

def get_db_connection():
    # Allow overriding DB file path via environment variable (useful for containers)
    db_path = os.environ.get('DB_PATH', 'db.sqlite')
    conn = sqlite3.connect(db_path, timeout=30.0, isolation_level='DEFERRED')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT)')
    # Add feedback_type column (developer or general) if it doesn't exist
    try:
        conn.execute('ALTER TABLE feedback ADD COLUMN feedback_type TEXT DEFAULT "general"')
    except Exception:
        pass
    conn.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, image TEXT)')
    # Add description column to products if it doesn't exist
    try:
        conn.execute("ALTER TABLE products ADD COLUMN description TEXT DEFAULT ''")
    except Exception:
        pass
    conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, address TEXT, total_price REAL, status TEXT, date TEXT)')
    # Ensure orders table has phone column for contact updates
    try:
        conn.execute('ALTER TABLE orders ADD COLUMN phone TEXT DEFAULT ""')
    except Exception:
        pass
    conn.execute('CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, product_id INTEGER, quantity INTEGER, FOREIGN KEY (order_id) REFERENCES orders (id), FOREIGN KEY (product_id) REFERENCES products (id))')
    # Додаткова таблиця для клієнтів
    conn.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, address TEXT)')
    # Спробуємо додати колонку has_courses якщо її ще немає (старі БД)
    try:
        conn.execute('ALTER TABLE clients ADD COLUMN has_courses INTEGER DEFAULT 0')
    except Exception:
        # Якщо колонка вже існує або SQLite не дозволяє — ігноруємо помилку
        pass
    conn.commit()
    conn.close()

def get_products(q=None, min_price=None, max_price=None, has_image=None):
    """Return products optionally filtered by search term (q), price range and whether they have an image.
    - q: substring to search in product name
    - min_price, max_price: numeric bounds
    - has_image: True to require non-empty image, None/False to ignore
    """
    conn = get_db_connection()
    query = 'SELECT * FROM products'
    clauses = []
    params = []
    if q:
        clauses.append('name LIKE ?')
        params.append(f'%{q}%')
    if min_price is not None:
        try:
            min_price_float = float(min_price)
            clauses.append('price >= ?')
            params.append(min_price_float)
        except (ValueError, TypeError):
            pass
    if max_price is not None:
        try:
            max_price_float = float(max_price)
            clauses.append('price <= ?')
            params.append(max_price_float)
        except (ValueError, TypeError):
            pass
    if has_image is True:
        clauses.append("(image IS NOT NULL AND image != '')")

    if clauses:
        query += ' WHERE ' + ' AND '.join(clauses)
    query += ' ORDER BY id'
    products = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return products


def get_product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return product


def add_product(name, price, image='', description=''):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO products (name, price, image, description) VALUES (?, ?, ?, ?)',
                (name, price, image, description))
    conn.commit()
    conn.close()


def update_product(product_id, name, price, image='', description=''):
    conn = get_db_connection()
    conn.execute('UPDATE products SET name = ?, price = ?, image = ?, description = ? WHERE id = ?',
                 (name, price, image, description, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def add_order(email, address, cart, phone=''):
    try:
        conn = get_db_connection()
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())
        cur = conn.cursor()
        cur.execute('INSERT INTO orders (email, address, total_price, status, date, phone) VALUES (?, ?, ?, ?, ?, ?)',
                    (email, address, total_price, 'Нове', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone))
        order_id = cur.lastrowid
        for item in cart.values():
            cur.execute('INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)',
                        (order_id, item['id'], item['quantity']))
        conn.commit()
        conn.close()
        return order_id
    except sqlite3.OperationalError as e:
        print(f'Database error in add_order: {e}')
        raise

def get_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return orders


def get_orders_by_email(email):
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE email = ? ORDER BY date DESC', (email,)).fetchall()
    conn.close()
    return orders


def get_orders_matching_email(email):
    """Return orders where email matches the provided value.
    This does a case-insensitive partial match (LIKE) and trims the input.
    Useful for searches from the frontend where users may enter partial or differently-cased emails.
    """
    conn = get_db_connection()
    if email is None:
        conn.close()
        return []
    email_search = f"%{email.strip().lower()}%"
    orders = conn.execute('SELECT * FROM orders WHERE LOWER(email) LIKE ? ORDER BY date DESC', (email_search,)).fetchall()
    conn.close()
    return orders


def get_clients():
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()
    return clients


def get_client(client_id):
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    return client


def add_client(name, email, phone, address, has_courses=0):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO clients (name, email, phone, address, has_courses) VALUES (?, ?, ?, ?, ?)',
                (name, email, phone, address, 1 if has_courses else 0))
    conn.commit()
    conn.close()


def update_client(client_id, name, email, phone, address, has_courses=0):
    conn = get_db_connection()
    conn.execute('UPDATE clients SET name = ?, email = ?, phone = ?, address = ?, has_courses = ? WHERE id = ?',
                 (name, email, phone, address, 1 if has_courses else 0, client_id))
    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

def get_order_details(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    items = conn.execute('SELECT oi.quantity, p.name, p.price FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?', (order_id,)).fetchall()
    conn.close()
    return order, items


def update_order_contact(order_id, address, phone):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET address = ?, phone = ? WHERE id = ?', (address, phone, order_id))
    conn.commit()
    conn.close()

def update_order_status(order_id, status):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()


def get_feedback_by_type(feedback_type='general'):
    """Get feedback filtered by type (general or developer)."""
    conn = get_db_connection()
    feedback = conn.execute('SELECT * FROM feedback WHERE feedback_type = ? ORDER BY id DESC', (feedback_type,)).fetchall()
    conn.close()
    return feedback


def add_feedback(name, email, message, feedback_type='general'):
    """Add feedback with a type indicator."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO feedback (name, email, message, feedback_type) VALUES (?, ?, ?, ?)',
        (name, email, message, feedback_type)
    )
    conn.commit()
    feedback_id = cur.lastrowid
    conn.close()
    return feedback_id