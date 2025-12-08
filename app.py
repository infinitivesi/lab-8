import os
from flask import Flask, render_template, session, request, redirect, url_for
from flask_cors import CORS
from models import init_db
from routes.feedback import feedback_bp
from routes.admin import admin_bp
from routes.shop import shop_bp
from routes.api import api_bp

app = Flask(__name__)
app.secret_key = '1234'  # Необхідно для роботи з сесіями
# Пароль адміністратора: можна встановити змінною оточення ADMIN_PASSWORD
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', '123')
# Пароль для доступу до API-Demo (можна задати змінною оточення)
app.config['API_DEMO_PASSWORD'] = os.environ.get('API_DEMO_PASSWORD', '123')

# ============================================
# НАЛАШТУВАННЯ CORS
# ============================================
# Дозволяємо запити з фронтенду
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Ініціалізація Flasgger для документації API (опціонально)
try:
    from flasgger import Swagger
    # Configure basic swagger metadata via app.config
    app.config.setdefault('SWAGGER', {
        'title': 'Flask Shop API',
        'uiversion': 3
    })
    swagger = Swagger(app)
except ImportError:
    print("Warning: Flasgger not installed. Install with: pip install Flasgger")

# Ініціалізація бази даних
init_db()

# Реєстрація блюпрінтів
app.register_blueprint(feedback_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(api_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api-demo')
def api_demo():
    # Захищена сторінка: показати лише якщо пройшли аутентифікацію
    if session.get('api_demo_authenticated'):
        return render_template('api_demo.html')
    return redirect(url_for('api_demo_login'))


@app.route('/api-demo/login', methods=['GET', 'POST'])
def api_demo_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password and password == app.config.get('API_DEMO_PASSWORD'):
            session['api_demo_authenticated'] = True
            return redirect(url_for('api_demo'))
        error = 'Невірний пароль'
    return render_template('api_demo_login.html', error=error)


@app.route('/api-demo/logout')
def api_demo_logout():
    session.pop('api_demo_authenticated', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Bind to 0.0.0.0 so the dev server is reachable from other devices on the LAN.
    # Allow overriding host/port via environment variables for flexibility.
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True)