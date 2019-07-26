import unittest
import requests
from tests import API_HOST
from urllib.parse import urljoin


class TestFooAPI(unittest.TestCase):

    API_URL = '/foo'
    DATA = {
        'name': 'Foo Example',
        'email': 'foo@email.com',
    }

    def test_foo_api(self):
        api_url = urljoin(API_HOST, self.API_URL)

        # Test POST
        resp = requests.post(api_url, json=self.DATA)
        self.assertEqual(resp.status_code, 201)

        foo_id = resp.json()['data']['id']

        # Test GET
        url = urljoin(api_url + '/', str(foo_id))
        resp = requests.get(url)
        self.assertEqual(resp.status_code, 200)
        foo_data = resp.json()['data']
        for k in self.DATA.keys():
            self.assertEqual(foo_data[k], self.DATA[k])

        # Test UPDATE
        put_data = {}
        for k, v in self.DATA.items():
            if isinstance(v, str):
                put_data[k] = '{} (updated)'.format(v)
        url = urljoin(api_url + '/', str(foo_id))
        resp = requests.put(url, json=put_data)
        self.assertEqual(resp.status_code, 200)
        foo_data = resp.json()['data']
        for k in put_data.keys():
            self.assertEqual(foo_data[k], put_data[k])

        # Test DELETE
        url = urljoin(api_url + '/', str(foo_id))
        resp = requests.delete(url)
        self.assertEqual(resp.status_code, 200)
        # GET response should be 404
        resp = requests.get(url)
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
