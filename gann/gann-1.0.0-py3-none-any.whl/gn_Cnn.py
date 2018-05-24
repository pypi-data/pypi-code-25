import cifar10_input
import tensorflow as tf
import numpy as np
import runga
import initparamobj
import saveparameters

'''
# 随机扰动值
mutation_value = {0: 0.1, 1: 0.1, 2: 1e-20, 3: 1e-12, 4: 0.1,
                  5: 0.4, 6: 0.3, 7: 0.2, 8: 0.2, 9: 0.2}
'''

data_dir = '../cifar10_data/cifar-10-batches-bin'
batch_size = 128


class CnnCifar10(object):
    def __init__(self, param_obj, batch_size_obj):
        self.gra = tf.Graph()
        with self.gra.as_default():
            self.batch_size = batch_size_obj
            self.image_holder = tf.placeholder(tf.float32, [self.batch_size, 24, 24, 3])
            self.labels_holder = tf.placeholder(tf.int32, [self.batch_size])

            self.w1_ = tf.placeholder(tf.float32, [5, 5, 3, 64])
            self.w2_ = tf.placeholder(tf.float32, [5, 5, 64, 64])
            self.w3_ = tf.placeholder(tf.float32, [2304, 384])
            self.w4_ = tf.placeholder(tf.float32, [384, 192])
            self.w5_ = tf.placeholder(tf.float32, [192, 10])

            self.b1_ = tf.placeholder(tf.float32, [64])
            self.b2_ = tf.placeholder(tf.float32, [64])
            self.b3_ = tf.placeholder(tf.float32, [384])
            self.b4_ = tf.placeholder(tf.float32, [192])
            self.b5_ = tf.placeholder(tf.float32, [10])

            global_step = tf.get_variable('global_step', [],
                                          initializer=tf.constant_initializer(0),
                                          trainable=False)

            self.weight1 = self.variable_with_weight_loss(param_obj.w[0], 0.0)
            self.kernel1 = tf.nn.conv2d(self.image_holder, self.weight1, [1, 1, 1, 1], padding='SAME')
            self.bias1 = tf.Variable(param_obj.b[0])
            self.conv1 = tf.nn.relu(tf.nn.bias_add(self.kernel1, self.bias1))
            self.pool1 = tf.nn.max_pool(self.conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')
            self.norm1 = tf.nn.lrn(self.pool1, bias=1.0, alpha=0.001 / 9.0, beta=0.75)

            self.weight2 = self.variable_with_weight_loss(param_obj.w[1], 0.0)
            self.kernel2 = tf.nn.conv2d(self.norm1, self.weight2, [1, 1, 1, 1], padding='SAME')
            self.bias2 = tf.Variable(param_obj.b[1])
            self.conv2 = tf.nn.relu(tf.nn.bias_add(self.kernel2, self.bias2))
            self.norm2 = tf.nn.lrn(self.conv2, bias=1.0, alpha=0.001 / 9.0, beta=0.75)
            self.pool2 = tf.nn.max_pool(self.norm2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

            reshape = tf.reshape(self.pool2, [self.batch_size, -1])
            self.weight3 = self.variable_with_weight_loss(param_obj.w[2], 0.004)
            self.bias3 = tf.Variable(param_obj.b[2])
            self.local3 = tf.nn.relu(tf.matmul(reshape, self.weight3) + self.bias3)

            self.weight4 = self.variable_with_weight_loss(param_obj.w[3], 0.004)
            self.bias4 = tf.Variable(param_obj.b[3])
            self.local4 = tf.nn.relu(tf.matmul(self.local3, self.weight4) + self.bias4)

            self.weight5 = self.variable_with_weight_loss(param_obj.w[4], 0.0)
            self.bias5 = tf.Variable(param_obj.b[4])
            self.logits = tf.matmul(self.local4, self.weight5) + self.bias5

            self.w1_update = tf.assign(self.weight1, self.w1_)
            self.w2_update = tf.assign(self.weight2, self.w2_)
            self.w3_update = tf.assign(self.weight3, self.w3_)
            self.w4_update = tf.assign(self.weight4, self.w4_)
            self.w5_update = tf.assign(self.weight5, self.w5_)

            self.b1_update = tf.assign(self.bias1, self.b1_)
            self.b2_update = tf.assign(self.bias2, self.b2_)
            self.b3_update = tf.assign(self.bias3, self.b3_)
            self.b4_update = tf.assign(self.bias4, self.b4_)
            self.b5_update = tf.assign(self.bias5, self.b5_)

            self.loss = self.loss_cal(self.logits, self.labels_holder)

            self.lr = tf.train.exponential_decay(
                learning_rate=0.1,
                global_step=global_step,
                decay_steps=int((50000 / 128) * 350 * n_task),
                decay_rate=0.1,
                staircase=True
            )
            self.train_op = tf.train.GradientDescentOptimizer(self.lr).\
                minimize(self.loss, global_step=global_step)
            self.top_k_op = tf.nn.in_top_k(self.logits, self.labels_holder, 1)

            self.init = tf.global_variables_initializer()

            self.sess = tf.Session(graph=self.gra)
            self.sess.graph.finalize()
            self.sess.run(self.init)

    def variable_with_weight_loss(self, init, wl):
        var = tf.Variable(init, dtype=tf.float32)
        if wl is not None:
            weight_loss = tf.multiply(tf.nn.l2_loss(var), wl, name='weight_loss')
            tf.add_to_collection('losses', weight_loss)
        return var

    def loss_cal(self, logits, labels):
        labels = tf.cast(labels, tf.int64)
        cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
            logits=logits, labels=labels, name='cross_entropy_per_example')
        cross_entropy_mean = tf.reduce_mean(cross_entropy)
        tf.add_to_collection('losses', cross_entropy_mean)
        return tf.add_n(tf.get_collection('losses'), name='total_loss')

    def run_update_w(self, w):
        return self.sess.run([self.w1_update, self.w2_update, self.w3_update, self.w4_update, self.w5_update],
                             feed_dict={self.w1_: w[0], self.w2_: w[1], self.w3_: w[2], self.w4_: w[3], self.w5_: w[4]})

    def run_update_b(self, b):
        return self.sess.run([self.b1_update, self.b2_update, self.b3_update, self.b4_update, self.b5_update],
                             feed_dict={self.b1_: b[0], self.b2_: b[1], self.b3_: b[2], self.b4_: b[3], self.b5_: b[4]})

    def run_train_op(self, x, y):
        self.sess.run(self.train_op,
                      feed_dict={self.image_holder: x, self.labels_holder: y})

    def run_logits(self, x, y):
        return self.sess.run(self.logits,
                             feed_dict={self.image_holder: x, self.labels_holder: y})

    def get_fitness(self, x, y):
        correct = self.sess.run(self.top_k_op, feed_dict={self.image_holder: x, self.labels_holder: y})
        return np.sum(correct) / self.batch_size

    def get_all_w(self):
        return self.sess.run([self.weight1, self.weight2, self.weight3, self.weight4, self.weight5])

    def get_all_b(self):
        return self.sess.run([self.bias1, self.bias2, self.bias3, self.bias4, self.bias5])


class CIFARInput(object):
    def __init__(self):
        self.gra_input = tf.Graph()
        with self.gra_input.as_default():
            self.images_train, self.labels_train = cifar10_input.distorted_inputs(
                data_dir=data_dir, batch_size=batch_size)
            self.images_test, self.labels_test = \
                cifar10_input.inputs(eval_data=True, data_dir=data_dir, batch_size=batch_size)
            self.final_images, self.final_label = \
                cifar10_input.inputs(eval_data=True, data_dir=data_dir, batch_size=10000)
            self.sess = tf.Session(graph=self.gra_input)
            self.sess.graph.finalize()
            tf.train.start_queue_runners(self.sess)

    def get_batch_train_data(self):
        return self.sess.run([self.images_train, self.labels_train])

    def get_batch_test_data(self):
        return self.sess.run([self.images_test, self.labels_test])

    def get_overall_test_data(self):
        return self.sess.run([self.final_images, self.final_label])


def ga_step_decay(step):
    '''
    if step < 100:
        ga_step = 2
    elif step < 260:
        ga_step = 5
    elif step < 360:
        ga_step = 10
    elif step < 390:
        ga_step = 20
    else:
        ga_step = 40
    '''
    return 1


w = [np.random.normal(scale=0.05, size=[5, 5, 3, 64]),
     np.random.normal(scale=0.05, size=[5, 5, 64, 64]),
     np.random.normal(scale=0.04, size=[2304, 384]),
     np.random.normal(scale=0.04, size=[384, 192]),
     np.random.normal(scale=1/192.0, size=[192, 10])]


b = [np.zeros((64, ), dtype=np.float32),
     np.ones((64,), dtype=np.float32) * 0.1,
     np.ones((384,), dtype=np.float32) * 0.1,
     np.ones((192,), dtype=np.float32) * 0.1,
     np.zeros((10,), dtype=np.float32)]

perturb = [[-0.5, 0.5], [-2, -0.2],
           [-0.2, 0.2], [-0.6, 0.4],
           [-0.02, 0.02], [-0.2, 0.3],
           [-0.03, 0.02], [0, 0.48],
           [-0.4, 0.24], [-0.65, 0.4]]

n_task = 2
param = initparamobj.create_param(n_task, w, b)
cnn = CnnCifar10(param[0], 128)
test_cnn = CnnCifar10(param[0], 10000)
generate_data = CIFARInput()
max_steps = 3000
param, fitness = runga.run_ga_nn(n_task=n_task,
                                 max_steps=max_steps,
                                 is_grad_des=True,
                                 cnn=cnn,
                                 generate_data=generate_data,
                                 param=param,
                                 ga_step_decay=ga_step_decay,
                                 test_cnn=test_cnn,
                                 is_equal_test=False,
                                 selection_way='sorting_selection',
                                 elitism=1,
                                 crossover_way='one_point_crossover',
                                 pc=0.6,
                                 mutation_way='simple_mutation',
                                 perturb=perturb,
                                 pm=0.1,
                                 pw=0.8,
                                 is_replace=True)

saveparameters.save_parameters(param)

'''
print('testing the precision of populations...')

    (1)将进化完的全部个体分别在整个测试集进行测试，求出平均准确率和最高准确率 
    res = []
    for i in range(n_task):
        test_cnn.run_update_w(param[i].w)
        test_cnn.run_update_b(param[i].b)
        true_num = np.sum(test_cnn.run_top_k_op(final_image, final_labels))
        true_prob = true_num / 10000
        print('classifier_id: %d, precision: %0.3f' % (i, true_prob))
        res.append(true_prob)
    print('Mean precision: %0.3f, Max precision: %0.3f' % (np.mean(res), np.max(res)))

    (2)用全部测试集测试，对每一个数据，全部个体同时进行判断，以赞同数最多的答案为最终答案
    vote_res = []
    for i in range(n_task):
        test_cnn.run_update_w(param[i].w)
        test_cnn.run_update_b(param[i].b)
        prob = test_cnn.run_logits(final_image, final_labels)
        vote = np.argmax(prob, axis=1)
        vote_res.append(vote)
    vote_res = np.array(vote_res).T
    labels_res = []
    for i in range(10000):
        labels_res.append(np.argmax(np.bincount(vote_res[i])))
    accuracy = np.sum(np.where(labels_res == final_labels, 1, 0)) / 10000
    print('vote_accuracy: %.3f' % accuracy)

'''







