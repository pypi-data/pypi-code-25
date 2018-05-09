import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim

from rec_rnn_a3c.src.supervised_rnn import length
from rec_rnn_a3c.src.util import normalized_columns_initializer


class LightA3CNetwork(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            # Actor #
            self.env_state_input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            with tf.device("/cpu:0"):
                env_state_embedding = tf.get_variable(name="state_embedding", shape=[self.item_dim, self.hidden_dim])
                env_state_embedded = tf.nn.embedding_lookup(params=env_state_embedding, ids=self.env_state_input)

            self.keep_prob = tf.placeholder_with_default(0.5, shape=[], name='keep_prob')

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=self.keep_prob)

            self.length = length(self.env_state_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=env_state_embedded,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=rnn_cell.zero_state(self.batch_dim, dtype=tf.float32),
                sequence_length=self.length
            )
            self.output_shape = output_shape = tf.shape(rnn_output)

            self.user_embedding = tf.get_variable("user_embedding", [self.hidden_dim], dtype=tf.float32)

            rnn_output += self.user_embedding

            # Probability distribution on the candidate actions a for s #

            self.w = tf.get_variable("w", [self.item_dim, self.hidden_dim], dtype=tf.float32)
            self.b = tf.get_variable("b", [self.item_dim], dtype=tf.float32)

            self.policy_log_prob_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.w, transpose_b=True)
            self.policy_log_prob_output = tf.nn.bias_add(self.policy_log_prob_output, self.b)
            self.policy_log_prob_output = tf.reshape(self.policy_log_prob_output, [output_shape[0], output_shape[1], self.item_dim])
            self.policy_prob_output = tf.nn.softmax(self.policy_log_prob_output)

            # Expected reward of the current state s #
            self.value_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=1,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(1.0),
                biases_initializer=None
            )

            # Critic #
            self.teacher_estimation = tf.placeholder(tf.float32, [None, None, None], name='teacher_estimation')
            self.sv_target = tf.placeholder(tf.int32, [self.batch_dim, None], name='target')
            shape = tf.shape(self.sv_target)

            with tf.device("/cpu:0"):
                self.teacher_loss = tf.nn.softmax_cross_entropy_with_logits(
                    labels=self.teacher_estimation,
                    logits=self.policy_log_prob_output
                )
            self.teacher_loss = tf.reduce_mean(self.teacher_loss, axis=0)
            self.teacher_loss = tf.reduce_sum(self.teacher_loss)

            self.sv_loss = tf.contrib.seq2seq.sequence_loss(
                logits=self.policy_log_prob_output,
                targets=self.sv_target,
                weights=tf.ones(shape=shape),
                average_across_timesteps=False,
                average_across_batch=True,
            )
            self.sv_loss = tf.reduce_sum(self.sv_loss)

            self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
            actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)

            self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
            self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

            #self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_prob_output, actions), axis=2)
            with tf.device("/cpu:0"):
                self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_log_prob_output, actions), axis=2)

            # Loss functions.
            value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
            self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
            self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
            self.entropy = - tf.reduce_sum(self.policy_log_prob_output * self.policy_prob_output)
            #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            self.loss = self.sv_loss + 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            #self.loss = self.teacher_loss
            #self.loss = self.sv_loss

            self.advantages_sum = tf.reduce_sum(self.advantages)

            local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)

            gradients = tf.gradients(self.loss, local_vars)
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

            self.train_op = optimizer.apply_gradients(zip(clipped_gradients, local_vars))


class A3CNetwork(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            # Actor #
            self.env_state_input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            with tf.device("/cpu:0"):
                env_state_embedding = tf.get_variable(name="state_embedding", shape=[self.item_dim, self.hidden_dim])
                env_state_embedded = tf.nn.embedding_lookup(params=env_state_embedding, ids=self.env_state_input)

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=0.5)

            c_init = np.zeros((self.batch_dim, rnn_cell.state_size.c), np.float32)  # Tuple of form (1, x), where 1 is needed to match 2D requirement of linear transformation
            h_init = np.zeros((self.batch_dim, rnn_cell.state_size.h), np.float32)
            self.rnn_zero_state = [c_init, h_init]

            self.c_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.c])
            self.h_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.h])
            state_input = tf.nn.rnn_cell.LSTMStateTuple(self.c_input, self.h_input)

            self.length = length(self.env_state_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=env_state_embedded,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=state_input,
                sequence_length=self.length
            )

            self.rnn_state_output = (rnn_c, rnn_h)

            # Probability distribution on the candidate actions a for s #
            # TODO: Check for correctness
            self.policy_log_prob_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=self.output_dim,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(0.01),
                biases_initializer=None
            )
            self.policy_prob_output = tf.nn.softmax(self.policy_log_prob_output)
            self.policy_log_prob_output = tf.nn.log_softmax(self.policy_log_prob_output)

            # Expected reward of the current state s #
            self.value_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=1,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(1.0),
                biases_initializer=None
            )

            # Critic #
            if self.scope != 'global':
                self.teacher_estimation = tf.placeholder(tf.float32, [None, None, None], name='teacher_estimation')
                self.sv_target = tf.placeholder(tf.int32, [self.batch_dim, None], name='target')
                shape = tf.shape(self.sv_target)

                self.teacher_loss = tf.nn.softmax_cross_entropy_with_logits(
                    labels=self.teacher_estimation,
                    logits=self.policy_log_prob_output
                )
                self.teacher_loss = tf.reduce_mean(self.teacher_loss, axis=0)
                self.teacher_loss = tf.reduce_sum(self.teacher_loss)

                self.sv_loss = tf.contrib.seq2seq.sequence_loss(
                    logits=self.policy_log_prob_output,
                    targets=self.sv_target,
                    weights=tf.ones(shape=shape),
                    average_across_timesteps=False,
                    average_across_batch=True,
                )
                self.sv_loss = tf.reduce_sum(self.sv_loss)

                self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
                actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)

                self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
                self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

                #self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_prob_output, actions), axis=2)
                self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_log_prob_output, actions), axis=2)

                # Loss functions.
                value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
                self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
                self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
                self.entropy = - tf.reduce_sum(self.policy_log_prob_output * self.policy_prob_output)
                #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
                self.loss = self.sv_loss + 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
                #self.loss = self.teacher_loss
                #self.loss = self.sv_loss

                self.advantages_sum = tf.reduce_sum(self.advantages)

                local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)
                global_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'global')

                gradients = tf.gradients(self.loss, local_vars)
                clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

                self.train_op = optimizer.apply_gradients(zip(clipped_gradients, global_vars))
