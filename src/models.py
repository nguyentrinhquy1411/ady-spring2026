from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression, RidgeCV, LassoCV
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
import numpy as np

class SVRWrapper(BaseEstimator, RegressorMixin):
    """
    Wrapper for SVR with GridSearchCV for tuning.
    """
    def __init__(self, kernel='rbf', param_grid=None, cv=3):
        self.kernel = kernel
        self.param_grid = param_grid if param_grid else {
            'C': [0.1, 1, 10, 100],
            'epsilon': [0.01, 0.1, 1],
            'gamma': ['scale', 'auto', 0.1, 0.01]
        }
        self.cv = cv
        self.best_estimator_ = None
        self.best_params_ = None
        
    def fit(self, X, y):
        svr = SVR(kernel=self.kernel)
        grid_search = GridSearchCV(svr, self.param_grid, cv=self.cv, scoring='neg_mean_squared_error', n_jobs=-1)
        grid_search.fit(X, y)
        
        self.best_estimator_ = grid_search.best_estimator_
        self.best_params_ = grid_search.best_params_
        return self
    
    def predict(self, X):
        if self.best_estimator_ is None:
            raise ValueError("Model not fitted yet.")
        return self.best_estimator_.predict(X)

class RidgeBaseline(BaseEstimator, RegressorMixin):
    """
    Wrapper for Ridge Regression with CV tuning.
    """
    def __init__(self, alphas=[0.1, 1.0, 10.0]):
        self.alphas = alphas
        self.model = RidgeCV(alphas=alphas)
        
    def fit(self, X, y):
        self.model.fit(X, y)
        self.alpha_ = self.model.alpha_
        self.coef_ = self.model.coef_
        self.intercept_ = self.model.intercept_
        return self
    
    def predict(self, X):
        return self.model.predict(X)

class LassoBaseline(BaseEstimator, RegressorMixin):
    """
    Wrapper for Lasso Regression with CV tuning.
    """
    def __init__(self, alphas=[0.1, 1.0, 10.0]):
        self.alphas = alphas
        self.model = LassoCV(alphas=alphas, random_state=42)
        
    def fit(self, X, y):
        self.model.fit(X, y)
        self.alpha_ = self.model.alpha_
        self.coef_ = self.model.coef_
        self.intercept_ = self.model.intercept_
        return self
    
    def predict(self, X):
        return self.model.predict(X)

class MeanBaseline(BaseEstimator, RegressorMixin):
    """
    Baseline model that always predicts the mean of the training target.
    """
    def fit(self, X, y):
        self.mean_ = np.mean(y)
        return self
    
    def predict(self, X):
        return np.full(X.shape[0], self.mean_)

class OLSBaseline(BaseEstimator, RegressorMixin):
    """
    Wrapper for Standard OLS Linear Regression.
    """
    def __init__(self):
        self.model = LinearRegression()
        
    def fit(self, X, y):
        self.model.fit(X, y)
        self.coef_ = self.model.coef_
        self.intercept_ = self.model.intercept_
        return self
    
    def predict(self, X):
        return self.model.predict(X)
