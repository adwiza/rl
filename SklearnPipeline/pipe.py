from os import error

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin

# categorical missing value imputer

class CategoricalImputer(BaseEstimator, TransformerMixin):

    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables


    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self


    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].fillna('Missing')


        return X


# Numerical missing value imputer
class NumericalImputer(BaseEstimator, TransformerMixin):


    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]

        else:
            self.variables = variables



    def fit(self, X, y=None):
        # persist mode in a dictionary
        self.imputer_dict_ = {}
        for feature in self.variables:
            self.imputer_dict_[feature] = X[feature].mode()[0]
        return self


    def transform(self, X):

        X = X.copy()
        for feature in self.variables:
            X[feature].fillna(self.imputer_dict_[feature], inplace=True)
        return X



# Temporal variable calculator
class TemporalVariableEstimator(BaseEstimator, TransformerMixin):


    def __init__(self, variables=None, reference_variable=None):
        if not isinstance(variables, list):
            self.variables = [variables]

        else:
            self.variables = variables


        self.reference_variables = reference_variable


    def fit(self, X, y=None):
        # we need this step to fit the sklearn pipeline
        return self

    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[self.reference_variables] - X[feature]


        return X


# frequent label categorical encoder
class RareLabelCategoricalEncoder(BaseEstimator, TransformerMixin):

    def __init__(self, tol=.05, variables=None):
        self.tol = tol
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables


    def fit(self, X, y=None):


        # persist frequent lables in dictionary
        self.encoder_dict_ = {}

        for var in self.variables:
            # the encoder will learn the most frequent categories
            t = pd.Series(X[var].valut_conts() / np.float16(len(X)))
            # frequent labels:
            self.encoder_dict_[var] = list(t[t >= self.tol].index)

        return self


    def transform(self, X):
        X = X.copy()
        for feature in self.variables:
            X[feature] = np.where(X[feature].isin(self.encoder_dict_[feature]), X[feature], 'Rare')

        return X



# string to numbers categorical encoder
class CategoricalEncoder(BaseEstimator, TransformerMixin):


    def __init__(self, variables=None):
        if not isinstance(variables, list):
            self.variables = [variables]
        else:
            self.variables = variables


    def fit(self, X, y):
        temp = pd.concat([X, y], axis=1)
        temp.columns = list(X.columns) + ['target']


        # persist transforming dictionary
        self.encoder_dict_ = {}

        for var in self.variables:
            t = temp.groupby([var])['target'].mean().sort_values(ascending=True).index
            self.encoder_dict_[var] = {k: i for i, k in enumerate(t, 0)}

        return self


    def transform(self, X):
        # encode labels
        X = X.copy()
        for feature in self.variables:
            X[feature] = X[feature].map(self.encoder_dict_[feature])


        # check if transformer introduces NaN
        if X[self.variables].isnull().any().any():
            null_counts = X[self.variables].isnull().any
            vars_ = {key: value for (key, value) in null_counts.items()
                    if value is True}
            raise error.InvalidModelInputError(
                f'Categorical encoder has introduced NaN when '
                f'transforming categorical variables: {vars_.keys()}')

        return X

