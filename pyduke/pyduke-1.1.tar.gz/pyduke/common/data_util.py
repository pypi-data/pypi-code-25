import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_mldata
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score, mean_squared_error
import util.core_util as cu

SEED = 42
    
def load_data ():
    dataset = fetch_mldata('MNIST original', data_home=cu.PROJECT_ROOT + '/dataset')
    X, y = dataset['data'], dataset['target']
    return X, y

def get_stratified_shuffle_split (X, y, **kwargs):
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=True, stratify=y, random_state=SEED, **kwargs)
    return X_train, y_train, X_test, y_test


def get_rmse (y, y_pred, table=True):
    '''Compute the root mean squared error for numeric arrays (regression)'''
    rmse = np.sqrt (mean_squared_error(y, y_pred))
    table and print ('RMSE {:2.4f}'.format(rmse))
    return rmse

def get_accuracy (y, y_pred, table=True, title=None):
    '''Get the accuracy of the prediction'''
    accuracy   = accuracy_score  (y, y_pred)
    if (table):
        print ("")                
        print ("{} : {:2.4f}".format(cu.join(title, "Accuracy", delimiter=" - "), accuracy))
    return accuracy        
    

def get_scores (y, y_pred, table=True, title=None):
    '''
    Compute and return scores for binary arrays: Accuracy, Precision, Recall, ROC-AUC
    
    Parameters
    ----------
    y : 1d array, boolean
        Actual, labelled output
        
    y_pred : 1d array, boolean
        Predicted output
        
    table : boolean, default=True
        If True, a tabular score id displayed

    title : string, default=None
        A title to be displayed    
        
    Returns
    -------
    Tuple with (Accuracy, Precision, Recall, F1Score)        
    '''
    accuracy   = accuracy_score  (y, y_pred)
    precision  = precision_score (y, y_pred)
    recall     = recall_score    (y, y_pred)
    f1score    = f1_score        (y, y_pred)
    roc        = roc_auc_score   (y, y_pred)
    
    if (table):
        print ("")                
        print (cu.join(title, "Precision Recall Scores", delimiter=" - "))
        score = np.array([accuracy, precision, recall, f1score, roc]).reshape(1, -1)
        label = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC']
        df = pd.DataFrame(score, index=['Score'], columns=label) 
        print (df)
       
    return (accuracy, precision, recall, f1score) 


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
    
    
    
    