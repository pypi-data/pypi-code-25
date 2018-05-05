from tec.ic.ia.p1.models.Model import Model
import numpy as np
from collections import Counter

""" 
This model creates a knn kd tree to predict votes in 1st and 2nd round
"""


class KNearestNeighbors(Model):
    def __init__(self, samples_train, samples_test, prefix, k):
        super().__init__(samples_train, samples_test, prefix)
        self.k = k
    """
    Recursive function that creates the kd tree using a dictionary.
    Input: The samples being distributed and the dimension of the tree.
    Output: A dictionary containing the built tree.
    """
    def create_kdtree(self, samples, level=0):
        # The samples' informaction is separated.
        samples_data = samples[0]
        samples_vote = samples[1]
        n = len(samples_data)
        # If there are no samples
        if n <= 0:
            return None
        # The splitting attribute to make the two branches is chosen
        breaking_point = level % len(samples_data[0])
        # The samples are ordered so they can be separated for the two branches
        ordered_samples, ordered_votes = (list(t) for t in zip(
            *sorted(zip(samples_data, samples_vote), key=lambda pair: pair[0][breaking_point])))
        half = round(n / 2)
        # A tree node is built containing its sample, its votes, and its left
        # and right branches (which are built recursively)
        return {
            'sample': ordered_samples[half],
            'vote': ordered_votes[half],
            'left_son': self.create_kdtree([ordered_samples[:half], 
                ordered_votes[:half]], level + 1),
            'right_son': self.create_kdtree([ordered_samples[half + 1:],
                ordered_votes[half + 1:]], level + 1)
        }

    """
    Function that calculates the Manhattan Distance (L1) between two points.
    Input: The two points being measured.
    Output: A float,the distance between the points.
    """
    def calculate_manhattan_distance(self, p1, p2):
        return sum(abs(x - y) for x, y in zip(p1, p2))

    """
    Recursive function that looks for the k closest points to the one being
    classified.
    Input: The root of the kd tree, the point being classified and the current
    level of the tree.
    Output: A list containing the list of votes of the closest points, and a
    list of their distances to the point.
    """
    def kdtree_closest_point(self, root, point, level=0):
        knn_best = []
        knn_distances = []
        # If root's parent is a leaf
        if root is None:
            return None
        # The attribute is chosen to classify the point into a branch (the same
        # attribute chosen for the tree building)
        axis = level % len(point)
        next_branch = None
        opposite_branch = None
        # The next_branch corresponds to the branch to which the point being 
        # classified belongs.
        # The opposite_branch is the other branch.
        if point[axis] < root['sample'][axis]:
            next_branch = root['left_son']
            opposite_branch = root['right_son']
        else:
            next_branch = root['right_son']
            opposite_branch = root['left_son']
        # The distanche between the root and the classified point is
        # calculated.
        root_distance = self.calculate_manhattan_distance(
            point, root['sample'])
        # The closest k points in the next_branch are calculated recursively.
        best_next = self.kdtree_closest_point(next_branch, point, level + 1)
        if best_next is None:
            best_next = [[], []]
        knn_best = best_next[0] + [root['vote']]
        knn_distances = best_next[1] + [root_distance]
        # The closest neighbors are ordered by distance.
        knn_distances, knn_best = (list(t) for t in zip(
            *sorted(zip(knn_distances, knn_best), key=lambda pair: pair[0])))
        # If the distance from the point to the root in the axis dimension is
        # lower than the greatest k best distance, the closest k points in the
        # opposite_branch are calculated recursively.
        best_opposite = []
        if abs(point[axis] - root['sample'][axis]
               ) < knn_distances[:self.k][-1]:
            best_opposite = self.kdtree_closest_point(
                opposite_branch, point, level + 1)
            if best_opposite is None:
                best_opposite = [[], []]

            knn_best += best_opposite[0]
            knn_distances += best_opposite[1]
            # The closest neighbors are ordered by distance.
            knn_distances, knn_best = (list(t) for t in zip(
                *sorted(zip(knn_distances, knn_best), key=lambda pair: pair[0])))
        # Only the k closest neighbors are returned.
        return [knn_best[:self.k], knn_distances[:self.k]]

    """
    Function that its called to execute the model. It creates the tree, and tests 
    it using the training and testing set.
    Input: -
    Output: A list containing the predicted votes for the training and
    testing set.
    """
    def execute(self):
        print("\n\n----------KNN kdtree-----------\n\n")

        print("Cantidad ejemplos training: ", len(self.samples_train[0]))
        print("Cantidad ejemplos testing: ", len(self.samples_test[0]), "\n\n")

        tree = self.create_kdtree(self.samples_train)
        pred_votes = []

        print("Arbol Creado!")
        print("Empezando el recorrido del arbol para metricas")
        # Measures error with training data
        p_results = 0
        n_results = 0
        for i in range(0, len(self.samples_train[0])):
            # Tests point agains kd tree and takes the predited votes
            knn_result = self.kdtree_closest_point(
                tree, self.samples_train[0][i])
            votes = knn_result[0]
            data = Counter(votes)
            sample_result = self.samples_train[1][i]
            pred_result = max(votes, key=data.get)
            # Compares the predited votes against real ones
            if sample_result == pred_result:
                p_results += 1
            else:
                n_results += 1
            pred_votes.append(pred_result)
        print("Training set")
        print("Aciertos: ", p_results, " De: ", len(self.samples_train[0]), " Accuracy: ",
              p_results / len(self.samples_train[0]))
        # Measures error with testing data
        p_results=0
        n_results=0
        for i in range(0, len(self.samples_test[0])):
            # Tests point agains kd tree and takes the predited votes
            knn_result=self.kdtree_closest_point(
                tree, self.samples_test[0][i])
            votes=knn_result[0]
            data=Counter(votes)
            sample_result=self.samples_test[1][i]
            pred_result=max(votes, key = data.get)
            # Compares the predited votes against real ones
            if sample_result == pred_result:
                p_results += 1
            else:
                n_results += 1
            pred_votes.append(pred_result)
        print("Testing set")
        print("Aciertos: ", p_results, " De: ", len(self.samples_test[0]), " Accuracy: ",
              p_results / len(self.samples_test[0]))
        return pred_votes
