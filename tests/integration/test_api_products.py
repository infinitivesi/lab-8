import json

class TestAPIProducts:
    def test_create_product_api_success(self, client):
        payload = {'name': 'APIProd', 'price': 11.5, 'image': ''}
        r = client.post('/api/v1/products', json=payload)
        assert r.status_code == 200 or r.status_code == 201

    def test_create_product_api_missing_fields(self, client):
        r = client.post('/api/v1/products', json={'name': 'x'})
        assert r.status_code == 400

    def test_get_products_api(self, client):
        r = client.get('/api/v1/products')
        assert r.status_code == 200
        data = r.get_json()
        assert 'data' in data

    def test_update_and_delete_product_api(self, client):
        # create
        r = client.post('/api/v1/products', json={'name': 'ToAPI', 'price': 3.3})
        assert r.status_code in (200,201)
        body = r.get_json()
        # find product id via listing
        list_r = client.get('/api/v1/products?q=ToAPI')
        items = list_r.get_json()['data']
        pid = items[0]['id']
        # update
        up = client.put(f'/api/v1/products/{pid}', json={'name': 'ToAPI2', 'price': 4.4})
        assert up.status_code == 200
        # delete
        d = client.delete(f'/api/v1/products/{pid}')
        assert d.status_code == 200
