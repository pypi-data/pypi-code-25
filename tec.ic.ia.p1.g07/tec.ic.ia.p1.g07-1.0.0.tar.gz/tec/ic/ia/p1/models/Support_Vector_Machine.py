from tec.ic.ia.p1.models.Model import Model
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import GridSearchCV


class SupportVectorMachine(Model):
    def __init__(self, samples_train, samples_test, prefix, C, kernel):
        super().__init__(samples_train, samples_test, prefix)
        self.C = C
        self.kernel = kernel

    def execute(self):
        scaler = StandardScaler()
        samples_train = self.samples_train[0]
        samples_train = scaler.fit_transform(samples_train)
        samples_test = self.samples_test[0]
        samples_test = scaler.fit_transform(samples_test)

        # Create the SVC model object
        svc = svm.SVC(kernel=self.kernel, C=self.C,
                      decision_function_shape='ovr')
        svc.fit(samples_train, self.samples_train[1])

        print("Optimization Finished!")

        predicted_train = svc.predict(samples_train)
        predicted_test = svc.predict(samples_test)

        # Print the results of training
        print("\nResults:")
        print("Loss on Training set:", mean_squared_error(
            self.samples_train[1], predicted_train))
        print("Loss on Test set:", mean_squared_error(
            self.samples_test[1], predicted_test))
        print("Accuracy on Training set:", accuracy_score(
            self.samples_train[1], predicted_train))
        print("Accuracy on Test set:", accuracy_score(
            self.samples_test[1], predicted_test))

        return(predicted_train.tolist() + predicted_test.tolist())
