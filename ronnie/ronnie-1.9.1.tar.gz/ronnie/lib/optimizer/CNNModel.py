#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# LICENSE 	   : MIT
# Version      : 1.9.x
# Summary      : CNNModel Constructor : integrated to TensorFlow
#			   : Transform *multi*,*auto detected sizes* images from csv by 1 line of code
# Description  : Default Input Format:1st column : Label, the rest of columns : Image Pixels 
#############################################################################################
import sys
import pandas 				as pd
import numpy 				as np
import logging

import tensorflow 			as tf

import 	ronnie.meta 					as meta
import 	ronnie.lib.util 				as util
import  ronnie.lib.monitor.custError	as cError

import 	ronnie.lib.monitor.logKeeper  	as lk
import  ronnie.lib.monitor.plottor		as plottor

#lk.initial()

logger = logging.getLogger("roNNie")

def activationFct(act):
	logger.debug("activationFct input {0}".format(act))
	result = None 
	if act == meta.MODEL_ACT_RELU:
		result = tf.nn.relu
	elif act == meta.MODEL_ACT_SIGMOID:
		result = tf.sigmoid
	elif act == meta.MODEL_ACT_TANH:
		result = tf.tanh
	else:
		result = None
	
	logger.debug("activationFct result {0}".format(result))
	return result

def actUnit(inputs, act):
	logger.debug("actUnit input {0}".format(act))
	
	result = None 
	
	if act in (meta.MODEL_ACT_RELU,meta.MODEL_ACT_SIGMOID, meta.MODEL_ACT_TANH,""):
		if act == meta.MODEL_ACT_RELU:
			result = tf.nn.relu(inputs)
		elif act == meta.MODEL_ACT_SIGMOID:
			result = tf.sigmoid(inputs)
		elif act == meta.MODEL_ACT_TANH:
			result = tf.tanh(inputs)
		elif act == "":
			result = inputs
		else:
			raise ValueError("Wrong Activation Type at actUnit {0}".format(act))
	else:
		raise ValueError ("WRONG {0}: Value {1}".format("act",act))
		
	logger.debug("actUnit result {0}".format(result))
	return tf.identity(result)

def batchNormUnit(inputs, mode):
	#actPosition (-1,0,1) : -1:Before ; 0:no activation 1:After
	try:	
		isTrain = True
		
		if not mode == tf.estimator.ModeKeys.TRAIN:
			isTrain = False
		bn = tf.layers.batch_normalization(imgXs, axis=3, training=isTrain)
        
		return tf.identity(bn)
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
	
def convLyr(imgXs, kernel,filter,padding, mode, stride=1,activation=tf.nn.relu):
#		strides=strides added at 1.9.x, default=1
	try:
		tensorImgXs = imgXs
		kr = None
		
		if type(kernel) is int or type(kernel) is tuple:
			kr = kernel
		else:
			raise ValueError ("KERNEL format error {0}".format(kernel))
		
		#Testing use, work well : 
		#CNNModel.printMatrixE(inputImgs)
		#CNNModel.printMatrixE(input_layer)
		#inStrides = [strides,strides]
		logger.debug("Convolution Layer : fct:convLyr:strides : {0}".format(stride))
		
		act = activationFct(activation)
		
		if act is None:
			conv = tf.layers.conv2d(inputs=tensorImgXs,	filters=filter,	kernel_size=kr,	strides=stride,	padding=padding)
			#TF V1.7 reference
			#tf.layers.conv2d(inputs, filters,kernel_size,
			#			strides=(1, 1),	padding='valid',data_format='channels_last', dilation_rate=(1, 1),
			#			activation=None, use_bias=True,	kernel_initializer=None,bias_initializer=tf.zeros_initializer(),
			#			kernel_regularizer=None,bias_regularizer=None,activity_regularizer=None,kernel_constraint=None,
			#			bias_constraint=None,trainable=True,name=None,reuse=None)
		else: 
			conv = tf.layers.conv2d(inputs=tensorImgXs,	filters=filter,	kernel_size=kr,	strides=stride,	padding=padding, activation=act)
		
		
		logger.debug("CNN Convolutional Layer was built : {0}".format(conv))
		#CNNModel.printMatrixE(baz)
			
		return tf.identity(conv)
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

# Pooling Layer 
# Example:
# Second max pooling layer with a 2x2 filter and stride of 2
# Input Tensor Shape: [batch_size, x, x, 16]
# Output Tensor Shape: [batch_size, x, x, 32]
# Would be better to define several poolsize and strides
def poolLyr(conv, size, strides, mode, padding=meta.PADDING_VALID, type=meta.POOL_MAX):
	try:
		
		logger.info("Input p size {0}".format(size))
		#tf.layers.max_pooling2d(inputs, pool_size,strides, padding='valid', data_format='channels_last', name=None)
		
		if not padding in (meta.PADDING_SAME, meta.PADDING_VALID):
			 raise ValueError ("WONG PADDING TYPE: SHOULD BE SAME, or VALID")
		
		
		pool = None
		if type in (meta.POOL_MAX, meta.POOL_AVG):
			if type == meta.POOL_MAX:
				pool = tf.layers.max_pooling2d(inputs=conv, pool_size=[size, size], strides=strides, padding=padding)
			else:
			#tf.layers.average_pooling2d(inputs,pool_size,strides, padding='valid',data_format='channels_last', name=None)
				pool = tf.layers.average_pooling2d(inputs=conv, pool_size=[size, size], strides=strides, padding=padding)
		else:
			raise ValueError ("WRONG POOL TYPE: SHOULD BE meta.POOL_MAX or meta.POOL_AVG")		
		logger.info(" CNN Pool Layer was built : {0}".format(pool))
		
		return tf.identity(pool)
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

# Dense Layer
# Example:
# Densely connected layer with 1024 neurons
# Input Tensor Shape: [batch_size, 7 * 7 * 64]
# Output Tensor Shape: [batch_size, 1024]
#inputs=pool2_flat (default) , pool1_flat changed to 1 layer
#try to submit optDict to DenseOpt
# units=10
def denseLyr(flatInput,optDict,index,mode):
	try:
		isTrain = True
		if not mode == tf.estimator.ModeKeys.TRAIN:
			isTrain = False
		
		logits = None 
		activation = None
		name = 'DENSE' + str(index)
		
		activation = activationFct(optDict[meta.MODEL_ACT])
		
		logger.debug ("actvation result is {0}".format(activation))
		tInput = flatInput
		if not float(optDict[meta.MODEL_DROPOUTRATE]) < 0:
				tInput = tf.layers.dropout(inputs=flatInput, rate=optDict[meta.MODEL_DROPOUTRATE], training=isTrain)
		#	logits = tf.layers.dense(inputs=dropout, units=optDict[meta.MODEL_NEURON],name=name)
		else:
			raise VaueError("DROPOUT RATE INCORRECT")
		if activation is None:
			logits = tf.layers.dense(inputs=tInput, units=optDict[meta.MODEL_NEURON],name=name)
			logger.debug("AcTIVATION IS NONE")
		else:
			logits = tf.layers.dense(inputs=tInput, units=optDict[meta.MODEL_NEURON], activation=activation,name=name)
			logger.debug("AcTIVATION NOT NONE")
				
		logger.debug(" CNN Dense Opt logits was built : {0}".format(logits))
		
		return tf.identity(logits)
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

		
def bnLyr(inputs, spec, mode, momentum=0.997, epsilon=1e-5, axis=-1, center=True, scale=True, fused=True):
	isTrain = True
	try:
		if not mode == tf.estimator.ModeKeys.TRAIN:
			isTrain = False
		if meta.MOMENTUM in spec:
			if spec[meta.MOMENTUM] >0 and spec[meta.MOMENTUM] < 1 :
				momentum = spec[meta.MOMENTUM]
		if meta.EPSILON in spec:
			epsilon = spec[meta.EPSILON]
		if  meta.AXIS in spec:
			if spec[meta.AXIS] in (-1,0,1,2,3):
				axis = spec[meta.AXIS]
		if  meta.CENTER in spec:
			if spec[meta.CENTER]in (0,1):
				center = spec[meta.CENTER]
		if meta.SCALE in spec:
			if spec[meta.SCALE]in (0,1):
				scale = spec[meta.SCALE]
		if meta.FUSED in spec:
			if spec[meta.FUSED]in (0,1):
				fused = spec[meta.FUSED]
	#######################################################################
	# API Reference:
	#######################################################################
	#tf.layers.batch_normalization(
	#      inputs=inputs, axis=1 if data_format == 'channels_first' else 3,
	#      momentum=, epsilon=, center=True,
	#      scale=True, training=training, fused=True)
		bn = tf.layers.batch_normalization(inputs,momentum=momentum,epsilon=epsilon, training=isTrain, axis=axis, center=center, scale=scale, fused=fused)
		
		bn = actUnit(bn, spec[meta.MODEL_ACT])
	
		return tf.identity(bn)
	
	except ValueError as vE: 
		raise ValueError ("!!! Value ERROR {0}".format(vE))
	
	
def modelTower(inputs, tower, mode):
	towerTops = []
	logger.debug("[INNNER TOWER] - ModelDef : ModelTower test for inception")
	logger.debug("[INNNER TOWER] - ModelDef :meta.MODEL : TOWER TYPE : {0}".format(tower[0][meta.TOWER_TYPE]))
	mBlocks = tower[0][meta.TOWER_BLOCKS]
	
	for i in range(0,len(mBlocks)):
		logger.debug("[INNNER TOWER] - ModelDef :meta.MODEL : meta.TOWER_BLOCK {0} : {1}".format(i, mBlocks[i]))
		
		tmTower = lyrMgr(inputs,mBlocks[i],mode)
		logger.debug("[INNNER TOWER] - LEN (tmTower) : {0} ".format(len(tmTower)))
		
		for j in range (0, len(tmTower)):
			logger.debug("[INNNER TOWER] - [meta.TOWER_BLOCKS][{0}][{1}]".format(i, j))
			logger.debug("[INNNER TOWER] - tmTower output :  {0}".format(tmTower[j]))
			
			logger.debug("[INNNER TOWER] - inceptTower.modelTower[0][meta.TOWER_BLOCKS][{0}][{1}] : {2}".format(i, j,tower[0][meta.TOWER_BLOCKS][i][j]))
			if j == len(tmTower)-1:
				towerTops.append(tower[0][meta.TOWER_BLOCKS][i][j][meta.LAYER_BRICK])
				logger.debug("[INNNER TOWER] - TOP BLOCK [{0}][{1}] : {2}".format(i, j,tower[0][meta.TOWER_BLOCKS][i][j]))	
		
	return tower, towerTops
	
def resTower(inputs, tower, mode):

	tower,towerTops = modelTower(inputs, tower, mode)
	
	##meta.TOWER_TYPE : meta.RESNET,
	##meta.MERGE_TYPE	: meta.MERGE_ADD,
	res = None
	logger.debug("##################################################################")
	logger.debug("RESTOWER : INPUT {0}".format(inputs))
	logger.debug("RESTOWER : OUTPUT {0}".format(towerTops))
	
	shortcut = inputs
	
	if len(towerTops) > 1:
		shortcut = towerTops[1]
		logger.debug("RESTOWER : 2 TOWERs")	
	else:
		logger.debug("RESTOWER : DIRECT INPUT")	
	
	logger.debug("RESTOWER : BEFORE ADD")	
	if tower[0][meta.MERGE_TYPE] == meta.MERGE_ADD:
		res = tf.add(shortcut,towerTops[0])
		logger.debug("RESTOWER : ADD PROCESS DONE")	
	else:
		raise ValueError("WRONG Resnet Merge Type {0}".format(meta.MERGE_ADD))
	##meta.MODEL_ACT	: meta.MODEL_ACT_RELU,		
	logger.debug("##################################################################")
	logger.debug("RES TOWER OUTPUT : {0}".format(res))
	
	logger.debug("#*# RESTOWER MODEL_ACT TYPE : {0}".format(tower[0][meta.MODEL_ACT]))
	res = actUnit(res, tower[0][meta.MODEL_ACT])
	logger.debug("RES TOWER DETAIL : AFTER ACTIVATION : {0}".format(res))
####sys.exit(1)
	return tower, tf.identity(res)

def inceptTower(inputs, tower, mode):
	
	tower,towerTops = modelTower(inputs, tower, mode)
	
	incept = tf.concat(towerTops, axis=3)
					
	return tower, tf.identity(incept)

def lyrMgr(imgXs, modelTower, mode):
	try:
		#tf.estimator.ModeKeys.*
		#TRAIN: training mode.
		#EVAL: evaluation mode.
		#PREDICT: inference mode.
		if len(modelTower) == 0:
			raise cError.ModelError("No Defined Layer. Please check Model Tower.")
		if mode not in (tf.estimator.ModeKeys.TRAIN, tf.estimator.ModeKeys.EVAL, tf.estimator.ModeKeys.PREDICT):
			raise ValueError("!!! Mode should not be tf.estimator.ModeKeys.{0}".format(mode))
		
		imgXs = tf.cast(imgXs, tf.float32)
		
		for index in range(len(modelTower)):
			spec = modelTower[index][meta.LAYER_SPEC]
			logger.debug("Spec : {0}".format(spec))
			input = imgXs
			denseLyrCounter = 0
			
			if not index == 0:
				input = modelTower[index-1][meta.LAYER_BRICK]
			
			logger.debug("Index : {0}, INPUT BRICK {1}".format(index,input))
			
			if spec[meta.LAYER_TYPE] == meta.CONV_LAYER:
				logger.debug("Index : {0}, CON : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				#added conStride at 1.9.x
				conStride = 1
				if meta.CON_STRIDE in spec:
					conStride = spec[meta.CON_STRIDE]
				logger.debug("Convolution Layer : Stride : {0}".format(conStride))
				#convLyr(imgXs, kernel,filter,padding, mode, stride=1,activation=tf.nn.relu)
				conv = convLyr(input, spec[meta.CON_KERNAL], spec[meta.CON_FILTER], spec[meta.CON_PADDING],mode, conStride)
				logger.debug("Convolution Layer with Stride : DONE {0}".format(conv))
				modelTower[index][meta.LAYER_BRICK] = conv
				
			elif spec[meta.LAYER_TYPE] == meta.POOL_LAYER:
				logger.debug("Index : {0}, Pool : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				type=meta.POOL_MAX
				#Add padding and stride at 1.9.x for GoogLeNet
				if meta.POOL_TYPE in spec:
					type=spec[meta.POOL_TYPE]
					
				padding = meta.PADDING_VALID	
				
				if meta.PADDING_TYPE in spec:
					padding=spec[meta.PADDING_TYPE]
				
				#poolLyr(conv, size, strides, mode, padding=meta.PADDING_VALID, type=meta.POOL_MAX)
				pol = poolLyr(input, spec[meta.POOL_KERNAL], spec[meta.POOL_STRIDE],mode, type=type, padding=padding)
				modelTower[index][meta.LAYER_BRICK] = pol
											
			elif spec[meta.LAYER_TYPE] == meta.DENSE_LAYER:
				logger.debug("Index : {0}, DENSE : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				denseLyrCounter += 1
				if index == 0 or not modelTower[index-1][meta.LAYER_SPEC][meta.LAYER_TYPE] == meta.DENSE_LAYER:
					logger.debug("ModelTower : Dense Layer before flatten : {0}".format(input))
					logger.debug("ModelTower : Dense Layer input shape : {0}".format(input.get_shape()))
					logger.debug("ModelTower : Dense Layer input shape : {0} | {1} | {2}  ".format(input.get_shape()[1],input.get_shape()[2],input.get_shape()[3] ))
					flattenShape = input.get_shape()[1]*input.get_shape()[2]*input.get_shape()[3] 
					logger.debug("ModelTower : Dense Layer expected flatten shape : {0} ".format(flattenShape ))
					
					logger.debug("ModelTower : Dense Layer before flatten : {0}".format(input))
					input = tf.reshape(input , [-1,flattenShape])
					# bugs at layers.flatten
					#input = tf.contrib.layers.flatten(input)
					logger.debug("Data Flattening : Shape {0}".format(input ))
	
				#denseLyr(flatInput,optDict,index,mode)
				dense = denseLyr(input, spec, index,mode)
				modelTower[index][meta.LAYER_BRICK] = dense			
##############################################################################################################################
#				#Add INCEPT_LAYER, ResLayer, BatchNormLyr at 1.9.x
##############################################################################################################################
			elif spec[meta.LAYER_TYPE] == meta.BATCHNORM_LAYER:

				bn = bnLyr(input, spec, mode)

				modelTower[index][meta.LAYER_BRICK] = bn
				
			elif spec[meta.LAYER_TYPE] == meta.INCEPT_LAYER:
				logger.debug("******************************************************************")
				logger.debug("MAIN Index : {0}, INCEPT : Lyr Type {1}".format(index,spec[meta.LAYER_TYPE] ))
				logger.debug("******************************************************************")
						
				inceptTowers = spec[meta.INCEPT_TOWER]
				logger.debug("Index : {0}, [INCEPT INNNER TOWER] -  : SPEC {1}".format(index,inceptTowers))
				logger.debug("[INCEPT INNNER TOWER] - ModelDef : Tower TYPE: {0}".format(inceptTowers[0][meta.TOWER_TYPE]))
				
				inceptTowers, incept = inceptTower(input, inceptTowers, mode)
					
				logger.debug("******************************************************************")
				logger.debug("OUTPUT: [INCEPT INNNER TOWER] -  incept Detail :{0}".format(incept))
				logger.debug("******************************************************************")
				logger.debug("[INCEPT INNNER TOWER] - incept Shape :{0}".format(incept.shape))
			
				modelTower[index][meta.LAYER_BRICK] = incept		
					#logger.debug("INCEPTION LYR : {0}".format(modelTower[index]))
				#V1.9.x testing use
				#		sys.exit(1)
	
			elif spec[meta.LAYER_TYPE] == meta.RESNET_LAYER:
				resTowers = spec[meta.RES_TOWER]
				resTowers, resnet = resTower(input, resTowers, mode)
				
				modelTower[index][meta.LAYER_BRICK] = resnet	
				
			else:
				raise cError.ModelError("Layer Type is missing")
	
		logger.info("#################################################################")		
		logger.info("#ModelTower was built. Details:")
		logger.info("#################################################################")		
		for index in range(len(modelTower)):
			logger.debug( "# Layer-{0} : Type:{1} : lyr Spec : {2}".format(index, modelTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE], modelTower[index][meta.LAYER_SPEC]))
			logger.info( "# Layer-{0} : Type:{1} ".format(index, modelTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE]))
			logger.debug("#lyr brick : {0}".format(modelTower[index][meta.LAYER_BRICK]))	
		
		logger.debug("#################################################################")		
			
		#V1.8.x will double check whether denseLyr
		#V1.9.x Not All CNN Model has denseLyr, remove the verification
		#if denseLyrCounter < 1:
		#	raise cError.ModelError("No Dense Layer. Please Review the Model Tower.")
			
		return modelTower
	except cError.ModelError as mE:
		logger.error("ERROR : {0}".format(mE))
		sys.exit(1)
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise  

def initialEnvironment():
	with tf.Session() as sess:	
		logger.info("Start Initial Evironment...")
		init_op = tf.global_variables_initializer()
		logger.debug("init_op is {0}".format(init_op))
		sess.run(init_op)
		logger.info("Session initialized")

def modelDetails(mTower, pid=0):
	cLayers = 0
	pid += 1
	spacing = ""
	for i in range (1, pid):
		spacing = spacing + "+---"
				
	for index in range(len(mTower)):
		cLayers +=1
		if not mTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE] in (meta.RESNET_LAYER, meta.INCEPT_LAYER):
			logger.info( "{3}# Level-{0} Layer - {1} : Type: {2}".format(pid, index, mTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE], spacing))
		else:
			logger.info( "{3}# Level-{0} Layer - {1} : Type: {2}".format(pid, index, mTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE], spacing))
			tower = None
			if mTower[index][meta.LAYER_SPEC][meta.LAYER_TYPE] == meta.RESNET_LAYER:
				tower = mTower[index][meta.LAYER_SPEC][meta.RES_TOWER][0][meta.TOWER_BLOCKS][0]
			else:
				tower = mTower[index][meta.LAYER_SPEC][meta.INCEPT_TOWER][0][meta.TOWER_BLOCKS][0]
			
			modelDetails(tower, pid)
			
			cLayers +=1
			
	logger.info( "#Total Layers : {0}".format(cLayers))	
		
def modelSummary(mTower):
	logger.info("##############################################################################")
	logger.info("#MODEL SUMMARY")
	logger.info("##############################################################################")
	modelDetails(mTower)
	logger.info("##############################################################################")
		
def initialModel(imgXs,modelDef):

	dataCfg = modelDef[meta.DATA_CONFIG]
	modelTower = modelDef[meta.MODEL]
	graph = tf.Graph()
	
	ph_imgXs = None
	ph_labelYs = None
	
	ph_imgXs = tf.placeholder(tf.float32, shape=(None,dataCfg[meta.DATA_IMGX_WIDTH],dataCfg[meta.DATA_IMGX_HEIGHT],dataCfg[meta.DATA_IMGX_CHANNEL]))
	ph_labelYs = tf.placeholder(tf.int32, shape=(None,dataCfg[meta.DATA_LABELY_CLASSs]))
	
	modelTower = lyrMgr(ph_imgXs,modelTower,mode)
	
	logger.info("imgXs obj {0}".format(imgXs))	
	logger.debug("Trying Model with PH")
#	modelTower = modelDef[meta.MODEL]
	phLogits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]
	
	logger.debug("Trying Model with PH")
	
	with tf.Session() as sess:	
		a = sess.run(phLogits,feed_dict={ph_imgXs:imgXs})
	
	logger.debug("Success")
	
	return modelTower

def tryModel(imgXs, modelDef):
	logger.debug("Trying Model with PH")
	modelTower = modelDef[meta.MODEL]
	phLogits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]
	with tf.Session() as sess:
		modelTower = sess.run(phLogits,feed_dict={"ph_imgXs":imgXs*1.0})
	logger.debug("Trying Model with PH")
	return
######after 1.1.x version	

def statDictResult(targets,predicts, classes):
	dResult = {}
	for i in range (classes):
		dResult.update({i:{"T" : 0 , "F":0}})
		
	iL = 0
	logger.debug("CHECK OBJECT dResult : {0}".format(dResult))
	logger.debug("CHECK OBJECT targets shape: {0}".format(targets.shape))
	logger.debug("CHECK OBJECT predicts shape: {0}".format(predicts.shape))
	for i in range (targets.shape[0]):
		iL = tf.cast(targets[i],tf.int32)
		logger.debug("CHECK OBJECT iL: {0}".format(iL))
		if targets[i] == predicts[i]:
			dResult[iL]["T"] +=1
		else:
			dResult[iL]["F"] +=1
	
	return dResult
	
def run(features, labels, mode, params):
	imgXs = features
	logger.debug("at RUN: CHECK TYPE: InputX(dtype) : {0} ".format(features.dtype))

	modelTower = params[meta.MODEL]
	logits = None
	#BUILD CNNMODEL
	logging.debug("imgXs shape {0}".format(imgXs.shape))
	
#add mode to lyrMgr-> fix the mode control at different layer	
	modelTower = lyrMgr(imgXs,modelTower,mode)
#	modelTower = lyrMgr(ph_imgXs,modelTower)
	
	logger.debug("len of modelTower : {0} ".format(len(modelTower)))
	
	logits = modelTower[len(modelTower)-1][meta.LAYER_BRICK]

	#End : Structure of CNN
	logger.info("Logits is {0}".format(logits))
			
	if mode == tf.estimator.ModeKeys.TRAIN:		
		learning_rate = None
				
		if meta.MODEL_LEARNRATE in dict(params):
			learning_rate = params[meta.TRAIN_CONFIG][meta.MODEL_LEARNRATE] 
		else:
			learning_rate = 0.001		
		
		distance = tf.losses.softmax_cross_entropy(onehot_labels=labels, logits=logits)
	
	
####ADAM and GD are the optimizers good at begining
		if params[meta.TRAIN_CONFIG][meta.OPTIMIZER] == meta.OPTIMIZER_ADAM:
			optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)	
		elif params[meta.TRAIN_CONFIG][meta.OPTIMIZER] == meta.OPTIMIZER_GD:
			optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)	
		
		################################################################
		#optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
		#rho: tensor或者浮点数. The decay rate. 
		#add decay rate(rho) for Adadelta
		#tf.train.AdagradOptimizer(learning_rate				, initial_accumulator_value=0.1, use_locking=False, name=’Adagrad’)
		#tf.train.MomentumOptimizer(learning_rate				, momentum, use_locking=False, name=’Momentum’, use_nesterov=False)
		#tf.train.AdadeltaOptimizer.init(learning_rate=0.001	, rho=0.95, epsilon=1e-08, use_locking=False, name=’Adadelta’)
		#tf.train.RMSPropOptimizer(learning_rate				,decay=0.9, momentum=0.0, epsilon=1e-10,use_locking=False, name=’RMSProp’)
		#tf.train.AdamOptimizer(learning_rate=0.001				, beta1=0.9, beta2=0.999, epsilon=1e-08, use_locking=False, name=’Adam’)
		#tf.train.FtrlOptimizer(learning_rate					, learning_rate_power=-0.5, initial_accumulator_value=0.1, l1_regularization_strength=0.0,l2_regularization_strength=0.0,use_locking=False, name=’Ftrl’)
		################################################################
		####DOUBLE CHECK update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
		####DOUBLE CHECK train_op = None
		####DOUBLE CHECK with tf.control_dependencies(update_ops):
#V1.9.x		
		#train_op = optimizer.minimize(loss=distance,global_step=tf.train.get_global_step())
		train_op = None
		update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
		logger.debug("******************************************")
		logger.debug("Update Ops :{0}".format(update_ops))

		with tf.control_dependencies(update_ops):
			train_op = optimizer.minimize(loss=distance,global_step=tf.train.get_global_step())
		
			
		logger.debug("CHECK TYPE: logits(dtype):{0}".format(logits.dtype))
		
		####testinggggggg 20180405
		
##		if params[meta.BASIC_CONFIG][meta.BYTES]==meta.BYTES32:
## and lyrMgr has casting of dType
		
		predicts = tf.argmax(input=(logits), axis=1,output_type=tf.int32)
				
		#tf.cast(predicts, tf.int32)
		
		vLabels = tf.argmax(input=(labels), axis=1,output_type=tf.int32)
		
		bResult = tf.equal(predicts,vLabels)
		logger.debug("CHECK TYPE: bResult(dtype):{0}".format(bResult.dtype))
		
		#acc = tf.equal(vLabels, predicts)
		accuracy = tf.reduce_mean(tf.cast(bResult, tf.float32))
		logger.debug("CHECK TYPE: accuracy(dtype):{0}".format(accuracy.dtype))							  
		#accRMean = tf.reduce_mean(tf.cast(accuracy, tf.float32))
		
		nTrue = tf.cast(tf.count_nonzero(bResult),tf.int32)
		logger.debug("CHECK TYPE: nTrue(dtype):{0}".format(nTrue.dtype))	
		nSize = tf.cast(tf.size(bResult),tf.int32)
		logger.debug("CHECK TYPE: nSize(dtype):{0}".format(nSize.dtype))
		calAcc = tf.cast(nTrue/nSize,tf.float32)
		logger.debug("CHECK TYPE: calAcc(dtype):{0}".format(calAcc.dtype))
		
		#Top_K use vLabels
		#tf.metrics.mean_per_class_accuracy(labels, predictions,num_classes,weights=None, metrics_collections=None, updates_collections=None, name=None)
		top2acc = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=vLabels, k=2), tf.float32))		
		top3acc = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=vLabels, k=3), tf.float32))
		top5acc = tf.reduce_mean(tf.cast(tf.nn.in_top_k(predictions=logits, targets=vLabels, k=5), tf.float32))
		
		#accOpt = tf.metrics.accuracy(labels=labels, predictions=predicts, name='accOpt')
		#metrics = {'Acc': accOpt}
		#eval_metric_ops = { "accuracy" : metrics }
		
		train_group = tf.group(train_op, accuracy)
		
		metrics = {'optimizer': train_op,'accuracy': accuracy}
		
		
		#logging_hook = tf.train.LoggingTensorHook({"3D-Distance" : distance}, every_n_iter=1)
		logging_hook = tf.train.LoggingTensorHook({"3D-Distance" : distance,"Accuracy(%)": accuracy, 
							"top2acc(%):":top2acc, "top3acc(%):":top3acc,"top5acc(%):":top5acc,
							"Predicts" : predicts,"labels : " : vLabels,
							"Total :" : nSize, "nTrue :" : nTrue, "% :" : calAcc}, every_n_iter=1)
		predictions={
				'classes': tf.argmax(logits, axis=1) ,
				'predictions': tf.nn.softmax(logits,name="softmax_tensor")           
		}				
		return tf.estimator.EstimatorSpec(mode=mode,  predictions=predictions, loss=distance, train_op=train_group,  training_hooks = [logging_hook])
	
#add comments		
	elif mode == tf.estimator.ModeKeys.EVAL:
		#onehot_labels = tf.one_hot（labels ，num_classes = 5） 
		#tf.contrib.losses.softmax_cross_entropy（logits ，onehot_labels ，weight = weight）
		#distance = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
		
		distance = tf.losses.softmax_cross_entropy(onehot_labels=labels, logits=logits)
		
		predicts = tf.argmax(input=(logits), axis=1)
		vLabels =  tf.argmax(input=(labels), axis=1)
		
		accuracy = tf.metrics.accuracy(labels=vLabels,
                              predictions=predicts, name='accuracyOpt')
		
		perClassAcc = tf.metrics.mean_per_class_accuracy(vLabels, predicts, 10, name="perClassAcc")
		
		
		metrics = {'accuracy': accuracy,'perClassAcc': perClassAcc}
		
		#eval_ops = {"accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])}
		return tf.estimator.EstimatorSpec(mode=mode, loss=distance, eval_metric_ops=metrics)
		

#add comments
	elif mode == tf.estimator.ModeKeys.PREDICT:

		predicts = tf.argmax(input=(logits), axis=1)
		predictions = {'class_ids': predicts[:, tf.newaxis],
						'probabilities': tf.nn.softmax(logits),'logits': logits,}

		return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
	else:
		logger.ERROR("!!! WRONG MODE !!!")
		return

def trainN(imgXs, labelYs, paramDict, batch, steps):
	try:
		logger.debug("Part 4: Training")
		results=None
		logger.debug("Labels Distribution")
		logger.debug("#############################################################")
		unique_elements, counts_elements = np.unique(labelYs, return_counts=True)
		logger.debug("Frequency of unique values of the said array:")
		logger.debug(np.asarray((unique_elements, counts_elements)))
		logger.debug("#############################################################")
		with tf.Session() as sess:
		
			logger.debug("Initializing TF variables : SESS_accRMean")
		
			mnist_classifier = tf.estimator.Estimator(model_fn=run,params=paramDict, model_dir="./models/" + paramDict[meta.MODEL_NAME])
			
			logger.info("################################################################")	
			logger.info("Classifier Constructed")
			logger.info("batch = {0} steps = {1}".format(batch, steps))
			logger.info("ImgXs Shape = {0} LabelYs Shape = {1}".format(imgXs.shape, labelYs.shape))
			inputFn = tf.estimator.inputs.numpy_input_fn(x=imgXs, y=labelYs, 
															batch_size=batch, 
															num_epochs=None, shuffle=paramDict[meta.TRAIN_CONFIG][meta.SHUFFLE])
			####Training part
#log hook at	 training?
			#tensors_to_log = None
			#logging_hook = tf.train.LoggingTensorHook(tensors=tensors_to_log, every_n_iter=100)
			logger.info("training start")
			#, hooks=[logging_hook]
			result = mnist_classifier.train(input_fn=inputFn, steps=steps)
	
		logger.info("training end")
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return result

	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
		raise
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
			


def modelEval(imgXs, labelYs, paramDict):
#evaluation_hooks
	try:

		logger.info("Part 5: Evaluate")
		results=None
		with tf.Session() as sess:
			mnist_classifier = tf.estimator.Estimator(model_fn=run, params=paramDict, model_dir="./models/" + paramDict[meta.MODEL_NAME])
			
			evalInputFn = tf.estimator.inputs.numpy_input_fn(x=imgXs,y=labelYs,
													num_epochs=1,shuffle=paramDict[meta.EVAL_CONFIG][meta.SHUFFLE])
			
			#Classifier is different from Predict
			results = mnist_classifier.evaluate(input_fn=evalInputFn)
			
		logger.debug("eResult : {0}".format(results))
		return results
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise

		
def predictExport(pResults, modelDef):
	try:	
		predictions = list(pResults)
		predicted_classes = [p["class_ids"] for p in predictions]
		df=pd.DataFrame(predicted_classes, columns = ["Label"])
		df.insert(0, 'ImageId', range(1, len(df)+1))
		
		exportFullFilePath = util.getPath("exportPredict",modelDef[meta.MODEL_NAME])
		
		df.to_csv(exportFullFilePath, encoding=modelDef[meta.BASIC_CONFIG][meta.MODEL_EXPORT_ENCODE],index=False)
		
		
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise	

def modelPredict(imgXs, labelYs, modelDef, export=True):
	try:
		logger.info("Part 6: Predict")
		results = None
		modelDef[meta.TRAIN_CONFIG]
		with tf.Session() as sess:

			mnist_classifier = tf.estimator.Estimator(model_fn=run, params=modelDef, model_dir="./models/" + modelDef[meta.MODEL_NAME])
			
			inputPredictFn = tf.estimator.inputs.numpy_input_fn(x=imgXs,y=labelYs,
																				num_epochs=1,shuffle=False)
			
			#Classifier is different from Eval			
			pResults = mnist_classifier.predict(input_fn=inputPredictFn)
			
			logger.debug("pResult is {0}".format(pResults))
			
		if export:
			predictExport(pResults, modelDef)
			logger.info("Finished. PREDICTION data exported to {0}".format(modelDef[meta.BASIC_CONFIG][meta.MODEL_EXPORT_FILE]))
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return pResults
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
		
def trainNeval(trainData,evalData, modelDef, cycles=50, samples=5000, steps=1, withEval=True, evalSteps=10,exportOnly=True):
	try:
		arrEvalAcc = []
		arrEvalSteps = []
		eResult = None
		logger.debug("at trainNeval: CHECK TYPE: InputX(dtype) : {0} | LabelYs(dtype):{1}".format(trainData[meta.DATA_INPUTXs].dtype, trainData[meta.DATA_LABELYs].dtype))
	
		for index in range (0, cycles):
			logger.info("#############################################################")
			logger.info("Start : Part 2.3: Training Cycle {0}".format(cycles))
			logger.info("Labels Distribution")
			logger.info("#############################################################")
			unique_elements, counts_elements = np.unique(trainData[meta.DATA_LABELYs], return_counts=True)
			logger.info("Frequency of unique values:")
			logger.info(np.asarray((unique_elements, counts_elements)))
			logger.info("#############################################################")
			
			tResult = trainN(trainData[meta.DATA_INPUTXs],trainData[meta.DATA_LABELYs], modelDef, samples, steps)
			logger.info("tResult :{0}".format(tResult))

			logger.info("#############################################################")
			logger.info("Finished : Part 2.3: Training.{0}".format(tResult))
#############################################################		
#############################################################
#############Evaluation######################################
			logger.info("Start : Part 2.2: Model Evaluation.")
	
			logger.debug("Evaluation imgXs   Shape: {0} ".format(evalData[meta.DATA_INPUTXs].shape))
			logger.debug("Evaluation LabelYs Shape: {0} ".format(evalData[meta.DATA_LABELYs].shape))
			
			if withEval and index % evalSteps == 0:
				eResult = modelEval(evalData[meta.DATA_INPUTXs], evalData[meta.DATA_LABELYs], modelDef)
				
				logger.info("EVALUATION RESULT : {0}".format(eResult))
				
				plottor.appendModelAcc(modelDef[meta.MODEL_NAME], {"steps": eResult['global_step'],"acc" : eResult['accuracy'],"loss" : eResult['loss']})
				plottor.plotModelAcc(modelDef[meta.MODEL_NAME],exportOnly=exportOnly)
		
		
		logger.info("Enjoy! Email us your comments and credits. Thanks.")
		return eResult
	
	except ValueError as vE:
		logger.error("Values error({0})".format(vE))
	except:
		logger.error("Unexpected error: {}".format(sys.exc_info()[0]))
		raise
####################		
def main():
	return
if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	