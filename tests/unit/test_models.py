import pytest
import sqlite3
from datetime import datetime

import models


class TestModels:
    def test_add_and_get_product(self):
        models.add_product('TestProd', 12.5, 'img.png')
        prod = models.get_products(q='TestProd')
        assert any(p['name'] == 'TestProd' for p in prod)

    def test_update_and_delete_product(self):
        models.add_product('ToUpdate', 1.0, '')
        prods = models.get_products(q='ToUpdate')
        prod_id = prods[0]['id']
        models.update_product(prod_id, 'Updated', 2.0, 'img2')
        p = models.get_product(prod_id)
        assert p['name'] == 'Updated'
        models.delete_product(prod_id)
        assert models.get_product(prod_id) is None

    def test_get_products_filters(self):
        # ensure sample products are present
        models.add_product('FilterMe', 100.0, 'x')
        res = models.get_products(min_price=50, max_price=150)
        assert any(r['name'] == 'FilterMe' for r in res)

    def test_get_products_has_image(self):
        models.add_product('HasImg', 5.0, 'url')
        res = models.get_products(has_image=True)
        assert any(r['name'] == 'HasImg' for r in res)

    def test_add_order_empty_cart(self):
        oid = models.add_order('a@b.com', 'Addr', {}, '')
        orders = models.get_orders_by_email('a@b.com')
        assert any(o['id'] == oid for o in orders)

    def test_get_orders_matching_email_partial_case(self):
        models.add_order('User@Example.com', 'Addr', {}, '')
        matches = models.get_orders_matching_email('user@exam')
        assert len(matches) >= 1

    def test_get_order_details_items(self):
        # create product and an order with that product
        models.add_product('ItemX', 7.5, '')
        p = models.get_products(q='ItemX')[0]
        cart = {str(p['id']): {'id': p['id'], 'price': p['price'], 'quantity': 2}}
        oid = models.add_order('z@z.com', 'Here', cart, '')
        order, items = models.get_order_details(oid)
        assert order is not None
        assert len(items) == 1

    def test_client_crud(self):
        models.add_client('C1', 'c1@example.com', '123', 'A')
        clients = models.get_clients()
        assert any(c['email'] == 'c1@example.com' for c in clients)

    def test_update_order_status_and_contact(self):
        oid = models.add_order('s@t.com', 'Addr', {}, '777')
        models.update_order_status(oid, 'Processing')
        models.update_order_contact(oid, 'New Addr', '888')
        order = models.get_orders_by_email('s@t.com')[0]
        assert order['status'] == 'Processing'
        assert order['phone'] == '888'

    def test_get_products_invalid_price_filters(self):
        # passing non-numeric min_price should be ignored
        models.add_product('NumTest', 9.9, '')
        res = models.get_products(min_price='notnumber')
        assert isinstance(res, list)

    def test_add_order_malformed_cart_raises(self):
        with pytest.raises(Exception):
            # malformed cart missing price/quantity
            models.add_order('bad@b', 'A', {'x': {'id': 999}}, '')
