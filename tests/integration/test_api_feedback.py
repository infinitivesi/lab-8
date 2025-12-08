class TestAPIFeedback:
    def test_create_feedback_api(self, client):
        payload = {'name': 'F1', 'email': 'f1@example.com', 'message': 'Nice'}
        r = client.post('/api/v1/feedback', json=payload)
        assert r.status_code in (200,201)

    def test_delete_feedback_api(self, client):
        # create
        r = client.post('/api/v1/feedback', json={'name': 'F2', 'email': 'f2@example.com', 'message': 'Hi'})
        # retrieve list and delete last
        lst = client.get('/api/v1/feedback')
        fid = lst.get_json()['data'][0]['id']
        d = client.delete(f'/api/v1/feedback/{fid}')
        assert d.status_code == 200
