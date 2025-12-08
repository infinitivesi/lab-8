import sqlite3

import models


class TestDatabase:
    def test_init_db_creates_tables(self):
        conn = models.get_db_connection()
        curs = conn.cursor()
        curs.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in curs.fetchall()]
        conn.close()
        assert 'orders' in tables and 'products' in tables and 'feedback' in tables
