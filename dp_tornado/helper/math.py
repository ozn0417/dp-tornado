# -*- coding: utf-8 -*-


from __future__ import absolute_import
from dp_tornado.engine.helper import Helper as dpHelper

import math


class MathHelper(dpHelper):
    @dpHelper.decorators.deprecated
    def floor(self, x):
        return math.floor(x)

    @dpHelper.decorators.deprecated
    def ceil(self, x):
        return math.ceil(x)

    @dpHelper.decorators.deprecated
    def round(self, number, ndigits=None):
        return round(number, ndigits)
