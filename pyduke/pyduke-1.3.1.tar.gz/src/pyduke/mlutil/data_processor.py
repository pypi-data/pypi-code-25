import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from functional import seq
import pyduke.common.data_util as du
import pyduke.common.core_util as cu

def main ():
    df_ipl = {
       'Team'  : ['Riders', 'Riders', 'Devils', 'Devils', 'Kings', 'Kings', 'Kings', 'Kings', 'Riders', 'Royals', 'Royals', 'Riders'],
       'Rank'  : [1, 2, 5, 3, 2, 4, 1, 5, 2, 4, 1, 2],
       'Year'  : [2014, 2015, 2014, 2015, 2014, 2015, 2016, 2017, 2016, 2014, 2015, 2017],
       'Points': [876, 789, 863, 673, 741, 812, 756, 788, 694, 701, 804, 690],
       'Short' : ['KKR', 'KKR', 'DDD', 'DDD', 'CSK', 'CSK', 'CSK', 'CSK', 'KKR', 'RCB', 'RCB', 'KKR' ],
       'City'  : ['Kolkata', 'Kolkata', 'Delhi', 'Delhi', 'Chennai', 'Chennai', 'Chennai', 'Chennai', 'Kolkata', 'Bangalore', 'Bangalore', 'Kolkata']
    }
    df = pd.DataFrame(df_ipl)
    df.info()

class AddColumn (BaseEstimator,TransformerMixin):
    '''
    Add new column(s) by invoking corresponding handler(s).
    
    - A map of new column names to handler (function name or lambda) is provided.
    - For each column, the corresponding handler for the column is invoked.
    - The handler is expected to accept a panda DataFrame object and return a panda Series object
    - The Series returned by the handler shall result in a new column
    
    Parameters
    ----------
    map_new_column_to_handler : map of new column name (string) to handler (function name), required
    '''
    def __init__ (self, map_new_column_to_handler):
        self.map_new_column_to_handler = {} if (map_new_column_to_handler is None) else map_new_column_to_handler
        
    def fit (self, X):
        du.assert_type_as_dataframe (X)
        return self
    
    def transform (self, X):
        for new_column, handler in self.map_new_column_to_handler.items():
            X[new_column] = handler(X)
        return X  

class RemoveColumn (BaseEstimator,TransformerMixin):       
    ''' Remove list of column '''
    
    def __init__(self, column):
        self.column = column
        
    def fit(self, X):
        du.assert_column_exists(X, self.column)
        return self
    
    def transform(self, X):
        seq(self.column).for_each(lambda c: X.pop(c))
        return X   
  

class IndependentColumnImputer(BaseEstimator,TransformerMixin):
    '''
    Each column is considered independent. The empty cells (NaN) of each column is replaced with the 
    chosen statistical strategy (mean, median or mode). 
    
    For example, If 'A' is a column name and it is present in a list passed to column_mean argument, 
    then empty cells in 'A' will be replaced by A.mean()    
    
    Parameters
    ----------
    
    column_mean : list of string (column name), optional, default=None
        Empty values (NaN) in the column is replaced by the mean (average) of the column.

    column_median : list of string (column name), optional, default=None
        Empty values (NaN) in the column is replaced by the median (middle element) of the column.

    column_mode : list of string (column name), optional, default=None
        Empty values (NaN) in the column is replaced by the mode (most repeated element) of the column.
    '''
    
    def __init__(self, column_mean=None, column_mode=None, column_median=None, column_rm=None):
        self.map_strategy_to_columns = {}
        if column_mean   is not None: self.map_strategy_to_columns['mean']   = cu.to_list(column_mean)
        if column_median is not None: self.map_strategy_to_columns['median'] = cu.to_list(column_median)
        if column_mode   is not None: self.map_strategy_to_columns['mode']   = cu.to_list(column_mode)
        
    def fit(self, X):
        du.assert_type_as_dataframe (X)
        self.result = pd.Series()  
        
        # k = Strategy name
        # v = List of column names to apply the strategy
        for k,v in self.map_strategy_to_columns.items():
            du.assert_column_exists(X, v)
            if (k == 'mean'):   self.result = self.result.append(X[v].mean())
            if (k == 'median'): self.result = self.result.append(X[v].median())
            if (k == 'mode'):   self.result = self.result.append(X[v].mode().iloc[0])
        return self           
        
    def transform(self, X):
        X = X.fillna(self.result)
        return X
    
        
class DependentColumnImputer(BaseEstimator,TransformerMixin):  
    '''
    An imputer to be used when empty cells (NaN) of a column are to be derived from other column(s)
    
    `Note:` DependentColumnImputer performs column wise opearations.
    
    - A map of column names to handler (function name or lambda) is provided.
    - For each column, the corresponding handler for the column is invoked.
    - The handler is expected to accept a panda DataFrame object and return a panda Series object
    - The Series returned by the handler shall be used to replace only the NaN in corresponding column
    
    Parameters
    ----------
    
    map_column_to_handler : dict of string to function, required
        A map (dict) of string representing the column name to a function (handler, could be lambda) that 
        perfoms the computation. See example below.        
    
    Example
    -------
        Let 'A' and 'B' be two column names of a DataFrame ``f``. 
        Fill empty cells in 'A' with twice the value of 'B'
        
        >>> imputer = ImputeDependentColumn({'A': lambda f: f['B']*2 })
        >>> imputer.fit_transform(X)
        
    '''

    def __init__ (self, map_column_to_handler):
        # A map of column name to a handler (A lambda function can be used as handler)
        # The handler calculates how the current column values (when NaN) are derived from other columns 
        self.map_column_to_handler = {} if (map_column_to_handler is None) else map_column_to_handler
        
    def fit (self, X):
        du.assert_type_as_dataframe (X)
        return self
    
    def transform (self, X):
        for column, handler in self.map_column_to_handler.items():
            X[column] = np.where(pd.isnull(X[column]), handler(X), X[column])
        return X

class Mapper(BaseEstimator,TransformerMixin):
    ''' 
    Process each cell of given columns with corresponding handler and create/replace the cell value with the one
    returned by the handler.
    
    - A map of column names to handler (function name or lambda) is provided.
    - For each cell of the column, the corresponding handler for the column is invoked.     
    - The handler is expected to accept a value and return a value. 
    - The handler is invoked by passing each cell value.
    - If map_column_to_new is None
        - The value returned by the handler shall replace the current cell value.
    - Else
        - The value returned by the handler shall create a new cell value, in the new column    
    
    Parameters
    ----------
    map_column_to_handler : dict of string to function, required    
        A map of column name to the corresponding handler (function/lambda).
        The handler should accept a value, process and return another.
        
    map_column_to_new : dict of string (column name) to string (new column name), optional, default=None
        For each column on which the Mapper is applied, the result is stored in a new column instead of 
        being overwritten.
        
    remove_original : boolean, optional, default=False
        If True, the original column shall be removed.
    '''
    def __init__ (self, map_column_to_handler, map_column_to_new=None, remove_original=False):
        self.map_column_to_handler = {} if (map_column_to_handler is None) else map_column_to_handler
        self.map_column_to_new     = {} if (map_column_to_new is None)     else map_column_to_new
        self.remove_original       = remove_original
        
    def fit (self, X):
        du.assert_type_as_dataframe (X)
        return self
        
    def transform (self, X):
        for column, handler in self.map_column_to_handler.items():
            new_column = self.map_column_to_new.get(column)
            if new_column is None: new_column = column
            X[new_column]  = X[column].apply(handler)
            if self.remove_original : X.pop(column)
        return X      

class StringToCategoryConverter(BaseEstimator,TransformerMixin):
    '''
    Convert string columns to category columns.
    
    Parameters
    ----------
    
    column : list of string (column name), required
        List of column names that shall be converted to category
        
    '''
        
    def __init__(self, column, category_of_empty='NULL'):
        self.category_of_empty = category_of_empty
        self.column = column
        self.map_column_to_category = {}
        self.set_null = {'', 'n/a', 'null', 'none'}
        
    def fit (self, X): 
        du.assert_type_as_dataframe (X)
        # Filter out columns that are already a category
        self.column = seq(self.column).filter(lambda c: X[c].dtype.name != 'category').to_list()
        
        for c in self.column:
            # Convert all the values indicating empty to NULL (self.category_of_empty)
            X[c] = seq(X[c]).map(lambda x: self.category_of_empty if x is np.nan or x is None or x.lower() in self.set_null else x).to_list()
            self.map_column_to_category[c] = pd.Categorical(X[c].str.upper()).categories
        return self
        
    def transform (self, X):
        for c in self.column:
            X[c] = pd.Categorical(X[c].str.upper(), self.map_column_to_category[c])
        return X            
                    

class RangeToCategoryConverter(BaseEstimator,TransformerMixin):
    '''
    Convert numerical columns into categories.
    
    Classify a numerical column into several ranges (Eg: 1-12, 13-19). 
    Associate each range with a category label (Eg: child=1-12, teen=13-19).    
    A number, based on the range, is assigned a corresponding category label. Thus a numerical column
    gets converted to a categorical column.
    
    Parameters
    ----------    
    map_column_to_range : A map (dict) of column name (string) to tuple of size two having the following:
        1. List of numbers denoting range of values
        2. List of labels denoting the category label for the corresponding range
        
        >>> map_column_to_range={ 
                'Age'    : ([1, 12, 19]      , ['CHILD', 'TEEN']),
                'Height' : ([1, 4.5, 6.5, 12], ['SHORT', 'AVG', 'TALL']) 
            }
    '''
    def __init__(self, map_column_to_range):
        self.map_column_to_range = {} if (map_column_to_range is None) else map_column_to_range
        
    def fit (self, X):
        du.assert_column_exists(X, self.map_column_to_range.keys())
        return self
        
    def transform (self, X):
        for c in self.map_column_to_range.keys():
            list_range, list_label = self.map_column_to_range[c]
            X[c] = pd.cut(X[c], bins=list_range, labels=list_label)
        return X
    
class CategoryToWeightEncoder(BaseEstimator,TransformerMixin):
    '''
    Encode category with corresponding weights. 
    
    Typical workflow is as follows:
     - A string column with a finite possible values is cleaned and converted to category. 
     - A category is more helpful in visualizing and analyzing the behavior of the column.
     - Based on the analysis, suitable weights can be associated to each category.
     - Since algorithms work with numbers and not categories, an encoder can be used to encode 
       categories with weights (CategoryToWeightEncoder)
       
    Parameters
    ----------
    map_column_category_weight : A map (dict) of column name to map (dict) where category name (string) is mapped to weight (number). 
        Example: 
        >>> map_column_category_weight = { 
                'Team' : { 'DEVILS':1, 'RIDERS':2, 'KINGS':3, 'RIDERS':4, 'ROYALS':5 },
                'City' : { 'BANGALORE':10, 'DELHI':6, 'KOLKATA':8, 'CHENNAI':9 }
            }
    '''    
    
    def __init__(self, map_column_category_weight):
        self.map_column_category_weight = map_column_category_weight

    def fit (self, X):
        for column, map_weight in self.map_column_category_weight.items():
            du.validate_series_category_with_input (X[column], map_weight.keys())
        return self
        
    def transform (self, X):
        for column, map_weight in self.map_column_category_weight.items():
            X[column] = X[column].map(map_weight)
        return X

class CategoryToOneHotEncoder(BaseEstimator,TransformerMixin):
    '''
    Convert the ``column`` to one-hot encoded format. Thus adding more features.
    
    Parameters
    ----------
    column : list of string (column name), required
        A list of column names to be one hot encoded
        
    drop_first : boolean, optional, default=True
        If true one of the features (column) after one-hot encoding is dropped.
        
    '''
    
    def __init__(self, column, drop_first=True):
        self.column = column
        self.drop_first = drop_first
        
    def fit (self, X):
        seq(self.column).for_each(lambda c: du.assert_column_type_as_category(X, [c]))
        return self
    
    def transform (self, X):
        X = pd.get_dummies(X, columns=self.column, drop_first=self.drop_first)
        return X
    
class Scaler (BaseEstimator,TransformerMixin):  
    '''
    Scale column(s) using a scaler of type specified by ``scaler_type``
    '''

    ##
    # Supported set of scaler types
    ##    
    set_type = {'standard', 'min-max'}
    
    def __init__ (self, column=None, scaler_type='standard'):
        self.column = column
        self.scaler_type = scaler_type
        self.scaler = StandardScaler () if type == 'standard' else MinMaxScaler()
    
    def fit(self, X):
        du.assert_type_as_dataframe (X)
        if self.column is None: self.column = list(X.columns)
        self.scaler.fit(X[self.column])
        return self
        
    def transform(self, X):
        X[self.column] = pd.DataFrame(self.scaler.transform(X[self.column]), columns=self.column)
        return X

if __name__ == '__main__':
    main()        

