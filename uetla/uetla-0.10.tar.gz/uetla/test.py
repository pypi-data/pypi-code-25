

import pickle

model = pickle.load(open('../test/15w_classification_8','rb'))
print(model.classes_)