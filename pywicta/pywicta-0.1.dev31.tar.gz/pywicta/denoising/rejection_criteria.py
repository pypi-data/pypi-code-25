#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math

import numpy as np

from pywicta.image.hillas_parameters import get_hillas_parameters
from pywicta.io import geometry_converter

class CTAMarsCriteria:

    def __init__(self,
                 cam_id,
                 min_npe=50,
                 max_npe=float('inf'),
                 min_radius_meters=0,
                 max_radius_meters=None,
                 min_ellipticity=0.1,
                 max_ellipticity=0.6,
                 min_num_pixels=3):
        """CTA Mars like preselection cuts.

        Note
        ----

        average_camera_radius_meters = math.tan(math.radians(average_camera_radius_degree)) * foclen

        The average camera radius values are, in degrees :

        - LST: 2.31
        - Nectar: 4.05
        - Flash: 3.95
        - SST-1M: 4.56
        - GCT-CHEC-S: 3.93
        - ASTRI: 4.67

        Parameters
        ----------
        cam_id
        min_radius_meters
        max_radius_meters
        min_npe
        max_npe
        min_ellipticity
        max_ellipticity
        """

        if max_radius_meters is None:
            RADIUS_CONSTRAINT_RATIO = 0.8

            if cam_id == "ASTRICam":
                average_camera_radius_degree = 4.67
                foclen_meters = 2.15
            elif cam_id == "CHEC":
                average_camera_radius_degree = 3.93
                foclen_meters = 2.283
            elif cam_id == "DigiCam":
                average_camera_radius_degree = 4.56
                foclen_meters = 5.59
            elif cam_id == "FlashCam":
                average_camera_radius_degree = 3.95
                foclen_meters = 16.0
            elif cam_id == "NectarCam":
                average_camera_radius_degree = 4.05
                foclen_meters = 16.0
            elif cam_id == "LSTCam":
                average_camera_radius_degree = 2.31
                foclen_meters = 28.0
            else:
                raise ValueError('Unknown camid', cam_id)

            average_camera_radius_meters = math.tan(math.radians(average_camera_radius_degree)) * foclen_meters
            max_radius_meters = RADIUS_CONSTRAINT_RATIO * average_camera_radius_meters

        self.cam_id = cam_id
        self.geom1d = geometry_converter.get_geom1d(self.cam_id)
        self.hillas_implementation = 2

        self.min_npe = min_npe
        self.max_npe = max_npe
        self.min_radius = min_radius_meters
        self.max_radius = max_radius_meters
        self.min_ellipticity = min_ellipticity
        self.max_ellipticity = max_ellipticity

        self.min_num_pixels = min_num_pixels

    def hillas_parameters(self, image):
        hillas_params = get_hillas_parameters(self.geom1d, image, self.hillas_implementation)
        return hillas_params

    def hillas_ellipticity(self, image, hillas_params):
        length = hillas_params.length.value
        width = hillas_params.width.value

        if length == 0:
            ellipticity = 0
        else:
            ellipticity = width / length

        return ellipticity

    def hillas_centroid_dist(self, image, hillas_params):
        x = hillas_params.cen_x.value
        y = hillas_params.cen_y.value

        return math.sqrt(x**2 + y**2)

    def __call__(self, images2d):
        ref_image_2d = images2d.reference_image  # TODO !!!!!!!!!!
        ref_image_1d = geometry_converter.image_2d_to_1d(ref_image_2d, self.cam_id)
        hillas_params = self.hillas_parameters(ref_image_1d)

        npe_contained = self.min_npe < np.nansum(ref_image_1d) < self.max_npe
        ellipticity_contained = self.min_ellipticity < self.hillas_ellipticity(ref_image_1d, hillas_params) < self.max_ellipticity
        radius_contained = self.min_radius < self.hillas_centroid_dist(ref_image_1d, hillas_params) < self.max_radius
        num_pixels_contained = self.min_num_pixels <= np.sum(ref_image_1d > 0)

        return not (npe_contained and ellipticity_contained and radius_contained and num_pixels_contained)