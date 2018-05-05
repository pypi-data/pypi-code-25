#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from thumbor.filters import BaseFilter, filter_method, PHASE_AFTER_LOAD
from thumbor.point import FocalPoint

class Filter(BaseFilter):
    phase = PHASE_AFTER_LOAD

    @filter_method(
        BaseFilter.DecimalNumber,#percentage_width
        BaseFilter.DecimalNumber,#percentage_height
    )
    def focus(self, percentage_width, percentage_height):
        # change to percentage
        self.percentage_width = float(percentage_width / 100)
        self.percentage_height = float(percentage_height / 100)
        # retrive original image
        source_image = self.engine.image
        source_width, source_height = self.context.request.engine.size
       
        left = int(self.percentage_width * source_width)
        top = int(self.percentage_height * source_height)
        width = int(source_width)
        height = int(source_height)
        
        self.context.request.focal_points.append(
            FocalPoint.from_square(left, top, width, height, origin="Explicit")
        )
