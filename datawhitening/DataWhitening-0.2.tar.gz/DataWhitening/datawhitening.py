#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:39:19 2016

@author: SB
"""

import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import itertools
import time
import sys


class Collection_points(object):

    def __init__(self):
        self.min = []
        self.max = []

    def stat(self, **kwargs):
        """

        :param kwargs:
        min and max can be given manually or through an example dataset
        """
        if 'data' in kwargs.keys():
            self.min = np.min(kwargs['data'], axis=0)
            self.max = np.max(kwargs['data'], axis=0)
        elif 'min' in kwargs.keys():
            self.min = kwargs['min']
            self.max = kwargs['max']
        else:
            sys.exit('Wrong input format')

    def generate_points(self, observation, num_points, num_dim):

        try:
            observation.shape[1]
            sys.exit('observation must be an array of shape (N,)')
        except IndexError:
            print('')



        if any([len(self.min) == 0, len(self.max) == 0]):
            sys.exit('Hyperspace boundaries missing. Please feed data or boundaries through .stat method')

        dimension = observation.shape[0]
        perturbations = MultiLabelBinarizer().fit_transform(list(itertools.combinations(list(range(dimension)), num_dim)))
        neighbours = np.asmatrix([observation.ravel(), ] * (num_points * perturbations.shape[0]))

        for perm in range(perturbations.shape[0]):
            id_c = np.where(np.array(perturbations[perm, :]) == 1)[0]
            c = np.random.uniform(self.min[id_c], self.max[id_c], size=(num_points, num_dim))
            neighbours[perm * num_points:(perm + 1) * num_points, id_c] = c

        # Adjust PChanges
        perturbations = np.repeat(perturbations, num_points, axis=0)

        self.observation = observation
        self.neighbours = neighbours
        self.perturbations = perturbations

    def whitening(self, predictor_method, target, Verbose=False):

        start = time.time()
        neighbours_classification = predictor_method(self.neighbours)

        matches = np.where(neighbours_classification == target)[0]

        #nb_matches = len(matches)
        if len(matches) == 0:

            end = time.time()
            if Verbose:

                print('Scan of hyperspace lasted ',end - start, ' seconds')
                print('No tested perturbation affect the observation classification')
            return {}

        else:
            opposed_class_neighbours = self.neighbours[matches, :]
            orden = np.linalg.norm(np.subtract(opposed_class_neighbours , self.observation),axis=1).argsort()
            closest_solution = opposed_class_neighbours[orden[0],:]
            perturbation_summary = self.perturbations[matches, :]
            perturbation_solution = perturbation_summary[orden[0], :]
            end = time.time()
            if Verbose:
                print('Scan of hyperspace lasted ',end - start, ' seconds')
                print(len(matches), ' solutions have been found')



            return {'closest_solution':closest_solution,
                    'perturbation_solution':perturbation_solution,
                    'all_solutions':opposed_class_neighbours,
                    'perturbation_summary':perturbation_summary.sum(axis=0)}


