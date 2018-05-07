import numpy as np
import vaex.ml.lightgbm
from memory_profiler import profile

@profile
def run():
	param = {'num_leaves':10, 'num_trees':10, 'objective':'softmax', 'num_class': 3}
	num_round = 10  # the number of training iterations
	ds = vaex.ml.iris_1e8()
	features = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
	classifier = vaex.ml.lightgbm.LightGBMClassifier(num_round=10, param=param,
                                       features=vaex.dataset._ensure_strings_from_expressions(features))
	ds_train = ds # use everything
	classifier.fit(ds_train, ds_train.class_, copy=False)

if __name__ == '__main__':
	run()
	# ds_t = classifier.transform(ds)
	# same = ds_t.lightgbm_prediction.evaluate() == ds.class_.evaluate()
	# print(ds_t.lightgbm_prediction.evaluate())
	# print(ds.class_.evaluate())
	# print(same)
	# print("{}%% correct".format(np.sum(same)/len(same) * 100))
