#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, pandas

if (sys.version_info < (3, 0)):
    print("Code optimized for Python 3")

class ML_Scores:

    def __init__(self, model_name, model, parameters="Default", training_score=None,
                 validation_score=None, description=None, other_metric=None):
        """
        _init_
        input: model_name: type str - Name you want to give to your model (unique). Ex: "Linear Reg 1.2"
               model: type str - Model name. Ex "Linear Regression"
               parameters: type str - parameters of your model, Default is "Default". Ex: "fit_intercept=False"
               training_score: type float - Training score of your model, Default is None. Ex: 98.7
               validation_score: type float - Validation score of your model, Default is None. Ex: 83.6
               description: type str - Default is None. Ex: "Train in 1min 2s and predict in 300ms"
               other_metric: type dict - Default is Non Ex: "F1_Score" : 0.9
        output: ML_Score init_object

        This function initialize our ML_Score object with a first model
        """

        # Check if all input parameters type are OK
        assert(type(model_name)==str)
        assert(type(model)==str)
        assert(type(parameters)==str)
        if training_score != None:
            assert(type(training_score)==float)
        if validation_score != None:
            assert(type(validation_score)==float)
        if description != None:
            assert(type(description)==str)
        if other_metric != None:
            assert(type(other_metric)==dict)
            self.new_columns = []
            self.dic_columns = {"Model_Name": [model_name], "Model": [model], "Parameters": [parameters],
                                "Training_Score": [training_score], "Validation_Score": [validation_score],
                                "Description": [description]}
            # Create Pandas DataFrame attribute where we will store our models features
            for key, value in other_metric.items():
                self.new_columns.append(key)
                self.dic_columns[key] = value
            self.df_models = pandas.DataFrame(self.dic_columns)
        else:
            self.df_models = pandas.DataFrame(self.dic_columns)


    def add(self, model_name, model, parameters="Default", training_score=None,
                 validation_score=None, description=None, other_metric=None):
        """
        add
        input: ML_Scores init object parameters
        output: None

        This function add to your dataframe a new model with its new features
        """

        # Check if model name is unique
        list_models = self.df_models["Model_Name"].ravel()
        if model_name in list_models:
            print("Cannot add this model name - already exists")
            return 0

        # Check if types are OK
        assert(type(model_name)==str)
        assert(type(model)==str)
        assert(type(parameters)==str)
        if training_score != None:
            assert(type(training_score)==float)
        if validation_score != None:
            assert(type(validation_score)==float)
        if description != None:
            assert(type(description)==str)
        if other_metric != None:
            assert(type(other_metric)==dict)
            new_row = {"Model_Name": model_name, "Model": model, "Parameters": parameters,
                       "Training_Score": training_score, "Validation_Score": validation_score,
                       "Description": description}
            for key, value in other_metric.items():
                new_row[key] = value

        else:
            new_row = {"Model_Name": model_name, "Model": model, "Parameters": parameters,
                       "Training_Score": training_score, "Validation_Score": validation_score,
                       "Description": description}
            self.df_models = self.df_models.append(new_row, ignore_index=True)

    def remove(self, model):
        """
        remove
        input: model: type str - model name you want to remove
        output: None

        This function remove the row of a specific model name you want to remove in your storage models features
        """
        self.df_models = self.df_models[self.df_models.Model_Name != model]


    def set_parameters(self, model, parameter):
        """
        set_parameters
        input: model: type str - model where you want to modify the parameters
               parameter: type str - new parameter
        output: None

        This function set the parameter of the model name you specified
        """
        assert(type(parameter)==str)
        self.df_models.loc[self.df_models.Model_Name == model, 'Parameters'] = parameter

    def set_train(self, model, train):
        """
        set_parameters
        input: model: type str - model where you want to modify the parameters
               train: type float - new trainning score
        output: None

        This function set the trainning score of the model name you specified
        """
        assert(type(train)==float)
        self.df_models.loc[self.df_models.Model_Name == model, 'Training_Score'] = train

    def set_validation(self, model, validation):
        """
        set_parameters
        input: model: type str - model where you want to modify the parameters
               validation: type float - new validation score
        output: None

        This function set the validation score of the model name you specified
        """
        assert(type(validation)==float)
        self.df_models.loc[self.df_models.Model_Name == model, 'Validation_Score'] = validation

    def set_description(self, model, description):
        """
        set_parameters
        input: model: type str - model where you want to modify the parameters
               description: type str - new description
        output: None

        This function set the description of the model name you specified
        """
        assert(type(description)==str)
        self.df_models.loc[self.df_models.Model_Name == model, 'Description'] = description

    def set_other(self, model, metric_name, value):
        """
        set_parameters
        input: model: type str - model where you want to modify the parameters
               description: type str - new description
        output: None

        This function set the description of the model name you specified
        """
        assert(type(metric_name)==str)
        self.df_models.loc[self.df_models.Model_Name == model, metric_name] = value

    def get_storage(self):
        """
        get_storage
        input: None
        output: type pd.DataFrame - dataframe object where your models features are stored

        This function return the dataframe object where your models features are stored
        """

        columns = ["Model", "Parameters", "Training_Score", "Validation_Score", "Description"]
        columns.extend(self.new_columns)
        return self.df_models.set_index("Model_Name")[columns]


if __name__ == '__main__':
    my_scores = ML_Scores("Logistic_Regression_default", "Logistique Regression", other_metric={"F1_Score": 2})
    my_scores.add("Neural Net 2 CNN", "Neural Net", parameters="2 hidden")
    my_scores.remove("Logistic_Regression_default")
    my_scores.set_parameters("Neural Net 2 CNN", "3 hidden layers")
    my_scores.set_other("Neural Net 2 CNN", "F1_Score", 3)
    my_scores.get_storage()
