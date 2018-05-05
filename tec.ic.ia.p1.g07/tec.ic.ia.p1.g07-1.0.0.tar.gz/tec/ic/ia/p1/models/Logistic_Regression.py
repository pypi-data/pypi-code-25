from tec.ic.ia.p1.models.Model import Model
import tensorflow as tf
import numpy as np


class LogisticRegression(Model):
    def __init__(self, samples_train, samples_test, prefix, regularization):
        super().__init__(samples_train, samples_test, prefix)
        self.regularization = regularization
        # HyperParameters
        self.learning_rate = 0.01
        self.training_epochs = 5000
        self.batch_size = 1000
        self.display_step = 5
        self.lambd = 0.01

    def execute(self):
        # Define the dimensions of the model
        dim_input = self.samples_train[0].shape[1]
        dim_output = self.samples_train[1].shape[1]

        # Declare inputs and outputs
        with tf.name_scope("Declaring_placeholder"):
            X = tf.placeholder(tf.float32, [None, dim_input])
            y = tf.placeholder(tf.float32, [None, dim_output])

        # Declaring variables to train
        with tf.name_scope("Declaring_variables"):
            W = tf.Variable(tf.zeros([dim_input, dim_output]))
            b = tf.Variable(tf.zeros([dim_output]))
            tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES, W)

        # Declaring the function of the linear model
        with tf.name_scope("Declaring_functions"):
            y_techo = tf.nn.softmax(tf.add(tf.matmul(X, W), b))

        # Declaring the cost, it depends if receives l1 or l2 flag
        with tf.name_scope("Calculating_Loss"):
            # Original loss function
            loss = tf.reduce_mean(
                tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=y_techo))
            # Regularization
            regularizer = None
            if self.regularization == "l1":
                regularizer = tf.contrib.layers.l1_regularizer(scale=self.lambd)
            elif self.regularization == "l2":
                regularizer = tf.contrib.layers.l2_regularizer(scale=self.lambd)
            reg_variables = tf.get_collection(
                tf.GraphKeys.REGULARIZATION_LOSSES)
            regularization_penalty = tf.contrib.layers.apply_regularization(
                regularizer, reg_variables)
            regularized_loss = tf.reduce_mean(loss + regularization_penalty)

        # Declaring the optimizer of the model
        with tf.name_scope("Declaring_Optimizer"):
            optimizer = tf.train.GradientDescentOptimizer(
                learning_rate=self.learning_rate).minimize(regularized_loss)

        # Training the model
        output_prediction = []
        with tf.name_scope("Training"):
            with tf.Session() as sess:
                # Initialize variables
                sess.run(tf.global_variables_initializer())
                l = 0
                # Train
                for epoch in range(self.training_epochs):
                    _, l = sess.run([optimizer, regularized_loss], feed_dict={
                                    X: self.samples_train[0], y: self.samples_train[1]})
                print("Optimization Finished!")

                print("\nResults:")

                # Calculate Loss
                print("Loss on Training set:", l)
                l = sess.run(regularized_loss, feed_dict={
                             X: self.samples_test[0], y: self.samples_test[1]})
                print("Loss on Test set:", l)

                # Accuracy
                correct_prediction = tf.equal(
                    tf.argmax(y_techo, 1), tf.argmax(y, 1))
                # Calculate accuracy for test examples
                accuracy = tf.reduce_mean(
                    tf.cast(correct_prediction, tf.float32))
                print("Accuracy on Training set:", accuracy.eval(
                    {X: self.samples_train[0], y: self.samples_train[1]}))
                print("Accuracy on Test set:", accuracy.eval(
                    {X: self.samples_test[0], y: self.samples_test[1]}))

                # Returns the samples for store them in a csv
                pred_train = self.samples_train[0].dot(sess.run(W))+sess.run(b)
                pred_test = self.samples_test[0].dot(sess.run(W))+sess.run(b)
                return (np.argmax(pred_train, axis=1).tolist() + np.argmax(pred_test, axis=1).tolist())
