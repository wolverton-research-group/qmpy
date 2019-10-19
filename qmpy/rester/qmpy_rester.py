import json
import os

WEBPORT = os.environ.get('web_port')

REST_OPTIMADE  = 'http://larue.northwestern.edu:'+WEBPORT+'/optimade'
REST_OQMDAPI   = 'http://larue.northwestern.edu:'+WEBPORT+'/oqmdapi'
REST_END_POINT = REST_OQMDAPI

class QMPYRester(object):
    def __init__(self, endpoint=REST_END_POINT):
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

    def get_oqmd_phases(self, verbose=True, **kwargs):
        """
        Input:
            verbose: boolean
            **kwargs: dict
        Output:
            dict
        """

        # URL paramters
        url_args = []
        kwargs_list = ['composition', 'icsd', 'noduplicate',#'filter',
                       'sort_by', 'desc', 'sort_offset',
                       'limit', 'offset', 'fields']

        # Attributes for filters
        filter_args = []
        filter_list = ['element_set', 'element', 'spacegroup',
                       'prototype', 'generic', 'volume',
                       'natoms', 'ntypes', 'stability',
                       'delta_e', 'band_gap']

        for k in kwargs.keys():
            if k in kwargs_list:
                url_args.append('%s=%s' %(k, kwargs[k]))
            elif k in filter_list:
                if '>' in kwargs[k] or '<' in kwargs[k] or '!=' in kwargs[k]:
                    filter_args.append('%s%s' %(k, kwargs[k]))
                else:
                    filter_args.append('%s=%s' %(k, kwargs[k]))

        if 'filter' in kwargs.keys():
            filter_args.append(kwargs['filter'])


        if filter_args != []:
            filters_tag = ' AND '.join(filter_args)
            url_args.append('filter='+filters_tag)
        if verbose:
            print "Your filters are:"
            if url_args == []:
                print "   No filters?"
            else:
                for arg in url_args:
                    print "   ", arg

            ans = raw_input('Proceed? [Y/n]:')

            if ans not in ['Y', 'y', 'Yes', 'yes']:
                return

        _url = '&'.join(url_args)
        self.suburl = _url

        return self._make_requests('/formationenergy?%s'%_url)

    def get_entries(self, verbose=True, all_data=False, **kwargs):
        """
        Input:
            verbose: boolean
            all_data: boolean  
                    :: whether or not to output all data at one time
            **kwargs: dict
                :composition
                :calculated
                :icsd
                :band_gap
                :ntypes
                :generic
                :sort_by
                :desc
                :sort_offset
                :limit
                :offset
        Output:
            dict
        """
        url_args = []
        kwargs_list = ['composition', 'calculated', 'icsd',
                       'band_gap', 'ntypes', 'generic',
                       'sort_by', 'desc', 'sort_offset',
                       'limit', 'offset']

        for k in kwargs_list:
            if k in kwargs:
                url_args.append('%s=%s' %(k, kwargs[k]))

        if verbose:
            print "Your Entry filters are:"
            if url_args == []:
                print "   No filters?"
            else:
                for arg in url_args:
                    print "   ", arg

            ans = raw_input('Proceed? [Y/n]:')

            if ans not in ['Y', 'y', 'Yes', 'yes']:
                return

        _url = '&'.join(url_args)

        if all_data == True:
            output = self._make_requests('/entry?%s'%_url)
            next_page = output['next']
            while next_page:
                tmp = self._make_requests(next_page.replace(self.preamble, ''))
                output['results'].extend(tmp['results'])
                next_page = tmp['next']
            output['next'] = next_page
            return output
            
        return self._make_requests('/entry?%s'%_url)

    def get_entry_by_id(self, entry_id):
        return self._make_requests('/entry/%d'%entry_id)

    def get_calculations(self, verbose=True, all_data=False, **kwargs):
        """
        Input:
            verbose: boolean
            all_data: boolean  
                    :: whether or not to output all data at one time
            **kwargs: dict
                :converged
                :label
                :band_gap
                :sort_by
                :desc
                :sort_offset
                :limit
                :offset
        Output:
            dict
        """
        url_args = []
        kwargs_list = ['converged', 'label', 'band_gap',
                       'sort_by', 'desc', 'sort_offset',
                       'limit', 'offset']

        for k in kwargs_list:
            if k in kwargs:
                url_args.append('%s=%s' %(k, kwargs[k]))

        if verbose:
            print "Your Calculation filters are:"
            if url_args == []:
                print "   No filters?"
            else:
                for arg in url_args:
                    print "   ", arg

            ans = raw_input('Proceed? [Y/n]:')

            if ans not in ['Y', 'y', 'Yes', 'yes']:
                return

        _url = '&'.join(url_args)

        if all_data == True:
            output = self._make_requests('/calculation?%s'%_url)
            next_page = output['next']
            while next_page:
                tmp = self._make_requests(next_page.replace(self.preamble, ''))
                output['results'].extend(tmp['results'])
                next_page = tmp['next']
            output['next'] = next_page
            return output

        return self._make_requests('/calculation?%s'%_url)

    def get_calculation_by_id(self, calc_id):
        return self._make_requests('/calculation/%d'%calc_id)
