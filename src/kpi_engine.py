def classify_status(kpi_score):
    if kpi_score >= 85:
        return "🟢 Good"
    elif kpi_score >= 70:
        return "🟡 Warning"
    else:
        return "🔴 Critical"


def calculate_kpis(df):
    df["Expected_kWh"] = df["Rated_kW"] * df["Operating_Hours"]
    df["Deviation_kWh"] = df["Actual_kWh"] - df["Expected_kWh"]
    df["Cost_Loss_Rs"] = df["Deviation_kWh"] * df["Cost_per_kWh"]

    df["Load_Factor"] = df["Actual_kWh"] / df["Expected_kWh"]
    df["Deviation_Index"] = abs(df["Deviation_kWh"]) / df["Expected_kWh"]

    df["KPI_Score"] = (100 - (df["Deviation_Index"] * 100)).clip(0, 100)
    df["Status"] = df["KPI_Score"].apply(classify_status)

    return df
