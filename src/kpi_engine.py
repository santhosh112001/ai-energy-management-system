import numpy as np

def calculate_kpis(df):
    df["Expected_kWh"] = df["Rated_kW"] * df["Operating_Hours"]
    df["Deviation_kWh"] = df["Actual_kWh"] - df["Expected_kWh"]
    df["Cost_Loss_Rs"] = df["Deviation_kWh"] * df["Cost_per_kWh"]

    df["Load_Factor"] = df["Actual_kWh"] / df["Expected_kWh"]
    df["Deviation_Index"] = abs(df["Deviation_kWh"]) / df["Expected_kWh"]

    # KPI Score (0–100)
    df["KPI_Score"] = np.clip(
        100 - (df["Deviation_Index"] * 100), 0, 100
    )

    return df

