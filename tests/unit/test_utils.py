import pytest

from models import get_products, add_product


class TestUtils:
    def test_search_substring(self):
        add_product('AlphaBeta', 1.0, '')
        res = get_products(q='Beta')
        assert any('Beta' in p['name'] for p in res)

    def test_ordering_of_products(self):
        add_product('OrderA', 1.0, '')
        add_product('OrderB', 2.0, '')
        res = get_products()
        assert res[0]['id'] <= res[-1]['id']
