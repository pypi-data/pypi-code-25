import os
import ctypes

import vaex
import xgboost.core
import numpy as np
import tempfile
import base64
import vaex.serialize
from . import state
import traitlets

#libpath = os.path.join(os.path.dirname(__file__), "vaex_ml_lib.cpython-35m-x86_64-linux-gnu.so")
#print(libpath)
#lib = ctypes.cdll.LoadLibrary(libpath)
lib = xgboost.core._LIB

class EXPRESSION_RESULT(ctypes.Structure):
     _fields_ = [
		 ("length", ctypes.c_longlong),
		 ("data", ctypes.POINTER(ctypes.c_float))
	 ]

EVALFUNC = ctypes.CFUNCTYPE(ctypes.c_int, (ctypes.c_char_p), ctypes.c_longlong, ctypes.c_longlong, ctypes.POINTER(EXPRESSION_RESULT))

@vaex.serialize.register
class XGBModel(state.HasState):
	'''XGBModel for vaex, using a faster memory saving copying mechanism'''

	features = traitlets.List(traitlets.Unicode())
	num_round = traitlets.CInt()
	param = traitlets.Dict()
	prediction_name = traitlets.Unicode(default_value='xgboost_prediction')


	def __call__(self, *args):
		data2d = np.vstack([arg.astype(np.float64) for arg in args]).T.copy()
		dmatrix = xgboost.DMatrix(data2d)
		return self.bst.predict(dmatrix)

	def transform(self, dataset):
		copy = dataset.copy()
		lazy_function = copy.add_function('xgboost_prediction_function', self)
		expression = lazy_function(*self.features)
		copy.add_virtual_column(self.prediction_name, expression, unique=False)
		return copy

	def fit(self, dataset, label, copy=True):
		if copy:
			data = np.vstack([dataset.evaluate(k).astype(np.float64) for k in self.features]).T
			label_data = dataset.evaluate(label)
			dtrain = xgboost.DMatrix(data, label_data)
		else:
			dtrain = VaexDMatrix(dataset, label, features=self.features)
		param = dict(self.param)
		self.bst = xgboost.train(param, dtrain, self.num_round)

	def predict(self, dataset, copy=True):
		if copy:
			data = np.vstack([dataset.evaluate(k) for k in self.features]).T
			dmatrix = xgboost.DMatrix(data)
		else:
			dmatrix = VaexDMatrix(dataset, features=self.features)
		return self.bst.predict(dmatrix)

	def state_get(self):
		filename = tempfile.mktemp()
		self.bst.save_model(filename)
		with open(filename, 'rb') as f:
			data = f.read()
		return dict(tree_state=base64.encodebytes(data).decode('ascii'),
			substate=super(XGBModel, self).state_get())

	def state_set(self, state):
		super(XGBModel, self).state_set(state['substate'])
		data = base64.decodebytes(state['tree_state'].encode('ascii'))
		filename = tempfile.mktemp()
		with open(filename, 'wb') as f:
			f.write(data)
		self.bst = xgboost.Booster(model_file=filename)

class VaexDMatrix(xgboost.DMatrix):
	def __init__(self, ds, label=None, features=None, selection=None, blocksize=10):
		super(VaexDMatrix, self).__init__(None)
		self.ds = ds
		self.features = features or self.ds.get_column_names(virtual=True)
		self.selection = selection
		self.blocksize = blocksize

		self.data_references = {}

		self.c_features = (ctypes.c_char_p * len(self.features))()
		self.c_features[:] = [k.encode() for k in self.features]

		self.c_evaluate = EVALFUNC(self.evaluate)

		self.handle = ctypes.c_void_p()
		rows = int(self.ds.count(selection=selection))
		batch_size = 1*1000*1000
		return_code = lib.create_dmatrix(self.c_features, len(self.features), rows, batch_size, self.c_evaluate, self.blocksize, ctypes.byref(self.handle))
		#lib.test_dmatrix(self.handle, 0)
		if label is not None:
			label = self.ds.evaluate(label)
			self.set_label_npy2d(label)

	def set_label_npy2d(self, label):
		"""Set label of dmatrix

		Parameters
		----------
		label: array like
		    The label information to be set into DMatrix
		    from numpy 2D array
		"""
		self.set_float_info_npy2d('label', label)

	def set_float_info_npy2d(self, field, data):
		"""Set float type property into the DMatrix
		   for numpy 2d array input

		Parameters
		----------
		field: str
		    The field name of the information

		data: numpy array
		    The array of data to be set
		"""
		data = np.array(data, copy=False, dtype=np.float32)
		c_data = data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
		xgboost.core._check_call(xgboost.core._LIB.XGDMatrixSetFloatInfo(self.handle,
		                                       xgboost.core.c_str(field),
		                                       c_data,
		                                       ctypes.c_uint64(len(data))))

	def evaluate(self, expression, i1, i2, result):
		try:
			expression = expression.decode()
			#print(expression, i1, i2)
			#print(result[0])
			data = self.ds.evaluate(expression, i1, i2) # TODO, support selections
			# keep a reference, since otherwise the memory is freed
			# and we overwrite the last reference, so that will be freed
			self.data_references[expression] = data = data.astype(np.float32) # TODO: think about masking, nan?
			#print(data, type(data), data.dtype)
			ptr = data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
			#print(ptr, ptr)
			result[0].length = len(data)
			result[0].data = ptr
			#print(result.data, result.length)
			#print(result)
			return 0 #EXPRESSION_RESULT(len(data), ptr)
		except (Exception, e):
			print('error', e)
