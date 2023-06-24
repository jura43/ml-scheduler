import joblib
import pandas as pd

def data_normalization(data):
    """
    Accepts dictionary with values nessesary to make prediction

    Returns normalized data to be used for making predicions
    """
    df = pd.DataFrame.from_dict(data)
    ct = joblib.load('ct.save')
    return ct.transform(df)