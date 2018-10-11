import json

class QMPYRester(object):
    def __init__(self, endpoint='http://larue.northwestern.edu:7000/serializer'):
        self.preamble = endpoint
        import requests
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def _make_requests(self, sub_url, payload=None, method='GET'):
        response = None
        url = self.preamble + sub_url

        if method == 'GET':
            response = self.session.get(url, params=payload, verify=True)
            
            if response.status_code in [200, 400]:
                data = json.loads(response.text)
                return data

    def get_entries_from_composition(self, comp):
        return self._make_requests('/entry?composition=%s'%comp)
