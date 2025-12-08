import pytest
import sqlite3
import sys
from pathlib import Path

# Add the project root to sys.path so imports work in CI environments
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import models
from app import app as flask_app


@pytest.fixture(scope='session')
def tmp_db_path(tmp_path_factory):
    p = tmp_path_factory.mktemp('data') / 'test_db.sqlite'
    return str(p)


@pytest.fixture(autouse=True)
def use_temp_db(tmp_db_path, monkeypatch):
    """Replace models.get_db_connection to use a temporary sqlite file for tests."""
    def get_db_connection():
        conn = sqlite3.connect(tmp_db_path, timeout=30.0, isolation_level='DEFERRED')
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(models, 'get_db_connection', get_db_connection)
    # Re-init DB for each test session
    models.init_db()
    yield


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def sample_products():
    # provide simple sample products for unit tests
    models.add_product('Widget A', 10.0, '')
    models.add_product('Widget B', 25.5, 'http://img')
    models.add_product('Gadget', 5.0, '')
    return True


@pytest.fixture
def sample_cart():
    # cart format used by add_order: dict of product_id -> {id, price, quantity}
    # We'll read inserted products to build a cart in tests when needed.
    return {}
