import os
import numpy as np
import pandas as pd
from pickle import load
from .constants import (DATA_PATH, MODEL_PATH, MODEL_WEIGHT_PATH, MODEL_SCALER_PATH, 
                        ranking, fluorescence)

import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures, OneHotEncoder


def prepare_input(df):
    """
        Input:
            df: pandas dataframe
        Output:
            x_num: (numpy array) numerical input features
    """
    # split measurements
    measurements = df['measurements'].str.replace(' mm', '').str.split(' x ', expand=True)
    measurements = measurements.apply(pd.to_numeric)
    measurements.columns = ['length', 'width', 'height']
    df = df.join(measurements)
    
    # ordinal encoding (can't use pd.Categorical, in case missing certain categories)
    for key, value in ranking.items():
        value_map = {k: v for v, k in enumerate(value)}
        df['ord_{}'.format(key)] = df[key].map(value_map)
    
    # add categorical features 
    # onehot encoding Fluorescence (no straightforward ordering)
    enc = OneHotEncoder(categories=[fluorescence], sparse=False)
    x_fluors = enc.fit_transform(df['fluorescence'].values.reshape(-1, 1))
    
    x_visual = df['hasVisualization'].astype(int).values.reshape(-1, 1)
    
    # select columns used in model
    cols_num = ['carat', 'depth', 'lxwRatio', 'table', 'sellingIndex', 'length', 'width', 'height']
    cols_ord = ['ord_{}'.format(key) for key in ranking.keys()]
    
    # polynomials (degree 2) for numerical+ordinal turn out to be useful
    poly_features = PolynomialFeatures(degree=2, include_bias=False)
    x_poly = poly_features.fit_transform(df[cols_num + cols_ord].values)
    
    # apply MinMax scale to only numerical+ordinal features
    scaler = load(open(MODEL_SCALER_PATH, 'rb'))
    
    # transform x
    x_minmax = scaler.transform(x_poly)
    
    x = np.hstack((x_minmax, x_fluors, x_visual))
    x = x.astype("float32")
    
    return x

def predict(x):
    # preprocess data
    x_process = prepare_input(x)
    # load the model
    model = tf.keras.models.load_model(MODEL_PATH)
    model.load_weights(MODEL_WEIGHT_PATH)
    return model.predict(x_process).flatten()