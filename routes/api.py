from flask import Blueprint, jsonify, request
from functools import wraps
from models import (
    get_db_connection,
    get_products,
    get_product,
    add_product,
    update_product,
    delete_product,
    get_orders,
  get_orders_by_email,
  get_orders_matching_email,
    get_order_details,
    add_order,
    update_order_status,
    delete_order,
    get_feedback_by_type,
    add_feedback
)

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ============ Helper decorators and functions ============

def require_json(*required_fields):
    """Decorator to validate JSON request and required fields."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON format', 'code': 'INVALID_JSON'}), 400
            for field in required_fields:
                if field not in data or data[field] is None:
                    return jsonify({
                        'error': f'Missing required field: {field}',
                        'code': 'MISSING_FIELD',
                        'field': field
                    }), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator

def error_response(message, code, status_code=500, details=None):
    """Create a standardized error response."""
    response = {'error': message, 'code': code, 'status': status_code}
    if details:
        response['details'] = details
    return jsonify(response), status_code

def success_response(data, message=None, status_code=200):
    """Create a standardized success response."""
    response = {'status': 'success', 'status_code': status_code}
    if message:
        response['message'] = message
    response['data'] = data
    return jsonify(response), status_code

# Products endpoints
@api_bp.route('/products', methods=['GET'])
def get_all_products():
    """
    Отримати всі продукти з опціональною фільтрацією
    ---
    tags:
      - Products
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Пошуковий термін для назви товару
      - name: min_price
        in: query
        type: number
        required: false
        description: Мінімальна ціна
      - name: max_price
        in: query
        type: number
        required: false
        description: Максимальна ціна
      - name: has_image
        in: query
        type: boolean
        required: false
        description: Тільки товари з фото
    responses:
      200:
        description: Список продуктів
      500:
        description: Помилка сервера
    """
    try:
        q = request.args.get('q')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        has_image = request.args.get('has_image') in ('true', '1', 'yes') if request.args.get('has_image') else None
        
        products = get_products(q=q, min_price=min_price, max_price=max_price, has_image=has_image)
        return success_response([dict(product) for product in products])
    except Exception as e:
        return error_response(f'Error retrieving products: {str(e)}', 'PRODUCT_RETRIEVAL_ERROR', 500)

@api_bp.route('/products', methods=['POST'])
@require_json('name', 'price')
def create_product():
    """
    Створити новий продукт
    ---
    tags:
      - Products
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
              example: "Ноутбук Dell"
            price:
              type: number
              example: 1999.99
            image:
              type: string
              example: "https://example.com/laptop.jpg"
    responses:
      201:
        description: Продукт успішно створено
      400:
        description: Відсутні обов'язкові поля
      500:
        description: Помилка сервера
    """
    try:
        data = request.get_json()
        name = data.get('name')
        price = float(data.get('price'))
        image = data.get('image', '')
        
        add_product(name, price, image)
        return success_response({'name': name, 'price': price, 'image': image}, 
                              message='Product created successfully', status_code=201)
    except ValueError:
        return error_response('Price must be a valid number', 'INVALID_PRICE', 400)
    except Exception as e:
        return error_response(f'Error creating product: {str(e)}', 'PRODUCT_CREATION_ERROR', 500)

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
@require_json('name', 'price')
def update_prod(product_id):
    """
    Оновити продукт
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
            price:
              type: number
            image:
              type: string
    responses:
      200:
        description: Продукт успішно оновлено
      404:
        description: Продукт не знайдено
      500:
        description: Помилка сервера
    """
    try:
        product = get_product(product_id)
        if not product:
            return error_response('Product not found', 'PRODUCT_NOT_FOUND', 404)
        
        data = request.get_json()
        name = data.get('name')
        price = float(data.get('price'))
        image = data.get('image', '')
        
        update_product(product_id, name, price, image)
        return success_response({'id': product_id, 'name': name, 'price': price, 'image': image},
                              message='Product updated successfully')
    except ValueError:
        return error_response('Price must be a valid number', 'INVALID_PRICE', 400)
    except Exception as e:
        return error_response(f'Error updating product: {str(e)}', 'PRODUCT_UPDATE_ERROR', 500)

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_prod(product_id):
    """
    Видалити продукт
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Продукт успішно видалено
      404:
        description: Продукт не знайдено
      500:
        description: Помилка сервера
    """
    try:
        product = get_product(product_id)
        if not product:
            return error_response('Product not found', 'PRODUCT_NOT_FOUND', 404)
        
        delete_product(product_id)
        return success_response({'id': product_id}, message='Product deleted successfully')
    except Exception as e:
        return error_response(f'Error deleting product: {str(e)}', 'PRODUCT_DELETE_ERROR', 500)

# Orders endpoints
@api_bp.route('/orders', methods=['GET'])
def get_all_orders():
    """
    Отримати всі замовлення або замовлення за email
    ---
    tags:
      - Orders
    parameters:
      - name: email
        in: query
        type: string
        required: false
        description: Email для фільтрації замовлень
    responses:
      200:
        description: Список замовлень
      500:
        description: Помилка сервера
    """
    try:
        email = request.args.get('email')
        if email:
            orders = get_orders_by_email(email)
        else:
            orders = get_orders()
        return success_response([dict(order) for order in orders])
    except Exception as e:
        return error_response(str(e), 'ORDER_RETRIEVAL_ERROR', 500)


@api_bp.route('/orders/search', methods=['GET'])
def search_orders_by_email():
    """
    Пошук замовлень за email (частковий, нечутливий до регістру)
    ---
    tags:
      - Orders
    parameters:
      - name: email
        in: query
        type: string
        required: true
        description: Email або його частина для пошуку
    responses:
      200:
        description: Список замовлень
      400:
        description: Не вказано email
      500:
        description: Помилка сервера
    """
    try:
        email = request.args.get('email', '').strip()
        if not email:
            return error_response('Email query parameter is required', 'MISSING_EMAIL', 400)
        # Use the models helper for case-insensitive partial matches
        orders = get_orders_matching_email(email)
        return success_response([dict(order) for order in orders])
    except Exception as e:
        return error_response(str(e), 'ORDER_SEARCH_ERROR', 500)

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Отримати деталі замовлення з товарами
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID замовлення
    responses:
      200:
        description: Деталі замовлення
      404:
        description: Замовлення не знайдено
      500:
        description: Помилка сервера
    """
    try:
        order, items = get_order_details(order_id)
        if not order:
            return error_response('Order not found', 'ORDER_NOT_FOUND', 404)
        return success_response({
            'order': dict(order),
            'items': [dict(item) for item in items]
        })
    except Exception as e:
        return error_response(str(e), 'ORDER_RETRIEVAL_ERROR', 500)

@api_bp.route('/orders', methods=['POST'])
@require_json('email', 'address')
def create_order():
    """
    Створити нове замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - address
          properties:
            email:
              type: string
              example: "user@example.com"
            address:
              type: string
              example: "вул. Шевченка, 10"
            phone:
              type: string
              example: "+380123456789"
            cart:
              type: object
              example: {}
            total_price:
              type: number
              example: 0
    responses:
      201:
        description: Замовлення успішно створено
      400:
        description: Відсутні обов'язкові поля
      500:
        description: Помилка сервера
    """
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        cart = data.get('cart', {})
        order_id = add_order(data['email'], data['address'], cart, phone)
        return success_response({
            'order_id': order_id,
            'message': 'Order created successfully'
        }, status_code=201)
    except Exception as e:
        return error_response(f'Error creating order: {str(e)}', 'ORDER_CREATION_ERROR', 500)

@api_bp.route('/orders/<int:order_id>', methods=['PUT'])
@require_json('status')
def update_order(order_id):
    """
    Оновити статус замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID замовлення
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              example: "Processing"
              enum: ["Нове", "Обробляється", "Відправлено", "Доставлено", "Скасовано"]
    responses:
      200:
        description: Замовлення оновлено
      400:
        description: Не вказано статус
      500:
        description: Помилка сервера
    """
    try:
        data = request.get_json()
        update_order_status(order_id, data['status'])
        return success_response({'message': 'Order updated successfully'})
    except Exception as e:
        return error_response(str(e), 'ORDER_UPDATE_ERROR', 500)

@api_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def remove_order(order_id):
    """
    Видалити замовлення
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID замовлення
    responses:
      200:
        description: Замовлення видалено
      500:
        description: Помилка сервера
    """
    try:
        delete_order(order_id)
        return success_response({'message': 'Order deleted successfully'})
    except Exception as e:
        return error_response(str(e), 'ORDER_DELETE_ERROR', 500)

# Feedback endpoints
@api_bp.route('/feedback', methods=['GET'])
def get_all_feedback():
    """
    Отримати всі відгуки
    ---
    tags:
      - Feedback
    responses:
      200:
        description: Список відгуків
      500:
        description: Помилка сервера
    """
    try:
        conn = get_db_connection()
        feedback = conn.execute('SELECT * FROM feedback ORDER BY id DESC').fetchall()
        conn.close()
        return success_response([dict(f) for f in feedback])
    except Exception as e:
        return error_response(str(e), 'FEEDBACK_RETRIEVAL_ERROR', 500)

@api_bp.route('/feedback', methods=['POST'])
@require_json('name', 'email', 'message')
def create_feedback():
    """
    Створити новий відгук (категорія 'general')
    ---
    tags:
      - Feedback
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - message
          properties:
            name:
              type: string
            email:
              type: string
            message:
              type: string
            feedback_type:
              type: string
              enum: [general, developer]
              default: general
    responses:
      201:
        description: Відгук створено
      500:
        description: Помилка сервера
    """
    try:
        data = request.get_json()
        feedback_type = data.get('feedback_type', 'general')
        feedback_id = add_feedback(data['name'], data['email'], data['message'], feedback_type)
        return success_response({
            'feedback_id': feedback_id,
            'message': 'Feedback submitted successfully'
        }, status_code=201)
    except Exception as e:
        return error_response(f'Error creating feedback: {str(e)}', 'FEEDBACK_CREATION_ERROR', 500)


@api_bp.route('/feedback/type/<feedback_type>', methods=['GET'])
def get_feedback_by_type_endpoint(feedback_type):
    """
    Отримати відгуки за типом (general або developer)
    ---
    tags:
      - Feedback
    parameters:
      - name: feedback_type
        in: path
        type: string
        required: true
        enum: [general, developer]
    responses:
      200:
        description: Список відгуків
      500:
        description: Помилка сервера
    """
    try:
        if feedback_type not in ('general', 'developer'):
            return error_response('Invalid feedback type', 'INVALID_TYPE', 400)
        feedback = get_feedback_by_type(feedback_type)
        return success_response([dict(f) for f in feedback])
    except Exception as e:
        return error_response(str(e), 'FEEDBACK_RETRIEVAL_ERROR', 500)

@api_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """
    Видалити відгук
    ---
    tags:
      - Feedback
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
        description: ID відгуку
    responses:
      200:
        description: Відгук видалено
      404:
        description: Відгук не знайдено
      500:
        description: Помилка сервера
    """
    try:
        conn = get_db_connection()
        feedback = conn.execute('SELECT * FROM feedback WHERE id = ?', (feedback_id,)).fetchone()
        
        if not feedback:
            conn.close()
            return error_response('Feedback not found', 'FEEDBACK_NOT_FOUND', 404)
            
        conn.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
        conn.commit()
        conn.close()
        
        return success_response({
            'deleted_id': feedback_id,
            'message': 'Feedback deleted successfully'
        })
    except Exception as e:
        return error_response(str(e), 'FEEDBACK_DELETE_ERROR', 500)

# ============ Health check endpoint ============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Перевірити стан API
    ---
    tags:
      - System
    responses:
      200:
        description: API працює
    """
    return success_response({'status': 'API is running'})
