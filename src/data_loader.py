import pandas as pd

def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

