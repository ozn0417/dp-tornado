# -*- coding: utf-8 -*-

"""

  dp for Tornado

  MVC Web Application Framework with Tornado
  http://github.com/why2pac/dp-tornado

  Copyright (c) 2015, why2pac <youngyongpark@gmail.com>

"""


import tornado.web
import tornado.ioloop
import tornado.httpserver

import logging
import logging.handlers

import time
import os
import multiprocessing
import importlib

from dp_tornado.engine.engine import EngineSingleton as dpEngineSingleton
from dp_tornado.engine.bootstrap import Bootstrap as EngineBootstrap
from dp_tornado.engine.scheduler import Scheduler
from dp_tornado.engine.plugin.static import Compressor
from dp_tornado.engine.plugin.static import StaticURL
from dp_tornado.engine.plugin.pagination import Pagination
from dp_tornado.engine.plugin import ui_methods
from dp_tornado.version import __version_info__


engine = dpEngineSingleton()


class RestfulApplication(tornado.web.Application):
    def __init__(self, handlers, kwargs):
        self.startup_at = int(round(time.time() * 1000))

        kwargs['ui_modules']['Static'] = StaticURL
        kwargs['ui_modules']['Pagination'] = Pagination
        kwargs['ui_methods'] = ui_methods

        super(RestfulApplication, self).__init__(handlers, **kwargs)


class Bootstrap(object):
    def run(self, **kwargs):
        as_cli = True if 'as_cli' in kwargs and kwargs['as_cli'] else False

        custom_scheduler = kwargs['scheduler'] if 'scheduler' in kwargs else None
        custom_service = kwargs['service'] if 'service' in kwargs else None
        custom_config_file = kwargs['config_file'] if 'config_file' in kwargs else 'config.ini'

        application_path = kwargs['application_path'] if 'application_path' in kwargs else None

        os.environ['DP_APPLICATION_PATH'] = application_path
        os.environ['DP_APPLICATION_INI'] = custom_config_file

        settings = EngineBootstrap.init_ini(
            application_path=application_path, ini_file=custom_config_file, as_cli=as_cli)

        engine.logger.log(100, '---------------------------------')
        engine.logger.log(100, 'dp for Python            v%s' % '.'.join([str(e) for e in __version_info__]))
        engine.logger.log(100, '---------------------------------')

        services_raw = [
            (r"/dp/scheduler/(.*)", 'dp_tornado.engine.scheduler_handler.SchedulerHandler'),
            (r"/", None),
            (r"/(.*)", None),
        ]

        if custom_service:
            services_raw = custom_service + services_raw

        services = []
        default_handler = None

        for service in services_raw:
            if len(service) < 2:
                raise Exception('The specified service is invalid.')

            if service[1] is not None:
                s = str.split(service[1], '.')
                class_name = s.pop()
                module_path = '.'.join(s)

                handler_module = importlib.import_module(module_path)
                handler = getattr(handler_module, class_name)

            else:
                if default_handler is None:
                    handler_module = importlib.import_module('dp_tornado.engine.default_handler')
                    default_handler = getattr(handler_module, 'DefaultHandler')

                module_path = 'controller'
                handler = default_handler

            services.append((service[0], handler, dict(prefix=module_path)))

        # Clear combined files
        Compressor.clear(settings['combined_static_path'])
        num_processed = engine.ini.server.num_processes if engine.ini.server.num_processes \
            else multiprocessing.cpu_count()

        engine.logger.log(100, 'Server Mode : %s' % ('Production' if not engine.ini.server.debug else 'Debugging'))
        engine.logger.log(100, 'Server time : %s' % time.strftime('%Y.%m.%d %H:%M:%S'))
        engine.logger.log(100, 'Server Port : %s' % engine.ini.server.port)
        engine.logger.log(100, 'Processors  : %s' % num_processed)
        engine.logger.log(100, 'CPU Count   : %d' % multiprocessing.cpu_count())
        engine.logger.log(100, '---------------------------------')

        if custom_scheduler:
            scheduler = Scheduler(custom_scheduler)
            scheduler.start()

        else:
            scheduler = None

        application = RestfulApplication(services, settings)
        service = tornado.httpserver.HTTPServer(
            application,
            xheaders=True,
            max_body_size=engine.ini.server.max_body_size)
        service.bind(engine.ini.server.port, '')
        service.start(engine.ini.server.num_processes)

        import random
        application.identifier = random.randint(100000, 999999)

        try:
            instance = tornado.ioloop.IOLoop.instance()
            instance.__setattr__('startup_at', getattr(application, 'startup_at'))
            instance.start()

        except KeyboardInterrupt:
            if scheduler:
                scheduler.interrupted = True
