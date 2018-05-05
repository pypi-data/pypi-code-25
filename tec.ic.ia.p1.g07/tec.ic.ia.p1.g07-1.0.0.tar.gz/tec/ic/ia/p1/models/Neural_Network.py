from tec.ic.ia.p1.models.Model import Model
from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers
import ast
import numpy as np
from keras.callbacks import History


class NeuralNetwork(Model):
    def __init__(self, samples_train, samples_test, prefix, layers, units_per_layer, activation_function):
        super().__init__(samples_train, samples_test, prefix)
        self.layers = layers
        self.units_per_layer = ast.literal_eval(units_per_layer)
        self.activation_function = activation_function
        # HyperParameters
        self.training_epochs = 3000
        self.batch_size = 500
        self.learning_rate = 0.01

    def execute(self):
        # Defining the dimensions of the problem
        dim_input = self.samples_train[0].shape[1]
        dim_output = self.samples_train[1].shape[1]

        # Create the model
        model = Sequential()

        # Add layers
        model.add(Dense(dim_input, input_dim=dim_input,
                        kernel_initializer="uniform", activation='relu'))
        for i in range(self.layers):
            model.add(Dense(
                self.units_per_layer[i], kernel_initializer="uniform", activation=self.activation_function))
        model.add(
            Dense(dim_output, kernel_initializer="uniform", activation='softmax'))

        # Compile the model
        #optimizer = optimizers.Adadelta(lr=1.0, rho=0.95, epsilon=None, decay=0.0)
        optimizer = optimizers.SGD(
            lr=self.learning_rate, momentum=0.1, nesterov=True)
        model.compile(loss='categorical_crossentropy',
                      optimizer=optimizer, metrics=['accuracy'])

        # Fit the model
        history = model.fit(self.samples_train[0], self.samples_train[1], validation_data=(
            self.samples_test[0], self.samples_test[1]), epochs=self.training_epochs, batch_size=self.batch_size, verbose=0)

        print("Optimization Finished!")

        # Print the results of training
        print("\nResults:")
        print("Loss on Training set:", history.history['loss'][-1])
        print("Loss on Test set:", history.history['val_loss'][-1])
        print("Accuracy on Training set:", history.history['acc'][-1])
        print("Accuracy on Test set:", history.history['val_acc'][-1])

        # scores = model.evaluate(self.samples_test[0], self.samples_test[1])
        # print("\nAccuracy: %.2f%%" % (scores[1]*100))

        # Returns the samples for store them in a csv
        pred_train = model.predict(self.samples_train[0])
        pred_test = model.predict(self.samples_test[0])
        return (np.argmax(pred_train, axis=1).tolist() + np.argmax(pred_test, axis=1).tolist())
