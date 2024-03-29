"""Pipeline utils."""

import numpy as np

def remove_highly_correlated_features(df, threshold=0.9):
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return to_drop

def remove_constant_features(df):
    return [column for column in df.columns if df[column].nunique() == 1]

def standarise_float_columns(df):
    for column in df.columns:
        if df[column].dtype == 'float64':
            df[column] = (df[column] - df[column].mean()) / df[column].std()
    return df

def normalise_int_columns(df):
    for column in df.columns:
        if df[column].dtype == 'int64':
            df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
    return df