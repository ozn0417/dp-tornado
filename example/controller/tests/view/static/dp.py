# -*- coding: utf-8 -*-


from dp_tornado.engine.controller import Controller
from bs4 import BeautifulSoup


class DpController(Controller):
    def get(self):
        o = self.render_string('tests/view/static/dp.html')
        o = BeautifulSoup(o, 'lxml')

        min_local = False
        min_s3 = False

        for e in o.findAll('script'):
            if e.attrs['src'].startswith('/s/'):
                min_local = True
            elif e.attrs['src'].startswith('http://'):
                min_s3 = True

        assert min_local
        assert min_s3

        min_local = False
        min_s3 = False

        for e in o.findAll('link'):
            if e.attrs['href'].startswith('/s/'):
                min_local = True
            elif e.attrs['href'].startswith('http://'):
                min_s3 = True

        assert min_local
        assert min_s3

        self.finish('done')
