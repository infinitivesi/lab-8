from app import app

with app.test_client() as c:
    # Simulate adding to cart and checkout
    c.get('/add_to_cart/1')
    
    resp = c.post('/checkout', data={
        'email': 'test@example.com',
        'address': 'Test Address'
    }, follow_redirects=False)
    
    print('Checkout status:', resp.status_code)
    if resp.status_code == 302:
        print('✓ Success! Redirected to:', resp.headers.get('Location'))
    else:
        print('Error response:')
        print(resp.data.decode()[:300])
