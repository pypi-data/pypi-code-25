import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_mldata
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score, mean_squared_error
from tabulate import tabulate
import pyduke.common.core_util as cu

SEED = 42

_this_module = sys.modules[__name__]

def main ():
    get_accuracy([1, 0, 1], [1, 0, 0])
    get_rmse([1, 0, 1], [1, 0, 0])
    get_scores([1, 0, 1], [1, 0, 0])
    
# -------------------------------------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------------------------------------
    
    
def load_sklearn_data (dataname, project_root=None, data_home=None):
    ''' 
    Load mldata.org dataset specified by ``dataname`` 
    If ``data_home`` is ``None`` it is evaluated to be ``<project root>/dataset``
    '''
    data_home = data_home if project_root == None else project_root + '/dataset'
    dataset = fetch_mldata(dataname, data_home=data_home)
    X, y = dataset['data'], dataset['target']
    return X, y

# -------------------------------------------------------------------------------------------------
# Stats utility functions
# -------------------------------------------------------------------------------------------------

def get_stratified_shuffle_split (X, y, **kwargs):
    ''' Perform a stratified shuffle split, statified based on ``y``. See train_test_split for ``kwargs`` '''
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, stratify=y, random_state=SEED, **kwargs)
    return X_train, y_train, X_test, y_test


def get_rmse (y, y_pred, show=True):
    '''Compute the root mean squared error for numeric arrays (regression)'''
    rmse = np.sqrt (mean_squared_error(y, y_pred))
    _this_module.show(pd.DataFrame(data=[rmse], columns=['RMSE']), showindex=False)

def get_accuracy (y, y_pred, title=None, show=True):
    '''Get the accuracy of the prediction'''
    accuracy   = accuracy_score  (y, y_pred)
    if (show):
        _this_module.show(pd.DataFrame(data=[accuracy], columns=['Accuracy']), showindex=False)
    return accuracy        

def get_scores (y, y_pred, title=None, show=True):
    '''
    Compute and return scores for binary arrays: Accuracy, Precision, Recall, ROC-AUC
    
    Parameters
    ----------
    y : 1d array, boolean
        Actual, labelled output
        
    y_pred : 1d array, boolean
        Predicted output
        
    show : boolean, default=True
        If True, a tabular scores are displayed

    title : string, default=None
        A title to be prepended    
        
    Returns
    -------
    Tuple with (Accuracy, Precision, Recall, F1Score)        
    '''
    accuracy   = accuracy_score  (y, y_pred)
    precision  = precision_score (y, y_pred)
    recall     = recall_score    (y, y_pred)
    f1score    = f1_score        (y, y_pred)
    roc        = roc_auc_score   (y, y_pred)
    
    if (show):
        print ("")                
        print (cu.join(title, "Precision Recall Scores", delimiter=" - "))
        data = cu.to_2d([accuracy, precision, recall, f1score, roc])
        label = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC']
        df = pd.DataFrame(data=data, index=['Score'], columns=label) 
        _this_module.show (df)
       
    return (accuracy, precision, recall, f1score) 
   
# -------------------------------------------------------------------------------------------------
# Pandas Dataframe utility functions
# -------------------------------------------------------------------------------------------------
        
def validate_series_category_with_input (series, set_input):
    assert series.dtype.name == 'category', 'Series {} is not of type "category". TypeFound={}'.format(series.name, series.dtype.name)
    set_categories_in_series  = set(series.cat.categories)
    set_categiries_to_replace = set(set_input)
    assert set_categories_in_series.issubset(set_categiries_to_replace), 'All categories in series must have a replacement. {} not subset of {}'.format(set_categories_in_series, set_categiries_to_replace)
    
def assert_column_exists (X, list_column_name):
    ''' Assert ``X`` is a ``DataFrame`` and ``list_column_name`` has a subset of columns in ``X`` '''
    assert_type_as_dataframe (X)
    set_column_name      = set(list_column_name)
    set_all_column_name  = set(X.columns)
    assert set_column_name.issubset(set_all_column_name), 'Colum(s) not found. AllColumns={} GivenColumns={}'.format(set_all_column_name, set_column_name)
    
def assert_column_type_as_category (X, list_column_name):
    ''' Assert that all columns in ``list_column_name`` in dataframe ``X`` are of type "category" '''
    s = set(X[list_column_name].dtypes)
    assert len(s) == 1, 'All columns must be of type "category". Columns={} TypesFound={}'.format(list_column_name, s)
    assert 'category' in s, 'Columns are not of type "category", TypeFound={}'.format(s)

def assert_type_as_dataframe (X):
    assert type(X) is pd.DataFrame, 'InvalidType: Expected type "pandas.core.frame.DataFrame". Found={}'.format(type(X))    
    
def show (X, showindex=True, floatfmt='4f'):
    assert_type_as_dataframe (X)
    print(tabulate(X, headers=X.columns, tablefmt="psql", showindex=showindex, floatfmt=floatfmt))
    
# -------------------------------------------------------------------------------------------------
# Visualization
# -------------------------------------------------------------------------------------------------


def plot_precision_recall_vs_threshold (precision_list, recall_list, threshold_list, title=None):
    plt.figure()
    plt.title(cu.join(title, "Precision, Recall Vs Threshold", delimiter=" - "))
    plt.plot(threshold_list, precision_list[:-1], "b--", label="Precision")
    plt.plot(threshold_list, recall_list[:-1], "g-", label="Recall")
    plt.xlabel("Threshold")
    plt.legend(loc="upper left")
    plt.ylim([0, 1])
    plt.show()
    
def plot_roc_curve(fpr, tpr, label=None, title=None):
    plt.figure()
    plt.title(cu.join(title, "ROC Curve", delimiter=" - "))
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')  
    plt.show()
    
def plot_confusion_matrix (matrix, title=None, rank=True):
    ''' 
    Plot confusion matrix with color codes. Better to average values range from Green to yellow.
    If rank is True, lesser the value better than rank.
    
    Parameters
    ----------
    matrix : 
        A confusion matrix
        
    title : boolean, default=True
        Title of the plot
        
    rank: boolean, default=True
        If True lower rank is considered better.      
    '''
    plt.matshow(matrix, cmap='YlGn_r')
    plt.colorbar()
    plt.show()
    
  
if __name__ == '__main__':
    main()        
    
    