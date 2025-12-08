import json


class TestAPIOrders:
    def test_create_order_api(self, client):
        payload = {'email': 'inttest@example.com', 'address': 'Street 1', 'cart': {}}
        r = client.post('/api/v1/orders', json=payload)
        assert r.status_code in (200,201)

    def test_search_orders_api(self, client):
        # create order
        client.post('/api/v1/orders', json={'email': 'findme@example.com', 'address': 'X', 'cart': {}})
        r = client.get('/api/v1/orders/search?email=findme')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data['data']) >= 1

    def test_get_order_details_api(self, client):
        # create product and order with items
        client.post('/api/v1/products', json={'name': 'OIProd', 'price': 2.5})
        list_r = client.get('/api/v1/products?q=OIProd')
        pid = list_r.get_json()['data'][0]['id']
        cart = {str(pid): {'id': pid, 'price': 2.5, 'quantity': 2}}
        create_r = client.post('/api/v1/orders', json={'email': 'det@example.com', 'address': 'Y', 'cart': cart})
        body = create_r.get_json()
        # find order id by searching
        s = client.get('/api/v1/orders/search?email=det@example.com')
        items = s.get_json()['data']
        oid = items[0]['id']
        detail = client.get(f'/api/v1/orders/{oid}')
        assert detail.status_code == 200
