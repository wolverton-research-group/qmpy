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

    def get_entries(self, **kwargs):
        url_args = []
        kwargs_list = ['composition', 'composition_include', 'calculated',
                       'gap', 'ntypes', 'generic']

        for k in kwargs_list:
            if k in kwargs:
                url_args.append('%s=%s' %(k, kwargs[k]))

        _url = '&'.join(url_args)
        return self._make_requests('/entry?%s'%_url)

    def get_entry_by_id(self, entry_id):
        return self._make_requests('/entry/%d'%entry_id)

    def get_calculations(self, **kwargs):
        url_args = []
        kwargs_list = ['converged', 'label', 'gap']

        for k in kwargs_list:
            if k in kwargs:
                url_args.append('%s=%s' %(k, kwargs[k]))

        _url = '&'.join(url_args)
        return self._make_requests('/calculation?%s'%_url)

    def get_calculation_by_id(self, calc_id):
        return self._make_requests('/calculation/%d'%calc_id)
